"""
📊 Página de Histórico de Avaliações de Dor do Pet - PETDOR

Responsável por:
- Exibir o histórico de avaliações de dor de todos os pets do tutor logado.
- Permitir exibição detalhada de cada avaliação.
- Permitir exclusão de avaliações.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Ajusta o path raiz do projeto
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import buscar_usuario_por_id
from database.models import (
    buscar_avaliacoes_usuario,
    deletar_avaliacao,
    buscar_avaliacao_por_id,
    buscar_respostas_avaliacao
)
from config import APP_CONFIG


# Configurações da página
st.set_page_config(
    page_title="Histórico - " + APP_CONFIG["titulo"],
    page_icon="📊",
    layout="centered"
)


# ---------------------------------------------------------
# Função para exibir os detalhes da avaliação
# ---------------------------------------------------------
def exibir_detalhes_avaliacao(avaliacao_id: int):
    """Exibe os detalhes de uma avaliação específica."""
    avaliacao = buscar_avaliacao_por_id(avaliacao_id)

    if not avaliacao:
        st.error("Avaliação não encontrada.")
        return

    # Trata data no formato ISO
    data_raw = avaliacao.get("data_avaliacao", "")
    data_formatada = data_raw.replace("T", " ")[:16] if "T" in data_raw else data_raw

    st.subheader(
        f"Detalhes da Avaliação de {avaliacao['pet_nome']} "
        f"em {data_formatada.split(' ')[0]}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Nível de Dor Registrado", f"{avaliacao['percentual_dor']}%")
        st.write(f"**Pet:** {avaliacao['pet_nome']} ({avaliacao['pet_especie']})")
        st.write(f"**Data:** {data_formatada}")

    with col2:
        st.write(f"**Raça:** {avaliacao['pet_raca'] or 'Não informada'}")
        st.write(f"**Nascimento:** {avaliacao['pet_data_nascimento'] or 'Não informado'}")
        st.write(f"**Sexo:** {avaliacao['pet_sexo'] or 'Não informado'}")
        st.write(f"**Peso:** {avaliacao['pet_peso']} kg" if avaliacao['pet_peso'] else "Peso não informado")

    if avaliacao.get("observacoes"):
        st.markdown(f"**Observações:** {avaliacao['observacoes']}")
    else:
        st.info("Nenhuma observação registrada.")

    # Exibir respostas das perguntas
    respostas = buscar_respostas_avaliacao(avaliacao_id)
    if respostas:
        st.markdown("---")
        st.markdown("#### Respostas Detalhadas")
        for r in respostas:
            pergunta = r.get("pergunta_id", "").replace("_", " ").capitalize()
            resposta = r.get("resposta", "Não informado")
            st.write(f"- **{pergunta}:** {resposta}")
    else:
        st.info("Nenhuma resposta detalhada encontrada.")

    # Botão deletar
    st.markdown("---")
    if st.button(
        f"🗑️ Deletar Avaliação de {avaliacao['pet_nome']}",
        key=f"del_{avaliacao_id}",
        type="secondary"
    ):
        if deletar_avaliacao(avaliacao_id):
            st.success("Avaliação deletada com sucesso!")
            st.rerun()
        else:
            st.error("Erro ao deletar avaliação.")


# ---------------------------------------------------------
# Página principal
# ---------------------------------------------------------
def main():

    # Verifica login
    if 'usuario_id' not in st.session_state:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.markdown("""
        <a href="/login" target="_self">
            <button style="
                background:#4CAF50;color:white;
                padding:12px 24px;border:none;
                border-radius:8px;font-size:16px;
                cursor:pointer;width:100%;margin-top:1rem;">
                🔐 Ir para Login
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.stop()

    usuario_id = st.session_state['usuario_id']
    usuario_data = buscar_usuario_por_id(usuario_id)
    nome_usuario = usuario_data['nome'] if usuario_data else "Usuário"

    # Cabeçalho
    st.markdown(f"""
    <div style="text-align:center; padding:2rem 1rem;">
        <h1 style="color:#2d3748; margin-bottom:0.5rem;">📊 Histórico de Avaliações</h1>
        <p style="color:#718096; font-size:1.1rem;">
            Olá, {nome_usuario}! Aqui estão todas as avaliações de dor dos seus pets.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Busca avaliações
    avaliacoes = buscar_avaliacoes_usuario(usuario_id)

    if not avaliacoes:
        st.info("Você ainda não possui avaliações registradas.")
        st.markdown("""
        <a href="/avaliacao" target="_self">
            <button style="
                background:#2196F3;color:white;
                padding:12px 24px;border:none;
                border-radius:8px;font-size:16px;
                cursor:pointer;width:100%;margin-top:1rem;">
                📋 Fazer Nova Avaliação
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.stop()

    # Lista de avaliações
    st.markdown("### Suas Últimas Avaliações")

    for avaliacao in avaliacoes:
        data_raw = avaliacao["data_avaliacao"]
        data_fmt = data_raw.split("T")[0] if "T" in data_raw else data_raw

        with st.expander(
            f"**{avaliacao['pet_nome']}** ({avaliacao['pet_especie']}) - "
            f"{data_fmt} - Dor: **{avaliacao['percentual_dor']}%**"
        ):
            exibir_detalhes_avaliacao(avaliacao["avaliacao_id"])


# ---------------------------------------------------------
# Execução
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
