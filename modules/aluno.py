import streamlit as st
import database as db

def render_aluno_view(preselected_quiz_code: str = None):
    st.title("Portal do Estudante")

    tab_responder, tab_consultar = st.tabs(["📝 Responder Questionário", "🔍 Consultar Meu Resultado"])

    # =========================================================================
    # ABA 1: RESPONDER QUESTIONÁRIO
    # =========================================================================
    with tab_responder:
        # Se foi passado um código de quiz na URL
        quiz = None
        if preselected_quiz_code:
            quiz = db.get_quiz_by_code(preselected_quiz_code)
        
        if not quiz:
            st.markdown("Insira o código do quiz fornecido pelo professor ou selecione na lista:")
            col_code, col_select = st.columns([1, 1])
            
            with col_code:
                code_input = st.text_input("Digite o Código do Quiz (6 letras/números):", placeholder="Ex: A1B2C3", key="aluno_quiz_code").strip().upper()
                if code_input:
                    quiz = db.get_quiz_by_code(code_input)
                    if not quiz:
                        st.error("Nenhum quiz encontrado com este código.")
            
            if not quiz:
                with col_select:
                    active_quizzes = [q for q in db.get_all_quizzes() if q['is_active']]
                    if active_quizzes:
                        q_map = {f"{q['title']} (Código: {q['quiz_code']})": q['quiz_code'] for q in active_quizzes}
                        chosen_label = st.selectbox("Ou selecione um quiz ativo:", ["-- Selecione --"] + list(q_map.keys()), key="aluno_select_quiz")
                        if chosen_label != "-- Selecione --":
                            quiz = db.get_quiz_by_code(q_map[chosen_label])

        if not quiz:
            st.info("Aponte a câmera do seu celular para o QR Code projetado pelo professor ou insira o código acima.")
        elif not quiz['is_active']:
            st.warning(f"O questionário '{quiz['title']}' está atualmente encerrado para novas respostas pelo professor.")
        else:
            quiz_id = quiz['id']
            quiz_details = db.get_quiz_details(quiz_id)
            questions = quiz_details.get('questions', [])

            if not questions:
                st.warning("Este questionário ainda não possui perguntas cadastradas.")
            else:
                # Gerar ou recuperar PIN único de 4 dígitos da sessão do aluno
                pin_session_key = f"student_pin_assigned_{quiz_id}"
                if pin_session_key not in st.session_state:
                    st.session_state[pin_session_key] = db.generate_unique_student_pin(quiz_id)
                
                assigned_pin = st.session_state[pin_session_key]

                # Cabeçalho do Quiz
                st.info(f"### {quiz['title']}\n{quiz['description'] or ''}\n\n**Total de Questões:** {len(questions)} | **Tempo Sugerido:** {quiz['time_limit_minutes'] or 'Livre'} min")

                # Cartão de Identificação Único do Aluno (Código de 4 Dígitos)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); padding: 18px 22px; border-radius: 12px; border: 1.5px solid #6366F1; margin: 15px 0 20px 0; text-align: center;">
                    <span style="font-size: 13px; text-transform: uppercase; font-weight: 700; letter-spacing: 1.5px; color: #A5B4FC;">🎫 SEU CÓDIGO IDENTIFICADOR ÚNICO:</span>
                    <div style="font-size: 40px; font-weight: 900; color: #38BDF8; letter-spacing: 8px; margin: 6px 0; font-family: monospace;">{assigned_pin}</div>
                    <p style="margin: 0; color: #E0E7FF; font-size: 14px;">📸 <b>Anote ou tire print deste código de 4 números!</b> Você o usará para consultar sua nota após o encerramento da prova pelo professor.</p>
                </div>
                """, unsafe_allow_html=True)

                # Identificação Opcional
                student_name = st.text_input("Seu Nome (Opcional - caso queira se identificar para o professor):", placeholder="Ex: Maria Eduarda (Opcional)", key=f"name_{quiz_id}")

                st.divider()
                st.markdown("#### Questões da Prova")

                # Dicionário para armazenar as seleções do aluno
                selected_answers = {}

                for idx, q in enumerate(questions, 1):
                    diff_tag = f"({q.get('difficulty_level', 'Média')})"
                    st.markdown(f"**Questão {idx}** {diff_tag} — {q['points']} pts")
                    st.markdown(f"##### {q['question_text']}")

                    # Exibe imagem ilustrativa da questão se houver
                    if q.get('image_data'):
                        st.image(q['image_data'], caption=f"Ilustração - Questão {idx}", use_container_width=True)

                    # Mapeia as opções
                    options_dict = {f"{opt['option_text']}": opt['id'] for opt in q['options']}
                    
                    # Widget de seleção (Radio)
                    choice = st.radio(
                        f"Selecione sua resposta para a questão {idx}:",
                        options=list(options_dict.keys()),
                        index=None,
                        key=f"q_{q['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if choice:
                        selected_answers[q['id']] = options_dict[choice]

                    st.markdown("---")

                # Botão de Envio
                if st.button("Enviar Minhas Respostas", type="primary", use_container_width=True):
                    unanswered = len(questions) - len(selected_answers)
                    if unanswered > 0:
                        st.warning(f"Você ainda não respondeu {unanswered} questão(ões). Por favor, responda todas antes de enviar.")
                        st.stop()

                    # Registrar no banco de dados SQLite com cálculo seguro da TRI e o PIN único
                    with st.spinner("Gravando suas respostas com segurança..."):
                        result = db.submit_student_answers(
                            quiz_id=quiz_id,
                            student_pin=assigned_pin,
                            student_name=student_name,
                            student_identifier=f"PIN-{assigned_pin}",
                            selected_options=selected_answers
                        )

                    # Verificar se o professor já liberou as notas ou se estão sob sigilo durante a prova
                    is_released = bool(quiz.get('results_released'))
                    
                    if not is_released:
                        # =========================================================
                        # MODO SEGURO: NOTAS E RESPOSTAS OCULTAS
                        # =========================================================
                        st.success("🎉 **Suas respostas foram enviadas e registradas com sucesso!**")
                        st.markdown(f"""
                        <div style="background: #0F172A; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-top: 15px;">
                            <h3 style="color: #38BDF8; margin-top: 0;">🔒 Avaliação em Andamento</h3>
                            <p style="font-size: 16px; color: #F8FAFC;">
                                🎫 <b>Seu Código de Consulta:</b> <span style="font-size: 22px; font-weight: 800; color: #FBBF24; font-family: monospace;">{assigned_pin}</span>
                            </p>
                            <p style="color: #94A3B8; font-size: 14px; line-height: 1.6;">
                                Por critério pedagógico e para garantir o sigilo da prova enquanto a turma responde, <b>o gabarito e a sua nota TRI só serão divulgados após todos terminarem e o professor liberar os resultados</b>.
                            </p>
                            <p style="color: #A5B4FC; font-size: 14px; margin-bottom: 0;">
                                📌 <i>Guarde o código <b>{assigned_pin}</b> e consulte seu boletim na aba 'Consultar Meu Resultado' assim que o professor encerrar a prova.</i>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Se já estava liberado pelo professor
                        st.success("Suas respostas foram avaliadas!")
                        tri_score = result.get('tri_score', 500.0)
                        theta = result.get('theta', 0.0)
                        coherence_label = result.get('coherence_label', 'Coerente')
                        
                        st.markdown(f"### Sua Nota TRI: **{tri_score:.1f} pts** (Proficiência: {theta:+.2f} θ)")
                        st.info(f"Coerência: {coherence_label}")

    # =========================================================================
    # ABA 2: CONSULTAR RESULTADO / BOLETIM (VIA CÓDIGO DE 4 DÍGITOS)
    # =========================================================================
    with tab_consultar:
        st.subheader("Consultar Nota e Gabarito Liberados")
        st.markdown("Digite o seu código de **4 números** gerado ao acessar a prova para visualizar seu boletim:")
        
        all_quizzes = db.get_all_quizzes()
        if not all_quizzes:
            st.info("Nenhum questionário cadastrado no momento.")
        else:
            q_options = {f"{q['title']} (Código: {q['quiz_code']})": q for q in all_quizzes}
            selected_label_c = st.selectbox("Selecione o Questionário:", list(q_options.keys()), key="consult_quiz_select")
            selected_quiz_c = q_options[selected_label_c]
            
            search_pin_input = st.text_input("Digite o seu Código Único (4 dígitos ou Nome):", max_chars=20, placeholder="Ex: 4829", key="search_student_pin_input")
            
            if st.button("Consultar Meu Resultado", type="primary", use_container_width=True):
                if not search_pin_input.strip():
                    st.error("Por favor, digite seu código de 4 números para consultar.")
                else:
                    # Verificar se as notas já foram liberadas pelo professor
                    if not selected_quiz_c.get('results_released'):
                        st.warning("⏳ **Avaliação ainda em andamento.**")
                        st.info("O professor ainda não liberou a divulgação das notas e gabaritos deste questionário. Aguarde o encerramento da prova por toda a turma.")
                    else:
                        # Buscar submissão pelo PIN de 4 dígitos
                        sub_data = db.get_student_submission_by_credentials(selected_quiz_c['id'], search_pin_input)
                        
                        if not sub_data:
                            st.error(f"Nenhum registro de resposta encontrado para o código '{search_pin_input}' neste questionário. Verifique se digitou o código de 4 números correto.")
                        else:
                            pin_display = sub_data.get('student_pin') or search_pin_input
                            st.success(f"Boletim localizado para **{sub_data['student_name']}** (Código: `{pin_display}`)!")
                            
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.metric("Nota TRI (Escala ENEM)", f"{sub_data['tri_score']:.1f} pts")
                            with col_m2:
                                st.metric("Proficiência (θ)", f"{sub_data['theta']:+.2f} DP")
                            with col_m3:
                                st.metric("Acertos / Pontuação", f"{sub_data['score']:.1f} / {sub_data['total_points']:.1f}", f"{sub_data['percentage']:.1f}%")
                            
                            c_label = sub_data.get('coherence_label', 'Coerente')
                            if "Alta" in c_label:
                                st.success(f"🎯 **Coerência Pedagógica:** {c_label}")
                            elif "Regular" in c_label or "Coerente" in c_label:
                                st.info(f"💡 **Coerência Pedagógica:** {c_label}")
                            else:
                                st.warning(f"⚠️ **Coerência Pedagógica:** {c_label}")
                            
                            # Detalhamento do Gabarito Comentado
                            with st.expander("📝 Ver Gabarito Comentado e Explicações", expanded=True):
                                for idx, ans_item in enumerate(sub_data.get('answers', []), 1):
                                    is_hit = bool(ans_item['is_correct'])
                                    status_label = "✅ [Acertou]" if is_hit else "❌ [Errou]"
                                    diff_tag = f"({ans_item.get('difficulty_level', 'Média')})"
                                    
                                    st.markdown(f"**{status_label} Questão {idx}** {diff_tag}: {ans_item['question_text']}")
                                    if ans_item.get('image_data'):
                                        st.image(ans_item['image_data'], caption=f"Ilustração - Questão {idx}", width=300)
                                    st.markdown(f"- **Sua resposta:** {ans_item['selected_option_text'] or 'Não respondida'}")
                                    if not is_hit:
                                        st.markdown(f"- **Resposta correta:** {ans_item['correct_option_text']}")
                                    if ans_item.get('explanation'):
                                        st.caption(f"**Explicação Pedagógica:** {ans_item['explanation']}")
                                    st.divider()


