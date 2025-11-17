"""
🔐 Página de Login
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import autenticar_usuario, buscar_usuario_por_id

# Configuração da página
st.set_page_config(
    page_title="Login - PETDor",
    page_icon="🔐",
    layout="centered"
)


def main():
    """Renderiza a página de login"""

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">🔐 Login</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Acesse sua conta PETDor
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de login
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        """, unsafe_allow_html=True)

        email = st.text_input(
            "📧 E-mail",
            placeholder="seu@email.com",
            help="Digite o e-mail cadastrado"
        )

        senha = st.text_input(
            "🔒 Senha",
            type="password",
            placeholder="••••••••",
            help="Digite sua senha"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            submitted = st.form_submit_button(
                "🔐 Entrar",
                use_container_width=True,
                type="primary"
            )

        with col2:
            if st.form_submit_button("❌ Limpar", use_container_width=True):
                st.experimental_rerun()

    # Processa login
    if submitted:
        if not email or not senha:
            st.error("⚠️ Preencha todos os campos")
        else:
            with st.spinner("Autenticando..."):
                sucesso, mensagem, usuario_id = autenticar_usuario(email, senha)

                if sucesso:
                    # Salva dados na sessão
                    st.session_state['usuario_id'] = usuario_id
                    st.session_state['email'] = email

                    # Busca dados completos do usuário
                    usuario_data = buscar_usuario_por_id(usuario_id)

                    if usuario_data:
                        st.session_state['nome'] = usuario_data['nome']
                        st.session_state['is_admin'] = usuario_data.get('is_admin', False)

                    st.success(f"✅ {mensagem}")
                    st.balloons()

                    # Redireciona para home
                    st.markdown("""
                    <meta http-equiv="refresh" content="1; url=/">
                    """, unsafe_allow_html=True)
                    st.info("Redirecionando para o sistema...")
                else:
                    st.error(f"❌ {mensagem}")

    # Links úteis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <a href="/cadastro" target="_self">
            <button style="background: #4CAF50; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                📝 Criar conta
            </button>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href="/recuperar_senha" target="_self">
            <button style="background: #FF9800; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                🔑 Esqueci a senha
            </button>
        </a>
        """, unsafe_allow_html=True)

    # Voltar para home
    st.markdown("<br>", unsafe_allow_html=True)

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
