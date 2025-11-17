"""
🔄 Página de Redefinição de Senha
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.password_reset import validar_token_reset, redefinir_senha, marcar_token_usado
from utils.validators import validar_senha, senhas_conferem

# Configuração da página
st.set_page_config(
    page_title="Redefinir Senha - PETDor",
    page_icon="🔄",
    layout="centered"
)


def main():
    """Renderiza a página de redefinição de senha"""

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">🔄 Redefinir Senha</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Crie uma nova senha para sua conta
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Pega token da URL
    query_params = st.query_params
    token = query_params.get("token", None)

    if not token:
        st.error("""
        ❌ **Token não encontrado**

        Este link não é válido. Por favor, solicite um novo link de recuperação de senha.
        """)

        if st.button("🔑 Solicitar novo link", use_container_width=True, type="primary"):
            st.switch_page("pages/recuperar_senha.py")

        if st.button("🏠 Voltar para Home", use_container_width=True):
            st.switch_page("app.py")

        return

    # Valida token
    valido, usuario_id, mensagem = validar_token_reset(token)

    if not valido:
        st.error(f"""
        ❌ **{mensagem}**

        Este link pode estar expirado ou já ter sido utilizado.
        Solicite um novo link de recuperação.
        """)

        if st.button("🔑 Solicitar novo link", use_container_width=True, type="primary"):
            st.switch_page("pages/recuperar_senha.py")

        if st.button("🏠 Voltar para Home", use_container_width=True):
            st.switch_page("app.py")

        return

    # Token válido - exibe formulário
    st.success("✅ Token válido! Defina sua nova senha abaixo.")

    # Formulário de redefinição
    with st.form("reset_senha
