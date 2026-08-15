import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db

def render_dashboard_view():
    st.title("📊 Painel Dinâmico de Resultados da Turma")
    st.markdown("Acompanhe o desempenho dos alunos em tempo real, identifique dificuldades e analise métricas detalhadas.")

    quizzes = db.get_all_quizzes()
    if not quizzes:
        st.info("Nenhum quiz encontrado para exibir estatísticas.")
        return

    # Seletor de Quiz no topo com botão de atualização rápida
    col_sel, col_ref = st.columns([4, 1])
    with col_sel:
        quiz_map = {f"{q['title']} (Código: {q['quiz_code']}) — {q['submission_count']} respostas": q['id'] for q in quizzes}
        selected_label = st.selectbox("Selecione o Questionário para Analisar:", list(quiz_map.keys()))
        selected_quiz_id = quiz_map[selected_label]
    
    with col_ref:
        st.write("")
        st.write("")
        if st.button("🔄 Atualizar Dados", use_container_width=True, type="primary"):
            st.rerun()

    analytics = db.get_quiz_analytics_data(selected_quiz_id)
    quiz_info = analytics.get('quiz', {})
    submissions = analytics.get('submissions', [])
    questions_stat = analytics.get('questions_stat', [])
    options_breakdown = analytics.get('options_breakdown', [])

    if not submissions:
        st.warning(f"⚠️ Nenhuma resposta registrada ainda para o quiz **'{quiz_info.get('title')}'**.")
        st.info("Peça aos alunos para escanearem o QR Code gerado no menu **'Área do Professor'**!")
        return

    df_subs = pd.DataFrame(submissions)

    # =========================================================================
    # MÉTRICAS PRINCIPAIS (KPIs)
    # =========================================================================
    st.divider()
    total_students = len(df_subs)
    avg_score = df_subs['score'].mean()
    max_score = df_subs['score'].max()
    min_score = df_subs['score'].min()
    avg_pct = df_subs['percentage'].mean()
    pass_rate = (df_subs['percentage'] >= 60.0).mean() * 100

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("👥 Total de Alunos", f"{total_students}")
    with kpi2:
        st.metric("📈 Média da Turma", f"{avg_score:.1f} pts", f"{avg_pct:.1f}%")
    with kpi3:
        st.metric("🥇 Maior Nota", f"{max_score:.1f} pts")
    with kpi4:
        st.metric("📉 Menor Nota", f"{min_score:.1f} pts")
    with kpi5:
        st.metric("🎯 Taxa de Aprovação (≥60%)", f"{pass_rate:.1f}%")

    st.divider()

    # =========================================================================
    # GRÁFICOS DINÂMICOS COM PLOTLY
    # =========================================================================
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📊 Distribuição de Notas da Turma")
        fig_hist = px.histogram(
            df_subs,
            x="percentage",
            nbins=10,
            color_discrete_sequence=["#6366F1"],
            labels={"percentage": "Aproveitamento (%)", "count": "Qtd. Alunos"},
            title="Histograma de Desempenho (%)"
        )
        fig_hist.update_layout(
            bargap=0.1,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_chart2:
        st.subheader("🎯 Taxa de Acerto por Questão")
        if questions_stat:
            df_q = pd.DataFrame(questions_stat)
            df_q['label'] = [f"Q{q['order_num']}" for q in questions_stat]
            
            # Cores dinâmicas: verde para alta taxa, vermelho/amarelo para dúvidas
            colors = []
            for rate in df_q['success_rate']:
                if rate >= 70:
                    colors.append("#10B981") # Verde
                elif rate >= 40:
                    colors.append("#F59E0B") # Amarelo/Laranja
                else:
                    colors.append("#EF4444") # Vermelho (Atenção)

            fig_bar = px.bar(
                df_q,
                x="label",
                y="success_rate",
                text="success_rate",
                hover_data=["question_text", "total_answers", "correct_answers"],
                labels={"label": "Questão", "success_rate": "% Acertos"},
                title="% de Acertos por Questão (Identifique Dúvidas)"
            )
            fig_bar.update_traces(marker_color=colors, texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(
                yaxis=dict(range=[0, 110]),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # =========================================================================
    # DETALHAMENTO DE ALTERNATIVAS POR QUESTÃO
    # =========================================================================
    if options_breakdown:
        with st.expander("🔍 Análise Pedagógica: Escolha de Alternativas por Questão", expanded=False):
            st.markdown("Veja quais alternativas incorretas (distratores) mais confundiram os alunos:")
            df_opts = pd.DataFrame(options_breakdown)
            
            # Agrupar por questão
            unique_q_ids = df_opts['question_id'].unique()
            for q_id in unique_q_ids:
                subset = df_opts[df_opts['question_id'] == q_id]
                q_text = next((q['question_text'] for q in questions_stat if q['question_id'] == q_id), f"Questão {q_id}")
                st.markdown(f"**Questão:** {q_text}")
                
                fig_opt = go.Figure()
                fig_opt.add_trace(go.Bar(
                    x=[opt['option_text'] for _, opt in subset.iterrows()],
                    y=subset['pick_count'],
                    marker_color=['#10B981' if opt['is_correct'] else '#64748B' for _, opt in subset.iterrows()],
                    text=subset['pick_count'],
                    textposition='auto'
                ))
                fig_opt.update_layout(
                    title=f"Distribuição de Respostas (Verde = Correta)",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=280,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_opt, use_container_width=True)
                st.divider()

    # =========================================================================
    # TABELA DE RANKING E CLASSIFICAÇÃO
    # =========================================================================
    st.subheader("🏆 Ranking e Resultados Individuais")
    
    # Preparar DataFrame com medalhas
    df_display = df_subs.copy()
    
    medals = ["🥇 1º", "🥈 2º", "🥉 3º"]
    ranking_col = []
    for i in range(len(df_display)):
        if i < 3:
            ranking_col.append(medals[i])
        else:
            ranking_col.append(f"{i+1}º")
    
    df_display.insert(0, "Posição", ranking_col)
    df_display = df_display.rename(columns={
        "student_name": "Nome do Aluno",
        "student_identifier": "Matrícula / Turma",
        "score": "Pontos",
        "total_points": "Total Possível",
        "percentage": "Aproveitamento (%)",
        "submitted_at": "Data/Hora de Envio"
    })
    
    st.dataframe(
        df_display[["Posição", "Nome do Aluno", "Matrícula / Turma", "Pontos", "Total Possível", "Aproveitamento (%)", "Data/Hora de Envio"]],
        use_container_width=True,
        hide_index=True
    )

    # Botão de Exportação CSV
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Resultados Completos em CSV (Excel)",
        data=csv_data,
        file_name=f"resultados_{quiz_info.get('quiz_code', 'quiz')}.csv",
        mime="text/csv",
        use_container_width=True
    )
