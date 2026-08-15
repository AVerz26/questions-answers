import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "quiz_app.db"

def get_connection():
    """Retorna uma conexão com o banco de dados SQLite com suporte a Foreign Keys."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Cria todas as tabelas necessárias no banco SQLite se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de Quizzes / Questionários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        time_limit_minutes INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tabela de Questões
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_type TEXT DEFAULT 'multipla_escolha',
        points REAL DEFAULT 1.0,
        order_num INTEGER DEFAULT 1,
        explanation TEXT DEFAULT '',
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    );
    """)

    # Tabela de Alternativas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        option_text TEXT NOT NULL,
        is_correct INTEGER DEFAULT 0,
        order_num INTEGER DEFAULT 1,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    );
    """)

    # Tabela de Submissões dos Alunos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        student_identifier TEXT,
        score REAL DEFAULT 0.0,
        total_points REAL DEFAULT 0.0,
        percentage REAL DEFAULT 0.0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    );
    """)

    # Tabela de Respostas Individuais dos Alunos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_option_id INTEGER,
        is_correct INTEGER DEFAULT 0,
        points_earned REAL DEFAULT 0.0,
        FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
        FOREIGN KEY (selected_option_id) REFERENCES options(id) ON DELETE SET NULL
    );
    """)

    conn.commit()
    conn.close()

def generate_short_code() -> str:
    """Gera um código alfanumérico curto e amigável para o quiz."""
    return uuid.uuid4().hex[:6].upper()

def create_quiz(title: str, description: str = "", time_limit_minutes: int = 0) -> Dict[str, Any]:
    """Cria um novo quiz e retorna os dados inseridos."""
    conn = get_connection()
    cursor = conn.cursor()
    quiz_code = generate_short_code()
    
    cursor.execute("""
        INSERT INTO quizzes (quiz_code, title, description, time_limit_minutes, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (quiz_code, title, description, time_limit_minutes))
    
    quiz_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": quiz_id, "quiz_code": quiz_code, "title": title}

def add_question(quiz_id: int, question_text: str, points: float, explanation: str, options: List[Dict[str, Any]]):
    """
    Adiciona uma questão e suas opções a um quiz.
    options = [{'text': 'Opção A', 'is_correct': True}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = ?", (quiz_id,))
    order_num = cursor.fetchone()[0] + 1

    cursor.execute("""
        INSERT INTO questions (quiz_id, question_text, points, order_num, explanation)
        VALUES (?, ?, ?, ?, ?)
    """, (quiz_id, question_text, points, order_num, explanation))
    
    question_id = cursor.lastrowid

    for idx, opt in enumerate(options):
        cursor.execute("""
            INSERT INTO options (question_id, option_text, is_correct, order_num)
            VALUES (?, ?, ?, ?)
        """, (question_id, opt['text'], 1 if opt.get('is_correct') else 0, idx + 1))

    conn.commit()
    conn.close()
    return question_id

def delete_quiz(quiz_id: int):
    """Exclui um quiz e todos os dados associados em cascata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()

def toggle_quiz_status(quiz_id: int, is_active: bool):
    """Ativa ou desativa a aceitação de respostas para um quiz."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE quizzes SET is_active = ? WHERE id = ?", (1 if is_active else 0, quiz_id))
    conn.commit()
    conn.close()

def get_all_quizzes() -> List[Dict[str, Any]]:
    """Recupera todos os quizzes com contagem de perguntas e respostas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            q.id, q.quiz_code, q.title, q.description, q.time_limit_minutes, q.is_active, q.created_at,
            COUNT(DISTINCT qs.id) as question_count,
            COUNT(DISTINCT s.id) as submission_count
        FROM quizzes q
        LEFT JOIN questions qs ON q.id = qs.quiz_id
        LEFT JOIN submissions s ON q.id = s.quiz_id
        GROUP BY q.id
        ORDER BY q.created_at DESC
    """)
    rows = cursor.fetchall()
    quizzes = [dict(row) for row in rows]
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id: int) -> Optional[Dict[str, Any]]:
    """Recupera um quiz pelo ID numérico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_quiz_by_code(quiz_code: str) -> Optional[Dict[str, Any]]:
    """Recupera um quiz pelo código alfanumérico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE quiz_code = ?", (quiz_code.upper().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_quiz_details(quiz_id: int) -> Dict[str, Any]:
    """Recupera o quiz completo com suas questões e respectivas opções."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    if not quiz:
        conn.close()
        return {}

    quiz_dict = dict(quiz)
    
    cursor.execute("SELECT * FROM questions WHERE quiz_id = ? ORDER BY order_num ASC", (quiz_id,))
    questions = [dict(q) for q in cursor.fetchall()]
    
    for q in questions:
        cursor.execute("SELECT * FROM options WHERE question_id = ? ORDER BY order_num ASC", (q['id'],))
        q['options'] = [dict(opt) for opt in cursor.fetchall()]

    quiz_dict['questions'] = questions
    conn.close()
    return quiz_dict

