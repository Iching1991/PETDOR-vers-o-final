"""
📝 Página de Avaliação de Dor - Design Wellness
Integra sistema modular de espécies (especies/)
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json
import os

# Importa sistema modular de espécies
from especies import get_especies_nomes, get_especie_config
from database.models import salvar_avaliacao
from utils.pdf_generator import gerar_relatorio_pdf
from config import get_nivel_dor


def render_avaliacao_page(usuario):
    """Renderiza página de avaliação com design wellness"""

    # Header
    st.markdown("""
    <div class="wellness-card" style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📝 Nova Avaliação</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Avalie o bem-estar do seu paciente com precisão científica
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Dados do paciente
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">🐾 Dados do Paciente</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        nome_pet = st.text_input(
            "🐕 Nome do Paciente",
            placeholder="Ex: Rex, Luna, Max...",
            help="Nome do animal a ser avaliado"
        )

    with col2:
        especies = get_especies_nomes()
        especie = st.selectbox(
            "🦴 Espécie",
            especies,
            help="Selecione a espécie do paciente"
        )

    with col3:
        idade = st.number_input(
            "📅 Idade (anos)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
            help="Idade aproximada do animal"
        )

    if not nome_pet.strip():
        st.info("👆 Preencha o nome do paciente para continuar")
        return

    try:
        config = get_especie_config(especie)
    except KeyError:
        st.error(f"❌ Configuração para '{especie}' não encontrada.")
        return

    # Instruções da espécie
    st.markdown(f"""
    <div class="wellness-card">
        <h4 style="color: #2d3748; margin-bottom: 1rem;">📋 Instruções para {especie}</h4>
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC);
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <strong>Escala:</strong> {config.escala_min} a {config.escala_max} |
            <strong>Perguntas:</strong> {len(config.perguntas)} |
            <strong>Tempo:</strong> ~5 minutos
        </div>
        <p style="color: #4a5568; line-height: 1.6;">
            {config.descricao}<br><br>
            <strong>Dicas importantes:</strong><br>
            • Avalie o comportamento nas últimas 24–48 horas<br>
            • Compare com o comportamento normal do paciente<br>
            • Seja objetivo e honesto nas respostas<br>
            • Em caso de dúvida, consulte literatura especializada
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Labels da escala
    labels_escala = config.get_labels_escala()

    with st.expander("📊 Legenda da Escala"):
        st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;'>",
                    unsafe_allow_html=True)

        for valor, label in labels_escala.items():
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;
                       background: rgba(174, 227, 255, 0.3);
                       border-radius: 8px; border: 1px solid #AEE3FF;">
                <strong style="font-size: 1.2rem; color: #2d3748;">{valor}</strong><br>
                <span style="color: #4a5568; font-size: 0.9rem;">{label}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Questionário
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">🩺 Questionário de Avaliação</h3>
    </div>
    """, unsafe_allow_html=True)

    progress_bar = st.progress(0)
    progress_text = st.empty()

    respostas = []
    pontuacao_total = 0

    for idx, pergunta in enumerate(config.perguntas, 1):
        progresso = idx / len(config.perguntas)
        progress_bar.progress(progresso)
        progress_text.text(f"Avaliação: Pergunta {idx} de {len(config.perguntas)}")

        st.markdown(f"""
        <div class="wellness-card" style="margin-bottom: 1.5rem; padding: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC);
                           width: 40px; height: 40px; border-radius: 50%;
                           display: flex; align-items: center; justify-content: center;
                           margin-right: 1rem; font-weight: bold; color: #2d3748;">
                    {idx}
                </div>
                <h4 style="color: #2d3748; margin: 0;">{pergunta.texto}</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)

        resposta = st.slider(
            label="",
            min_value=config.escala_min,
            max_value=config.escala_max,
            value=config.escala_min,
            step=1,
            key=f"pergunta_{idx}_{nome_pet}_{especie}"
        )

        label_resposta = labels_escala.get(resposta, str(resposta))

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.caption(f"Selecionado: **{label_resposta}**")

        with col_b:
            if resposta <= 1:
                st.markdown("🟢")
            elif resposta <= 3:
                st.markdown("🟡")
            else:
                st.markdown("🟠")

        # Cálculo
        pontos = (config.escala_max - resposta) if pergunta.invertida else resposta
        respostas.append(resposta)
        pontuacao_total += pontos

        if idx < len(config.perguntas):
            st.markdown("---")

    progress_bar.empty()
    progress_text.empty()

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([3, 1])

    # Botão calcular
    with col_btn1:
        if st.button("🔍 Calcular Avaliação", use_container_width=True):

            pontuacao_maxima = config.get_pontuacao_maxima()
            percentual = config.calcular_percentual(pontuacao_total)
            nivel = get_nivel_dor(percentual)

            # Resultado principal
            cor_nivel = "#28a745" if percentual < 30 else "#ffc107" if percentual < 60 else "#dc3545"

            st.markdown(f"""
            <div style="background: {cor_nivel};
                       color: white; border-radius: 20px; padding: 2rem;
                       text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{percentual:.1f}%</div>
                <h3>Nível de Dor Estimado</h3>
                <p>{nome_pet} • {especie} • {idade} anos</p>
                <div style="font-size: 1.2rem; font-weight: 600;">
                    {pontuacao_total}/{pontuacao_maxima} pontos
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Recomendação
            st.markdown(f"""
            <div class="wellness-card" style="margin: 2rem 0;">
                <h4 style="color: #2d3748; margin-bottom: 1rem;">💡 Recomendação Clínica</h4>
                <div style="padding: 1rem; background: rgba(199, 249, 204, 0.3);
                           border-radius: 10px; border-left: 4px solid #28a745;">
                    <p style="color: #2d3748; margin: 0;">
                        {nivel["texto"]}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Salvar no banco
            sucesso, msg = salvar_avaliacao(
                usuario['id'], nome_pet, especie,
                respostas, pontuacao_total,
                pontuacao_maxima, percentual
            )

            if sucesso:
                st.success("✅ Avaliação salva no histórico!")
                st.balloons()
            else:
                st.error(f"❌ Erro ao salvar: {msg}")

            # PDF
            try:
                pdf_path = gerar_relatorio_pdf(
                    pet_nome=nome_pet,
                    especie=especie,
                    percentual=percentual,
                    pontuacao_total=pontuacao_total,
                    pontuacao_maxima=pontuacao_maxima,
                    usuario_nome=usuario['nome'],
                    idade=idade
                )

                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Baixar Relatório PDF",
                        data=pdf_file.read(),
                        file_name=f"petdor_{nome_pet}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                os.unlink(pdf_path)

            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

    # Voltar ao início
    with col_btn2:
        if st.button("← Voltar ao Início", use_container_width=True):
            st.session_state["menu"] = "🏠 Início"
            st.rerun()
