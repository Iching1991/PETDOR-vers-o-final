"""
📥 Página de Login - PETDOR

Responsável por:
- Receber email e senha
- Autenticar o usuário (módulo auth.user)
- Salvar dados da sessão
- Redirecionar automaticamente para a página de avaliação de dor
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import autenticar_usuario
from config import APP_CONFIG

# Configuração da página
st.set_page_config(
    page_title="Login - PETDOR",
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
            Entre com sua conta no PETDOR
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de login
    with st.form("login_form"):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        """, unsafe_allow_html=True)

        email = st.text_input(
            "📧 E-mail",
            placeholder="seu@email.com",
            help="O e-mail será convertido para minúsculas automaticamente"
        )

        senha = st.text_input(
            "🔒 Senha",
            type="password",
            placeholder="••••••••"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🔐 Entrar",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        # Normaliza o e-mail (lower-case) antes de enviar ao backend
        email_normalizado = email.strip().lower()

        # Autentica o usuário
        sucesso, mensagem, usuario_id = autenticar_usuario(email_normalizado, senha)

        if sucesso:
            # Salva informações da sessão
            st.session_state['usuario_id'] = usuario_id
            st.session_state['logado'] = True

            st.success(mensagem)
            st.balloons()

            # Aguarda 1 segundo para o usuário ver a mensagem
            import time
            time.sleep(1)

            # Redireciona para a página de avaliação
            try:
                # Streamlit >= 1.22
                st.switch_page("pages/avaliacao.py")
            except AttributeError:
                # Versões anteriores
                st.session_state['redirect_to_avaliacao'] = True
                st.rerun()
        else:
            st.error(mensagem)

    # Links adicionais
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <a href="/cadastro" target="_self">
            <button style="background: #2196F3; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                📝 Criar Conta
            </button>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href="/esqueci_senha" target="_self">
            <button style="background: #FF9800; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                🔑 Esqueci a Senha
            </button>
        </a>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

