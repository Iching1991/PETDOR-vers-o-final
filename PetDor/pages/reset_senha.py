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
    st.title("🔄 Redefinir Senha")
    st.markdown("Crie uma nova senha para sua conta")
    st.markdown("---")

    # Pega token da URL
    token = None
    try:
        # Tenta pegar do query_params (Streamlit >= 1.30)
        params = dict(st.query_params)
        token = params.get("token")
    except:
        try:
            # Fallback para versão antiga
            params = st.experimental_get_query_params()
            token = params.get("token", [None])[0]
        except:
            pass

    if not token:
        st.error("""
        ❌ **Token não encontrado**

        Este link não é válido. Por favor, solicite um novo link de recuperação de senha.
        """)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔑 Solicitar novo link", use_container_width=True, type="primary"):
                st.markdown("""
                <meta http-equiv="refresh" content="0; url=/recuperar_senha">
                """, unsafe_allow_html=True)
                st.info("Redirecionando...")

        with col2:
            if st.button("🏠 Voltar para Home", use_container_width=True):
                st.markdown("""
                <meta http-equiv="refresh" content="0; url=/">
                """, unsafe_allow_html=True)
                st.info("Redirecionando...")

        return

    # Valida token
    valido, usuario_id, mensagem = validar_token_reset(token)

    if not valido:
        st.error(f"""
        ❌ **{mensagem}**

        Este link pode estar expirado ou já ter sido utilizado.
        Solicite um novo link de recuperação.
        """)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔑 Solicitar novo link", use_container_width=True, type="primary"):
                st.markdown("""
                <meta http-equiv="refresh" content="0; url=/recuperar_senha">
                """, unsafe_allow_html=True)
                st.info("Redirecionando...")

        with col2:
            if st.button("🏠 Voltar para Home", use_container_width=True):
                st.markdown("""
                <meta http-equiv="refresh" content="0; url=/">
                """, unsafe_allow_html=True)
                st.info("Redirecionando...")

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

                    # Link para login
                    st.markdown("---")
                    st.markdown("""
                    <div style="text-align: center; padding: 1rem;">
                        <a href="/login" target="_self">
                            <button style="background: #4CAF50; color: white; padding: 12px 24px; 
                                           border: none; border-radius: 8px; font-size: 16px; 
                                           cursor: pointer; width: 100%;">
                                🔐 Fazer Login Agora
                            </button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ {mensagem_reset}")

    # Links úteis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <a href="/login" target="_self">
            <button style="background: #2196F3; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                🔐 Fazer Login
            </button>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href="/" target="_self">
            <button style="background: #607D8B; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                🏠 Voltar para Home
            </button>
        </a>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