def submit_student_answers(quiz_id: int, student_name: str, student_identifier: str, selected_options: Dict[int, int]) -> Dict[str, Any]:
    """
    Registra a submissão do aluno, calcula notas e acertos.
    selected_options: { question_id: selected_option_id }
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Busca as questões e opções corretas
    cursor.execute("SELECT id, points FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()
    
    total_points = sum(q['points'] for q in questions)
    score = 0.0
    detailed_answers = []

    for q in questions:
        q_id = q['id']
        pts = q['points']
        selected_opt_id = selected_options.get(q_id)
        
        is_correct = 0
        points_earned = 0.0
        
        if selected_opt_id:
            cursor.execute("SELECT is_correct FROM options WHERE id = ? AND question_id = ?", (selected_opt_id, q_id))
            opt = cursor.fetchone()
            if opt and opt['is_correct'] == 1:
                is_correct = 1
                points_earned = pts
                score += pts

        detailed_answers.append({
            'question_id': q_id,
            'selected_option_id': selected_opt_id,
            'is_correct': is_correct,
            'points_earned': points_earned
        })

    percentage = (score / total_points * 100) if total_points > 0 else 0.0

    # Insere Submissão
    cursor.execute("""
        INSERT INTO submissions (quiz_id, student_name, student_identifier, score, total_points, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (quiz_id, student_name.strip(), student_identifier.strip(), score, total_points, round(percentage, 2)))
    
    submission_id = cursor.lastrowid

    # Insere Respostas Individuais
    for ans in detailed_answers:
        cursor.execute("""
            INSERT INTO student_answers (submission_id, question_id, selected_option_id, is_correct, points_earned)
            VALUES (?, ?, ?, ?, ?)
        """, (submission_id, ans['question_id'], ans['selected_option_id'], ans['is_correct'], ans['points_earned']))

    conn.commit()
    conn.close()

    return {
        "submission_id": submission_id,
        "score": score,
        "total_points": total_points,
        "percentage": round(percentage, 2)
    }

