# Quiz Interativo com Streamlit, SQLite e QR Code

Sistema completo e moderno para criação de questionários/quizzes interativos para professores e salas de aula, com geração automática de **QR Code** para resposta dos alunos via smartphone e **Dashboard dinâmico em tempo real** com gráficos analíticos.

---

## Funcionalidades Principais

- **Área do Professor**:
  - Cadastro rápido de questionários (título, instruções, tempo limite).
  - Adição de questões de múltipla escolha com pontuação personalizada e gabarito com explicação pedagógica.
  - Ativação/Pausa e exclusão de questionários.
- **Gerador de QR Code Inteligente**:
  - Geração automática do QR Code com o link direto do quiz (`https://questions-and-anwers.streamlit.app/?quiz=CODIGO`).
  - Detecção automática do IP da rede local para uso em sala de aula (Wi-Fi).
  - Download da imagem do QR Code em alta resolução (PNG) para projeção ou slides.
- **Portal do Aluno**:
  - Interface limpa, responsiva e adaptada para celulares.
  - Acesso direto via câmera/QR Code.
  - Correção automática imediata com cálculo de nota, porcentagem e visualização do gabarito comentado.
- **Dashboard Dinâmico de Resultados**:
  - **KPIs em tempo real**: Total de alunos, média da turma, maior/menor nota e taxa de aprovação.
  - **Gráficos Interativos (Plotly)**: Histograma de distribuição de notas e taxa de acerto por questão (destacando pontos de dúvida).
  - **Análise Pedagógica**: Visualização de alternativas mais marcadas pelos alunos (análise de distratores).
  - **Tabela de Classificação/Ranking**: Com posições e exportação dos dados para **CSV (Excel)**.

---

## Estrutura do Projeto

```text
quiz_interativo_streamlit/
├── .streamlit/
│   └── config.toml          # Configurações de tema e servidor
├── modules/
│   ├── professor.py         # Criação de quizzes, questões e geração de QR Code
│   ├── aluno.py             # Interface responsiva para o aluno responder
│   └── dashboard.py         # Dashboard interativo com gráficos Plotly e ranking
├── app.py                   # Ponto de entrada e roteamento via URL params
├── database.py              # Camada de persistência SQLite e queries analíticas
├── requirements.txt         # Lista de dependências Python
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Documentação do projeto
```

---

## Como Executar Localmente

### 1. Pré-requisitos
Tenha o **Python 3.9+** instalado no seu computador.

### 2. Clonar ou Baixar o Projeto
Abra o terminal/PowerShell na pasta do projeto:
```bash
cd quiz_interativo_streamlit
```

### 3. Criar e Ativar um Ambiente Virtual (Recomendado)
```bash
# No Windows:
python -m venv venv
.\venv\Scripts\activate

# No Linux/Mac:
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 5. Iniciar a Aplicação
```bash
streamlit run app.py
```

O Streamlit abrirá automaticamente no navegador em: `http://localhost:8501`.

---

## Como Fazer Upload para o GitHub

Execute os comandos no terminal dentro da pasta do projeto:

```bash
# 1. Inicializar o repositório git
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Criar o primeiro commit
git commit -m "feat: Aplicativo de Quiz Interativo com Streamlit, SQLite e QR Code"

# 4. Criar a branch principal
git branch -M main

# 5. Conectar com o seu repositório remoto do GitHub
# (Substitua SEU-USUARIO e SEU-REPOSITORIO pelos seus dados)
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git

# 6. Enviar os arquivos
git push -u origin main
```

---

## Licença
Este projeto está sob a licença MIT. Sinta-se livre para usar, modificar e distribuir.
