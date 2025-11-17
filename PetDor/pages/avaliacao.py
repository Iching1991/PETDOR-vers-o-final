"""
📋 Pagina de Avaliacao de Dor do Pet
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import buscar_usuario_por_id
from database.connection import conectar_db


st.set_page_config(
    page_title="Avaliar Pet - PETDor",
    page_icon="📋",
    layout="centered"
)


def listar_pets_do_tutor(usuario_id):
    """Lista pets cadastrados pelo tutor (usuario_id)."""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, especie
        FROM pets
        WHERE tutor_id = ?
        ORDER BY nome
    """, (usuario_id,))
    rows = cursor.fetchall()
    conn.close()

    pets = []
    for row in rows:
        pets.append({
            "id": row["id"] if isinstance(row, dict) else row[0],
            "nome": row["nome"] if isinstance(row, dict) else row[1],
            "especie": row["especie"] if isinstance(row, dict) else row[2],
        })
    return pets


def salvar_avaliacao(pet_id, usuario_id, percentual_dor, observacoes):
    """Salva avaliacao no banco."""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes)
        VALUES (?, ?, ?, ?)
    """, (pet_id, usuario_id, percentual_dor, observacoes))

    conn.commit()
    conn.close()


def main():
    # Verifica se usuario esta logado
    if "usuario_id" not in st.session_state:
        st.error("Voce precisa estar logado para avaliar um pet.")
        st.markdown(
            '<a href="/login" target="_self"><button style="background:#4CAF50;'
            'color:white;padding:10px 20px;border:none;border-radius:8px;'
            'cursor:pointer;">🔐 Ir para Login</button></a>',
            unsafe_allow_html=True,
        )
        return

    usuario = buscar_usuario_por_id(st.session_state["usuario_id"])

    st.markdown(
        f"""
        <div style="text-align:center; padding: 1.5rem 1rem;">
            <h1 style="color:#2d3748;">📋 Avaliar Dor do Pet</h1>
            <p style="color:#718096;">Usuario: <strong>{usuario['nome']}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Se for tutor, lista pets dele
    pets = listar_pets_do_tutor(st.session_state["usuario_id"])

    if not pets:
        st.warning("Voce ainda nao cadastrou nenhum pet.")
        st.markdown(
            '<a href="/cadastro_pet" target="_self"><button style="background:#2196F3;'
            'color:white;padding:10px 20px;border:none;border-radius:8px;cursor:pointer;">'
            '➕ Cadastrar Pet</button></a>',
            unsafe_allow_html=True,
        )
        return

    nomes_pets = [f"{p['nome']} ({p['especie']})" for p in pets]
    escolha = st.selectbox("Selecione o pet para avaliar", nomes_pets)
    pet_escolhido = pets[nomes_pets.index(escolha)]

    st.markdown("### 🩺 Nível de dor")
    percentual_dor = st.slider(
        "Intensidade da dor (0% = sem dor, 100% = dor maxima)",
        min_value=0, max_value=100, value=0, step=5,
    )

    observacoes = st.text_area(
        "📝 Observacoes (opcional)",
        placeholder="Descreva sinais de dor, comportamento, medicamentos em uso, etc."
    )

    if st.button("💾 Salvar Avaliacao", use_container_width=True):
        salvar_avaliacao(
            pet_id=pet_escolhido["id"],
            usuario_id=st.session_state["usuario_id"],
            percentual_dor=percentual_dor,
            observacoes=observacoes,
        )
        st.success("Avaliacao salva com sucesso!")
        st.balloons()


if __name__ == "__main__":
    main()
