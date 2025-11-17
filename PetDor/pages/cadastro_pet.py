"""
➕ Página de Cadastro de Pet - PETDor
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
from config import APP_CONFIG

st.set_page_config(
    page_title="Cadastrar Pet - " + APP_CONFIG["titulo"],
    page_icon="➕",
    layout="centered"
)


def cadastrar_pet_db(tutor_id, nome, especie, raca, idade, peso):
    """
    Função para cadastrar um novo pet no banco de dados.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pets (tutor_id, nome, especie, raca, idade, peso)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tutor_id, nome, especie, raca, idade, peso))

        conn.commit()
        conn.close()
        return True, "Pet cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar pet: {e}"


def main():
    """Renderiza a página de cadastro de pet"""

    # Verifica se o usuário está logado
    if 'usuario_id' not in st.session_state:
        st.warning("Você precisa estar logado para cadastrar um pet.")
        st.info("Faça login ou crie uma conta para continuar.")
        st.markdown("""
        <a href="/login" target="_self">
            <button style="background: #4CAF50; color: white; padding: 12px 24px; 
                           border: none; border-radius: 8px; font-size: 16px; 
                           cursor: pointer; width: 100%; margin-top: 1rem;">
                🔐 Ir para Login
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.stop() # Para a execução da página se não estiver logado

    usuario_id = st.session_state['usuario_id']
    usuario_data = buscar_usuario_por_id(usuario_id)
    nome_tutor = usuario_data['nome'] if usuario_data else "Tutor"

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">➕ Cadastrar Novo Pet</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Olá, {nome_tutor}! Registre aqui os dados do seu pet.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("cadastro_pet_form"):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        """, unsafe_allow_html=True)

        nome_pet = st.text_input("Nome do Pet", placeholder="Ex: Rex")
        especie = st.selectbox("Espécie", ["Cão", "Gato", "Outro"], help="Selecione a espécie do seu pet")
        raca = st.text_input("Raça (opcional)", placeholder="Ex: Labrador")
        idade = st.number_input("Idade (anos)", min_value=0, max_value=30, value=0, help="Idade aproximada do pet")
        peso = st.number_input("Peso (kg)", min_value=0.1, max_value=100.0, value=5.0, step=0.1, help="Peso do pet em quilogramas")

        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "💾 Cadastrar Pet",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if not nome_pet or not especie:
            st.error("Por favor, preencha o nome e a espécie do pet.")
        else:
            sucesso, mensagem = cadastrar_pet_db(usuario_id, nome_pet.strip().title(), especie, raca.strip().title(), idade, peso)
            if sucesso:
                st.success(mensagem)
                st.balloons()
                # Redireciona para a página de avaliação após o cadastro
                import time
                time.sleep(1)
                st.switch_page("pages/avaliacao.py")
            else:
                st.error(mensagem)

if __name__ == "__main__":
    main()
