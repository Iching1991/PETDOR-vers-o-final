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

    # Pega token da URL (compatível com diferentes versões do Streamlit)
    try:
        # Streamlit >= 1.30
        query_params = st.query_params
        token = query_params.get("token", [None])[0] if isinstance(query_params.get("token"), list) else query_params.get("token")
    except AttributeError:
        # Streamlit < 1.30
        query_params = st.experimental_get_query_params()
        token = query_params.get("token", [None])[0]

    if not token:
        st.error("""
        ❌ **Token não encontrado**

        Este link não é válido. Por favor, solicite um novo link de recuperação de senha.
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔑 Solicitar novo link", use_container_width=True, type="primary"):
                st.switch_page("pages/recuperar_senha.py")

        with col2:
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

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔑 Solicitar novo link", use_container_width=True, type="primary"):
                st.switch_page("pages/recuperar_senha.py")

        with col2:
            if st.button("🏠 Voltar para Home", use_container_width=True):
                st.switch_page("app.py")

        return

    # Token válido - exibe formulário
    st.success("✅ Token válido! Defina sua nova senha abaixo.")

    # Formulário de redefinição
    with st.form("reset_senha_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 1rem 0;">
        """, unsafe_allow_html=True)

        st.info("""
        🔒 **Requisitos da senha:**
        - Mínimo de 6 caracteres
        - Recomendado: use letras, números e símbolos
        """)

        nova_senha = st.text_input(
            "🔒 Nova senha",
            type="password",
            placeholder="••••••••",
            help="Digite sua nova senha"
        )

        confirmar_senha = st.text_input(
            "🔒 Confirmar nova senha",
            type="password",
            placeholder="••••••••",
            help="Digite a senha novamente"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🔄 Redefinir Senha",
            use_container_width=True,
            type="primary"
        )

    # Processa redefinição
    if submitted:
        if not nova_senha or not confirmar_senha:
            st.error("⚠️ Preencha todos os campos")
        else:
            # Valida senha
            ok_senha, msg_senha = validar_senha(nova_senha)
            if not ok_senha:
                st.error(f"❌ {msg_senha}")
                return

            # Verifica se senhas conferem
            ok_conf, msg_conf = senhas_conferem(nova_senha, confirmar_senha)
            if not ok_conf:
                st.error(f"❌ {msg_conf}")
                return

            with st.spinner("Redefinindo senha..."):
                # Redefine senha
                sucesso, mensagem_reset = redefinir_senha(usuario_id, nova_senha)

                if sucesso:
                    # Marca token como usado
                    marcar_token_usado(token)

                    st.success(f"""
                    ✅ **{mensagem_reset}**

                    Sua senha foi alterada com sucesso!
                    Agora você pode fazer login com a nova senha.
                    """)

                    st.balloons()

                    # Aguarda um pouco antes de mostrar o botão
                    import time
                    time.sleep(1)

                    # Botão para ir ao login
                    if st.button("🔐 Fazer Login Agora", use_container_width=True, type="primary"):
                        st.switch_page("pages/login.py")
                else:
                    st.error(f"❌ {mensagem_reset}")

    # Links úteis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔐 Fazer Login", use_container_width=True):
            st.switch_page("pages/login.py")

    with col2:
        if st.button("🏠 Voltar para Home", use_container_width=True):
            st.switch_page("app.py")


if __name__ == "__main__":
    main()
