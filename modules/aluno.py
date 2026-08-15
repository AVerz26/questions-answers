import streamlit as st
import database as db

def render_aluno_view(preselected_quiz_code: str = None):
    st.title("Portal do Aluno - Responder Questionário")

    # Se foi passado um código de quiz na URL
    quiz = None
    if preselected_quiz_code:
        quiz = db.get_quiz_by_code(preselected_quiz_code)
    
    if not quiz:
        st.markdown("Insira o código fornecido pelo professor ou selecione na lista:")
        col_code, col_select = st.columns([1, 1])
        
        with col_code:
            code_input = st.text_input("Digite o Código do Quiz (6 letras/números):", placeholder="Ex: A1B2C3").strip().upper()
            if code_input:
                quiz = db.get_quiz_by_code(code_input)
                if not quiz:
                    st.error("Nenhum quiz encontrado com este código.")
        
        if not quiz:
            with col_select:
                active_quizzes = [q for q in db.get_all_quizzes() if q['is_active']]
                if active_quizzes:
                    q_map = {f"{q['title']} (Código: {q['quiz_code']})": q['quiz_code'] for q in active_quizzes}
                    chosen_label = st.selectbox("Ou selecione um quiz ativo:", ["-- Selecione --"] + list(q_map.keys()))
                    if chosen_label != "-- Selecione --":
                        quiz = db.get_quiz_by_code(q_map[chosen_label])

    if not quiz:
        st.info("Aponte a câmera do celular para o QR Code projetado pelo professor ou insira o código acima.")
        return

    # Verificar se o Quiz está ativo
    if not quiz['is_active']:
        st.warning(f"O questionário '{quiz['title']}' está atualmente encerrado pelo professor.")
        return

    quiz_id = quiz['id']
    quiz_details = db.get_quiz_details(quiz_id)
    questions = quiz_details.get('questions', [])

    if not questions:
        st.warning("Este questionário ainda não possui perguntas cadastradas.")
        return

    # Cabeçalho do Quiz
    st.info(f"### {quiz['title']}\n{quiz['description'] or ''}\n\n**Total de Questões:** {len(questions)} | **Tempo Sugerido:** {quiz['time_limit_minutes'] or 'Livre'} min")

    # Identificação do Aluno
    st.markdown("#### Identificação")
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Seu Nome Completo *", placeholder="Ex: Maria Eduarda Santos", key=f"name_{quiz_id}")
    with col2:
        student_id = st.text_input("Matrícula / Turma / E-mail (Opcional)", placeholder="Ex: Turma 3B / 202401", key=f"id_{quiz_id}")

    st.divider()
    st.markdown("#### Questões")

    # Dicionário para armazenar as seleções do aluno
    selected_answers = {}

    for idx, q in enumerate(questions, 1):
        st.markdown(f"**Questão {idx}** ({q['points']} pts)")
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
    if st.button("Enviar Respostas", type="primary", use_container_width=True):
        if not student_name.strip():
            st.error("Por favor, preencha o seu nome completo antes de enviar!")
            st.stop()

        unanswered = len(questions) - len(selected_answers)
        if unanswered > 0:
            st.warning(f"Você ainda não respondeu {unanswered} questão(ões). Por favor, responda todas para enviar.")
            st.stop()

        # Registrar no banco de dados SQLite
        with st.spinner("Processando e calculando sua pontuação..."):
            result = db.submit_student_answers(
                quiz_id=quiz_id,
                student_name=student_name,
                student_identifier=student_id,
                selected_options=selected_answers
            )

        # Feedback
        st.success("Suas respostas foram enviadas com sucesso!")
        
        score = result['score']
        total = result['total_points']
        pct = result['percentage']

        if pct >= 70:
            alert_type = st.success
        elif pct >= 50:
            alert_type = st.info
        else:
            alert_type = st.warning

        alert_type(f"### Sua Nota: **{score:.1f} / {total:.1f}** ({pct:.1f}%)")

        # Detalhamento e Gabarito
        with st.expander("Ver Gabarito e Explicações", expanded=True):
            for idx, q in enumerate(questions, 1):
                user_opt_id = selected_answers.get(q['id'])
                correct_opt = next((o for o in q['options'] if o['is_correct']), None)
                chosen_opt = next((o for o in q['options'] if o['id'] == user_opt_id), None)
                
                is_hit = chosen_opt and chosen_opt['is_correct']
                status_label = "[Correta]" if is_hit else "[Incorreta]"
                
                st.markdown(f"**{status_label} Questão {idx}:** {q['question_text']}")
                if q.get('image_data'):
                    st.image(q['image_data'], caption=f"Ilustração - Questão {idx}", width=300)
                st.markdown(f"- **Sua resposta:** {chosen_opt['option_text'] if chosen_opt else 'Não respondida'}")
                if not is_hit and correct_opt:
                    st.markdown(f"- **Resposta correta:** {correct_opt['option_text']}")
                if q.get('explanation'):
                    st.caption(f"**Explicação do Professor:** {q['explanation']}")
                st.divider()
