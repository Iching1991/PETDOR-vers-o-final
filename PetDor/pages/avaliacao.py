"""
📋 Página de Avaliação de Dor do Pet - PETDor

Responsável por:
- Exibir formulário de avaliação de dor para um pet selecionado.
- Listar pets do tutor logado.
- Redirecionar para cadastro de pet se nenhum for encontrado.
- Salvar a avaliação no banco de dados.
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

# Configuração da página (apenas uma vez, no nível superior)
st.set_page_config(
    page_title="Avaliar Pet - " + APP_CONFIG["titulo"],
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
        # Garante que os dados são acessados corretamente, seja por nome ou índice
        pets.append({
            "id": row["id"] if isinstance(row, dict) else row[0],
            "nome": row["nome"] if isinstance(row, dict) else row[1],
            "especie": row["especie"] if isinstance(row, dict) else row[2],
        })
    return pets


def salvar_avaliacao(pet_id, usuario_id, percentual_dor, observacoes):
    """Salva avaliação no banco de dados."""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes)
            VALUES (?, ?, ?, ?)
        """, (pet_id, usuario_id, percentual_dor, observacoes))

        conn.commit()
        conn.close()
        return True, "Avaliação salva com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar avaliação: {e}"


def main():
    """Renderiza a página de avaliação de dor"""

    # 1. Verifica se o usuário está logado
    if 'usuario_id' not in st.session_state:
        st.warning("Você precisa estar logado para acessar esta página.")
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
    nome_usuario = usuario_data['nome'] if usuario_data else "Usuário"

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📋 Avaliar Dor do Pet</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Olá, {nome_usuario}! Selecione um pet e registre sua avaliação.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Lista pets do tutor
    pets_do_tutor = listar_pets_do_tutor(usuario_id)

    if not pets_do_tutor:
        st.info("Você ainda não tem pets cadastrados. Cadastre um para começar a avaliar!")
        st.markdown("""
        <a href="/cadastro_pet" target="_self">
            <button style="background: #2196F3; color: white; padding: 12px 24px; 
                           border: none; border-radius: 8px; font-size: 16px; 
                           cursor: pointer; width: 100%; margin-top: 1rem;">
                ➕ Cadastrar Novo Pet
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.stop() # Para a execução se não houver pets

    # 3. Seleção do pet para avaliação
    st.markdown("---")
    st.subheader("Selecione o Pet para Avaliar")

    # Cria uma lista de strings para o selectbox, mostrando nome e espécie
    nomes_pets_formatados = [f"{pet['nome']} ({pet['especie']})" for pet in pets_do_tutor]

    escolha_pet_str = st.selectbox(
        "Escolha um pet",
        options=nomes_pets_formatados,
        help="Selecione o pet que você deseja avaliar."
    )

    # Encontra o objeto pet completo a partir da escolha do selectbox
    pet_escolhido = next((pet for pet in pets_do_tutor if f"{pet['nome']} ({pet['especie']})" == escolha_pet_str), None)

    if not pet_escolhido:
        st.warning("Nenhum pet selecionado ou encontrado. Por favor, selecione um pet.")
        st.stop()

    st.write(f"Você está avaliando: **{pet_escolhido['nome']}** (Espécie: {pet_escolhido['especie']})")

    # 4. Formulário de avaliação de dor
    st.markdown("### 🩺 Nível de Dor")
    with st.form("avaliacao_dor_form"):
        percentual_dor = st.slider(
            "Intensidade da dor (0% = sem dor, 100% = dor máxima)",
            min_value=0, max_value=100, value=0, step=5,
            help="Arraste para indicar o nível de dor percebido no pet."
        )

        observacoes = st.text_area(
            "📝 Observações (opcional)",
            placeholder="Descreva sinais de dor, comportamento, medicamentos em uso, etc.",
            height=150
        )

        submitted = st.form_submit_button(
            "💾 Salvar Avaliação",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        sucesso, mensagem = salvar_avaliacao(
            pet_id=pet_escolhido["id"],
            usuario_id=usuario_id,
            percentual_dor=percentual_dor,
            observacoes=observacoes,
        )
        if sucesso:
            st.success(mensagem)
            st.balloons()
            # Opcional: redirecionar para o histórico ou recarregar a página
            # st.rerun()
        else:
            st.error(mensagem)


if __name__ == "__main__":
    main()
