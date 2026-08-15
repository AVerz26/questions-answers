import streamlit as st
import qrcode
import io
import socket
from PIL import Image
import database as db

def get_local_ip():
    """Tenta identificar o IP local da máquina na rede Wi-Fi/Ethernet."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def generate_qr_image(url: str) -> bytes:
    """Gera os bytes de uma imagem PNG com o QR Code de alta qualidade."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def render_professor_view():
    st.title("👨‍🏫 Painel do Professor - Gestão de Quizzes")
    st.markdown("Crie questionários, cadastre questões, gere QR Codes para os alunos e gerencie suas avaliações.")
    
    tabs = st.tabs(["📋 Meus Quizzes & QR Codes", "➕ Criar Novo Quiz", "❓ Adicionar Questões"])

    # =========================================================================
    # TAB 1: MEUS QUIZZES & QR CODES
    # =========================================================================
    with tabs[0]:
        st.subheader("Questionários Cadastrados")
        quizzes = db.get_all_quizzes()
        
        if not quizzes:
            st.info("Nenhum quiz cadastrado ainda. Use a aba **'Criar Novo Quiz'** para começar!")
        else:
            local_ip = get_local_ip()
            
            for q in quizzes:
                with st.expander(f"📌 **{q['title']}** (Código: `{q['quiz_code']}`) — {q['question_count']} questões | {q['submission_count']} respostas", expanded=False):
                    col1, col2 = st.columns([1.2, 1])
                    
                    with col1:
                        st.markdown(f"**Descrição:** {q['description'] or '_Sem descrição_'}")
                        st.markdown(f"**Criado em:** {q['created_at']}")
                        status_str = "🟢 **Ativo (Recebendo Respostas)**" if q['is_active'] else "🔴 **Pausado / Fechado**"
                        st.markdown(f"**Status:** {status_str}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if q['is_active']:
                                if st.button("⏸️ Pausar Quiz", key=f"pause_{q['id']}", use_container_width=True):
                                    db.toggle_quiz_status(q['id'], False)
                                    st.rerun()
                            else:
                                if st.button("▶️ Ativar Quiz", key=f"activate_{q['id']}", use_container_width=True):
                                    db.toggle_quiz_status(q['id'], True)
                                    st.rerun()
                        
                        with col_btn2:
                            if st.button("🗑️ Excluir Quiz", key=f"del_{q['id']}", type="secondary", use_container_width=True):
                                db.delete_quiz(q['id'])
                                st.success("Quiz excluído com sucesso!")
                                st.rerun()

                        st.divider()
                        st.markdown("#### 🔗 Link de Acesso do Aluno")
                        
                        # Opção para configurar domínio ou IP
                        base_url_default = f"http://{local_ip}:8501"
                        base_url = st.text_input(
                            "Endereço Base (IP Local ou URL do Streamlit Cloud):",
                            value=base_url_default,
                            key=f"url_base_{q['id']}",
                            help="Se os alunos estiverem no mesmo Wi-Fi, use o IP local. Se estiver no Streamlit Cloud, cole a URL pública."
                        )
                        
                        quiz_url = f"{base_url}/?quiz={q['quiz_code']}"
                        st.code(quiz_url, language="text")

                    with col2:
                        st.markdown("#### 📱 QR Code para Sala de Aula")
                        qr_bytes = generate_qr_image(quiz_url)
                        st.image(qr_bytes, caption=f"Escaneie para responder: {q['title']}", width=230)
                        
                        st.download_button(
                            label="⬇️ Baixar Imagem do QR Code (PNG)",
                            data=qr_bytes,
                            file_name=f"qrcode_quiz_{q['quiz_code']}.png",
                            mime="image/png",
                            key=f"dl_{q['id']}",
                            use_container_width=True
                        )

    # =========================================================================
    # TAB 2: CRIAR NOVO QUIZ
    # =========================================================================
    with tabs[1]:
        st.subheader("Cadastrar Novo Questionário")
        with st.form("form_create_quiz", clear_on_submit=True):
            title = st.text_input("Título do Quiz *", placeholder="Ex: Avaliação de Física - Cinemática")
            description = st.text_area("Descrição / Instruções para os Alunos", placeholder="Ex: Responda a todas as questões individualmente. Boa sorte!")
            time_limit = st.number_input("Tempo Estimado (minutos - opcional)", min_value=0, max_value=180, value=0, help="0 significa sem limite de tempo estrito.")
            
            submitted = st.form_submit_button("💾 Salvar Quiz", use_container_width=True, type="primary")
            if submitted:
                if not title.strip():
                    st.error("Por favor, preencha o título do Quiz!")
                else:
                    new_q = db.create_quiz(title, description, time_limit)
                    st.success(f"Quiz **'{title}'** criado com sucesso! Código gerado: **{new_q['quiz_code']}**")
                    st.info("Agora vá para a aba **'Adicionar Questões'** para cadastrar as perguntas!")

    # =========================================================================
    # TAB 3: ADICIONAR QUESTÕES
    # =========================================================================
    with tabs[2]:
        st.subheader("Adicionar Perguntas ao Quiz")
        quizzes = db.get_all_quizzes()
        
        if not quizzes:
            st.warning("Crie primeiro um Quiz na aba anterior.")
        else:
            quiz_options = {f"{q['title']} (Código: {q['quiz_code']})": q['id'] for q in quizzes}
            selected_quiz_label = st.selectbox("Selecione o Quiz de Destino:", list(quiz_options.keys()))
            selected_quiz_id = quiz_options[selected_quiz_label]

            # Mostrar questões atuais do quiz selecionado
            quiz_data = db.get_quiz_details(selected_quiz_id)
            existing_questions = quiz_data.get('questions', [])
            
            st.markdown(f"**Questões atuais neste quiz:** {len(existing_questions)}")
            if existing_questions:
                with st.expander("👀 Ver Questões já cadastradas", expanded=False):
                    for idx, q_item in enumerate(existing_questions, 1):
                        st.markdown(f"**{idx}. {q_item['question_text']}** ({q_item['points']} pts)")
                        for opt in q_item['options']:
                            mark = "✅" if opt['is_correct'] else "⚪"
                            st.write(f"{mark} {opt['option_text']}")
                        if q_item.get('explanation'):
                            st.caption(f"💡 Explicação: {q_item['explanation']}")
                        st.divider()

            st.markdown("---")
            st.markdown("#### 📝 Formulário da Nova Questão")

            with st.form("form_add_question", clear_on_submit=True):
                question_text = st.text_area("Enunciado da Questão *", placeholder="Ex: Qual é a fórmula da velocidade média?")
                points = st.number_input("Pontuação da Questão", min_value=0.5, max_value=100.0, value=2.5, step=0.5)
                explanation = st.text_input("Explicação da Resposta (Feedback para o Aluno após término)", placeholder="Ex: Vm = ΔS / Δt")
                
                st.markdown("**Alternativas de Resposta (Marque a Correta):**")
                
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    opt_a = st.text_input("Alternativa A *", placeholder="Texto da opção A")
                with col_b:
                    is_correct_a = st.checkbox("Correta (A)", value=True, key="chk_a")

                col_a, col_b = st.columns([4, 1])
                with col_a:
                    opt_b = st.text_input("Alternativa B *", placeholder="Texto da opção B")
                with col_b:
                    is_correct_b = st.checkbox("Correta (B)", value=False, key="chk_b")

                col_a, col_b = st.columns([4, 1])
                with col_a:
                    opt_c = st.text_input("Alternativa C (Opcional)", placeholder="Texto da opção C")
                with col_b:
                    is_correct_c = st.checkbox("Correta (C)", value=False, key="chk_c")

                col_a, col_b = st.columns([4, 1])
                with col_a:
                    opt_d = st.text_input("Alternativa D (Opcional)", placeholder="Texto da opção D")
                with col_b:
                    is_correct_d = st.checkbox("Correta (D)", value=False, key="chk_d")

                btn_add_q = st.form_submit_button("➕ Salvar Questão", use_container_width=True, type="primary")

                if btn_add_q:
                    if not question_text.strip():
                        st.error("Digite o enunciado da questão!")
                    elif not opt_a.strip() or not opt_b.strip():
                        st.error("Preencha ao menos as alternativas A e B!")
                    else:
                        options_list = [
                            {"text": opt_a.strip(), "is_correct": is_correct_a},
                            {"text": opt_b.strip(), "is_correct": is_correct_b}
                        ]
                        if opt_c.strip():
                            options_list.append({"text": opt_c.strip(), "is_correct": is_correct_c})
                        if opt_d.strip():
                            options_list.append({"text": opt_d.strip(), "is_correct": is_correct_d})

                        correct_count = sum(1 for o in options_list if o['is_correct'])
                        if correct_count != 1:
                            st.error("Selecione exatamente UMA alternativa como correta!")
                        else:
                            db.add_question(
                                quiz_id=selected_quiz_id,
                                question_text=question_text.strip(),
                                points=points,
                                explanation=explanation.strip(),
                                options=options_list
                            )
                            st.success("🎉 Questão cadastrada com sucesso!")
                            st.rerun()
