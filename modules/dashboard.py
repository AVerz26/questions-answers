import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
import tri_engine

def render_dashboard_view():
    st.title("Painel Analítico de Resultados & Psicométrico (TRI ENEM)")
    st.markdown("Acompanhe o desempenho da turma em tempo real, analisando a proficiência na régua do ENEM, coerência pedagógica e curvas psicométricas dos itens.")

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
        if st.button("Atualizar Dados", use_container_width=True, type="primary"):
            st.rerun()

    analytics = db.get_quiz_analytics_data(selected_quiz_id)
    quiz_info = analytics.get('quiz', {})
    submissions = analytics.get('submissions', [])
    questions_stat = analytics.get('questions_stat', [])
    options_breakdown = analytics.get('options_breakdown', [])

    if not submissions:
        st.warning(f"Nenhuma resposta registrada ainda para o quiz '{quiz_info.get('title')}'.")
        st.info("Peça aos alunos para acessarem o link ou escanearem o QR Code gerado no menu 'Área do Professor'.")
        return

    df_subs = pd.DataFrame(submissions)

    # Garantir colunas TRI caso venham de submissões antigas
    if 'tri_score' not in df_subs.columns:
        df_subs['tri_score'] = 500.0
    if 'theta' not in df_subs.columns:
        df_subs['theta'] = 0.0
    if 'coherence_label' not in df_subs.columns:
        df_subs['coherence_label'] = 'Coerente'

    # =========================================================================
    # MÉTRICAS PRINCIPAIS (TRI ENEM & ACERTOS)
    # =========================================================================
    st.divider()
    total_students = len(df_subs)
    avg_tri = df_subs['tri_score'].mean()
    max_tri = df_subs['tri_score'].max()
    min_tri = df_subs['tri_score'].min()
    avg_theta = df_subs['theta'].mean()
    avg_pct = df_subs['percentage'].mean()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Total de Alunos", f"{total_students}")
    with kpi2:
        st.metric("Média TRI (ENEM)", f"{avg_tri:.1f} pts", f"{avg_theta:+.2f} θ")
    with kpi3:
        st.metric("Maior Nota TRI", f"{max_tri:.1f} pts")
    with kpi4:
        st.metric("Menor Nota TRI", f"{min_tri:.1f} pts")
    with kpi5:
        st.metric("Aproveitamento Médio", f"{avg_pct:.1f}%")

    st.divider()

    # =========================================================================
    # GRÁFICOS DINÂMICOS COM PLOTLY
    # =========================================================================
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Dispersão: Aproveitamento (%) vs. Nota TRI (ENEM)")
        st.caption("Ilustra a 'escada de conhecimento': alunos com mesmo % de acertos têm notas diferentes conforme a coerência das respostas.")
        
        # Mapeamento de cores para coerência
        color_map = {
            "Alta Coerência Pedagógica": "#10B981", # Verde
            "Coerência Regular": "#F59E0B",        # Laranja
            "Indício de Chute (Incoerente)": "#EF4444", # Vermelho
            "Coerente": "#6366F1"                  # Roxo
        }

        fig_disp = px.scatter(
            df_subs,
            x="percentage",
            y="tri_score",
            color="coherence_label",
            color_discrete_map=color_map,
            hover_data=["student_name", "score", "theta"],
            labels={"percentage": "Aproveitamento Clássico (%)", "tri_score": "Nota TRI (Escala ENEM)", "coherence_label": "Coerência"},
            title="Efeito da Coerência Pedagógica na Nota TRI"
        )
        fig_disp.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color='white')))
        fig_disp.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_disp, use_container_width=True)

    with col_chart2:
        st.subheader("Distribuição da Proficiência da Turma")
        st.caption("Histograma das notas estimadas na régua do ENEM (Média 500 / Desvio 100).")
        fig_hist = px.histogram(
            df_subs,
            x="tri_score",
            nbins=8,
            color_discrete_sequence=["#8B5CF6"],
            labels={"tri_score": "Nota TRI (ENEM)", "count": "Qtd. Alunos"},
            title="Distribuição das Notas TRI na Turma"
        )
        fig_hist.update_layout(
            bargap=0.1,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # =========================================================================
    # CURVAS CARACTERÍSTICAS DOS ITENS (CCI - MODELO 3PL DO ENEM)
    # =========================================================================
    if questions_stat:
        with st.expander("📈 Curvas Características dos Itens (CCI - Modelo Logístico 3PL)", expanded=False):
            st.markdown("""
            A **Curva Característica do Item (CCI)** mostra a probabilidade esperada de um aluno acertar a questão conforme seu nível de conhecimento (proficiência $\\theta$):
            - **Questões Fáceis:** Curva deslocada para a esquerda (alta chance de acerto mesmo com proficiência menor).
            - **Questões Difíceis:** Curva deslocada para a direita (exige maior proficiência para acertar).
            - **Assíntota Inferior ($c$):** Probabilidade de acerto ao acaso (chute).
            """)
            
            fig_cci = go.Figure()
            
            # Paleta de cores para as questões
            colors = ["#38BDF8", "#34D399", "#FBBF24", "#F87171", "#A78BFA", "#F472B6"]
            
            for idx, q_item in enumerate(questions_stat):
                a_val = q_item.get('param_a') if q_item.get('param_a') is not None else 1.2
                b_val = q_item.get('param_b') if q_item.get('param_b') is not None else 0.0
                c_val = q_item.get('param_c') if q_item.get('param_c') is not None else 0.25
                d_level = q_item.get('difficulty_level', 'Média')
                
                pts = tri_engine.get_icc_curve_points(a_val, b_val, c_val)
                color = colors[idx % len(colors)]
                
                fig_cci.add_trace(go.Scatter(
                    x=pts['enem_scale'],
                    y=pts['probability'],
                    mode='lines',
                    name=f"Q{q_item['order_num']} ({d_level}) [b={b_val}]",
                    line=dict(width=3, color=color),
                    hovertemplate=f"<b>Q{q_item['order_num']}</b><br>Nota ENEM: %{{x:.0f}}<br>P(Acerto): %{{y:.2%}}<extra></extra>"
                ))
            
            fig_cci.update_layout(
                title="Curvas Características dos Itens (CCI - Escala ENEM)",
                xaxis_title="Proficiência (Régua ENEM de 300 a 900)",
                yaxis_title="Probabilidade de Acerto P(θ)",
                yaxis=dict(range=[0, 1.05], tickformat=".0%"),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            st.plotly_chart(fig_cci, use_container_width=True)

    # =========================================================================
    # TAXA DE ACERTO E DISTRATORES POR QUESTÃO
    # =========================================================================
    if questions_stat:
        with st.expander("🔍 Análise Pedagógica: Taxa de Acertos e Distratores", expanded=False):
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                df_q = pd.DataFrame(questions_stat)
                df_q['label'] = [f"Q{q['order_num']} ({q.get('difficulty_level', 'M')})" for q in questions_stat]
                
                bar_colors = []
                for rate in df_q['success_rate']:
                    if rate >= 70:
                        bar_colors.append("#10B981")
                    elif rate >= 40:
                        bar_colors.append("#F59E0B")
                    else:
                        bar_colors.append("#EF4444")

                fig_bar = px.bar(
                    df_q,
                    x="label",
                    y="success_rate",
                    text="success_rate",
                    hover_data=["question_text", "total_answers", "correct_answers"],
                    labels={"label": "Questão", "success_rate": "% Acertos"},
                    title="% de Acertos Reais por Questão"
                )
                fig_bar.update_traces(marker_color=bar_colors, texttemplate='%{text:.1f}%', textposition='outside')
                fig_bar.update_layout(
                    yaxis=dict(range=[0, 110]),
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=320,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_b2:
                if options_breakdown:
                    st.markdown("**Alternativas mais marcadas:**")
                    df_opts = pd.DataFrame(options_breakdown)
                    for q_stat in questions_stat:
                        q_id = q_stat['question_id']
                        subset = df_opts[df_opts['question_id'] == q_id]
                        if not subset.empty:
                            st.caption(f"**Q{q_stat['order_num']}:** {q_stat['question_text'][:70]}...")
                            for _, opt in subset.iterrows():
                                tag = " (Gabarito)" if opt['is_correct'] else ""
                                st.write(f"- {opt['option_text']}{tag}: **{opt['pick_count']} escolha(s)**")
                            st.markdown("---")

    # =========================================================================
    # TABELA DE RANKING E CLASSIFICAÇÃO COM TRI
    # =========================================================================
    st.subheader("Ranking Geral da Turma (Classificação por Nota TRI)")
    
    # Preparar DataFrame com classificação
    df_display = df_subs.copy()
    
    ranking_col = [f"{i+1}º Lugar" for i in range(len(df_display))]
    df_display.insert(0, "Classificação", ranking_col)
    
    # Formatação de colunas para exibição limpa
    df_display['Código PIN'] = df_display['student_pin'].fillna("-")
    df_display['Nota TRI (ENEM)'] = df_display['tri_score'].apply(lambda x: f"{x:.1f}")
    df_display['Proficiência (θ)'] = df_display['theta'].apply(lambda x: f"{x:+.2f} DP")
    df_display['Aproveitamento'] = df_display['percentage'].apply(lambda x: f"{x:.1f}%")
    df_display['Pontos Clássicos'] = df_display.apply(lambda r: f"{r['score']:.1f} / {r['total_points']:.1f}", axis=1)

    df_display = df_display.rename(columns={
        "student_name": "Nome / Identificação",
        "coherence_label": "Coerência Pedagógica",
        "submitted_at": "Data/Hora"
    })
    
    cols_to_show = [
        "Classificação", "Código PIN", "Nome / Identificação", "Nota TRI (ENEM)",
        "Proficiência (θ)", "Coerência Pedagógica", "Pontos Clássicos", "Aproveitamento", "Data/Hora"
    ]
    
    st.dataframe(
        df_display[cols_to_show],
        use_container_width=True,
        hide_index=True
    )

    # Botão de Exportação CSV com todos os dados da TRI
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Baixar Relatório Psicométrico Completo em CSV (Excel)",
        data=csv_data,
        file_name=f"relatorio_tri_enem_{quiz_info.get('quiz_code', 'quiz')}.csv",
        mime="text/csv",
        use_container_width=True
    )

