import streamlit as st
import database as db
from modules.professor import render_professor_view
from modules.aluno import render_aluno_view
from modules.dashboard import render_dashboard_view

# Configuração global da página
st.set_page_config(
    page_title="Quiz Interativo com QR Code",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o banco SQLite e popula dados de exemplo se necessário
db.seed_sample_quiz_if_empty()

# Leitura de parâmetros de URL para acesso direto via QR Code
query_params = st.query_params
url_quiz_code = query_params.get("quiz", None)

# Se o usuário acessou via link com código de quiz (ex: /?quiz=A1B2C3), direciona para o Portal do Aluno
default_index = 1 if url_quiz_code else 0

# Barra Lateral de Navegação
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/quiz.png", width=70)
    st.title("🎯 Quiz Interativo")
    st.caption("Sistema de Avaliações em Tempo Real")
    
    st.divider()
    
    nav_options = [
        "👨‍🏫 Área do Professor",
        "🎓 Portal do Aluno",
        "📊 Dashboard de Resultados"
    ]
    
    # Se veio com parâmetro na URL, pré-seleciona "Portal do Aluno"
    selected_page = st.radio(
        "Navegação:",
        nav_options,
        index=default_index
    )
    
    st.divider()
    st.markdown("### 💡 Como Usar:")
    st.markdown("""
    1. **Professor:** Crie o quiz e as questões.
    2. **QR Code:** Projete o QR code na tela para os alunos.
    3. **Alunos:** Escaneiam pelo celular e respondem.
    4. **Resultados:** Acompanhe o gráfico em tempo real no Dashboard!
    """)
    st.caption("Powered by Streamlit & SQLite")

# Roteamento de Páginas
if selected_page == "👨‍🏫 Área do Professor":
    render_professor_view()
elif selected_page == "🎓 Portal do Aluno":
    render_aluno_view(preselected_quiz_code=url_quiz_code)
elif selected_page == "📊 Dashboard de Resultados":
    render_dashboard_view()