def get_submissions_by_quiz(quiz_id: int) -> List[Dict[str, Any]]:
    """Retorna todas as submissões de um quiz ordenadas por nota."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, student_name, student_identifier, score, total_points, percentage, submitted_at
        FROM submissions
        WHERE quiz_id = ?
        ORDER BY score DESC, submitted_at ASC
    """, (quiz_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_quiz_analytics_data(quiz_id: int) -> Dict[str, Any]:
    """Retorna dados estatísticos completos e agrupados para o Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    # Informações do Quiz
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    if not quiz:
        conn.close()
        return {}

    # Submissões
    cursor.execute("""
        SELECT id, student_name, student_identifier, score, total_points, percentage, submitted_at
        FROM submissions
        WHERE quiz_id = ?
        ORDER BY score DESC
    """, (quiz_id,))
    submissions = [dict(s) for s in cursor.fetchall()]

    # Questões e taxa de acertos
    cursor.execute("""
        SELECT 
            q.id as question_id,
            q.question_text,
            q.points,
            q.order_num,
            COUNT(sa.id) as total_answers,
            SUM(CASE WHEN sa.is_correct = 1 THEN 1 ELSE 0 END) as correct_answers
        FROM questions q
        LEFT JOIN student_answers sa ON q.id = sa.question_id
        WHERE q.quiz_id = ?
        GROUP BY q.id
        ORDER BY q.order_num ASC
    """, (quiz_id,))
    questions_stat = []
    for row in cursor.fetchall():
        d = dict(row)
        tot = d['total_answers'] or 0
        corr = d['correct_answers'] or 0
        d['success_rate'] = round((corr / tot * 100), 1) if tot > 0 else 0.0
        questions_stat.append(d)

    # Detalhamento por Opção (quantas vezes cada alternativa foi marcada)
    cursor.execute("""
        SELECT 
            o.id as option_id,
            o.question_id,
            o.option_text,
            o.is_correct,
            COUNT(sa.id) as pick_count
        FROM options o
        JOIN questions q ON o.question_id = q.id
        LEFT JOIN student_answers sa ON o.id = sa.selected_option_id
        WHERE q.quiz_id = ?
        GROUP BY o.id
        ORDER BY o.question_id ASC, o.order_num ASC
    """, (quiz_id,))
    options_breakdown = [dict(opt) for opt in cursor.fetchall()]

    conn.close()
    return {
        "quiz": dict(quiz),
        "submissions": submissions,
        "questions_stat": questions_stat,
        "options_breakdown": options_breakdown
    }

def seed_sample_quiz_if_empty():
    """Cria um quiz de exemplo rico caso o banco esteja novo."""
    init_db()
    quizzes = get_all_quizzes()
    if len(quizzes) == 0:
        quiz = create_quiz(
            title="Quiz Demonstração: Conhecimentos Gerais e Tecnologia",
            description="Questionário interativo de teste para demonstração em sala de aula.",
            time_limit_minutes=15
        )
        q_id = quiz['id']
        
        # Pergunta 1
        add_question(
            quiz_id=q_id,
            question_text="Qual linguagem de programação é amplamente utilizada para Ciência de Dados e aplicações com Streamlit?",
            points=2.5,
            explanation="Python é a principal linguagem usada no ecossistema Streamlit e Data Science.",
            options=[
                {"text": "Python", "is_correct": True},
                {"text": "C++", "is_correct": False},
                {"text": "PHP", "is_correct": False},
                {"text": "Ruby", "is_correct": False}
            ]
        )
        
        # Pergunta 2
        add_question(
            quiz_id=q_id,
            question_text="O SQLite é um banco de dados relacional que se destaca por:",
            points=2.5,
            explanation="O SQLite é embutido (serverless) e armazena tudo em um único arquivo local.",
            options=[
                {"text": "Ser serverless e armazenar a base em um único arquivo", "is_correct": True},
                {"text": "Exigir um servidor dedicado e complexo", "is_correct": False},
                {"text": "Funcionar apenas como banco NoSQL", "is_correct": False},
                {"text": "Não suportar chaves primárias ou transações", "is_correct": False}
            ]
        )

        # Pergunta 3
        add_question(
            quiz_id=q_id,
            question_text="Qual é a principal finalidade de um QR Code em sala de aula interativa?",
            points=2.5,
            explanation="O QR Code permite que os alunos acessem instantaneamente o link do questionário apontando a câmera do celular.",
            options=[
                {"text": "Facilitar o acesso instantâneo ao formulário pelo smartphone dos alunos", "is_correct": True},
                {"text": "Aumentar a velocidade do Wi-Fi da escola", "is_correct": False},
                {"text": "Substituir a necessidade de energia elétrica", "is_correct": False},
                {"text": "Gravar as aulas em vídeo automaticamente", "is_correct": False}
            ]
        )

        # Pergunta 4
        add_question(
            quiz_id=q_id,
            question_text="O protocolo HTTP/HTTPS é fundamental na web. O que a sigla 'S' em HTTPS significa?",
            points=2.5,
            explanation="O 'S' significa Secure (Seguro), utilizando criptografia SSL/TLS.",
            options=[
                {"text": "Secure (Seguro com criptografia)", "is_correct": True},
                {"text": "Speed (Velocidade)", "is_correct": False},
                {"text": "Standard (Padrão)", "is_correct": False},
                {"text": "Server (Servidor)", "is_correct": False}
            ]
        )

        # Simular algumas submissões de exemplo para o dashboard já começar com visual incrível
        submit_student_answers(q_id, "Ana Clara Silva", "20240101", {1: 1, 2: 5, 3: 9, 4: 13}) # 10.0
        submit_student_answers(q_id, "Bruno Henrique", "20240102", {1: 1, 2: 6, 3: 9, 4: 13})  # 7.5
        submit_student_answers(q_id, "Carlos Eduardo", "20240103", {1: 1, 2: 5, 3: 10, 4: 14}) # 5.0
        submit_student_answers(q_id, "Daniela Souza", "20240104", {1: 1, 2: 5, 3: 9, 4: 13})  # 10.0
        submit_student_answers(q_id, "Eduardo Gomes", "20240105", {1: 2, 2: 5, 3: 9, 4: 14})  # 5.0
        submit_student_answers(q_id, "Fernanda Lima", "20240106", {1: 1, 2: 5, 3: 9, 4: 13})  # 10.0
        submit_student_answers(q_id, "Gabriel Martins", "20240107", {1: 1, 2: 7, 3: 9, 4: 13})# 7.5
