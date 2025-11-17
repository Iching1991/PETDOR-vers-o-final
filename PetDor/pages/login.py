"""
📥 Página de Login - PETDor
Responsável por:
- Receber email e senha
- Autenticar o usuário (módulo auth.user)
- Salvar dados da sessão
- Redirecionar automaticamente para a página de avaliação de dor
"""

import sys
from pathlib import Path

# --------------------------------------------------------------
# 1️⃣  Garante que a raiz do projeto esteja no sys.path
# --------------------------------------------------------------
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import autenticar_usuario
from config import APP_CONFIG

# --------------------------------------------------------------
# 2️⃣  Configurações da página (conforme preferência)
# --------------------------------------------------------------
st.set_page_config(
    page_title="Login - " + APP_CONFIG["titulo"],
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Renderiza a tela de login e trata a autenticação"""

    # Header
    st.markdown(
        """
        <div style="text-align:center; padding:2rem ;">
            <h1 style="color:#2d3748;">🔐 Login</h1>
            <p style="color:#718096; font-size:1.1rem;">
                Acesse sua conta para avaliar a dor do seu pet
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Formulário de login
    with st.form("login_form"):
        email = st.text_input(
            "📧 E‑mail",
            placeholder="seu@email.com",
            help="O e‑mail será convertido para minúsculas automaticamente",
        )
        senha = st.text_input(
            "🔒 Senha",
            type="password",
            placeholder="••••••••",
        )
        submitted = st.form_submit_button(
            "Entrar",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        # Normaliza o e‑mail (lower‑case) antes de enviar ao backend
        email_normalizado = email.strip().lower()

        sucesso, mensagem, usuario_id = autenticar_usuario(email_normalizado, senha)

        if sucesso:
            # ------------------------------------------------------
            # 3️⃣  Salva informações da sessão
            # ------------------------------------------------------
            st.session_state["usuario_id"] = usuario_id
            st.session_state["logado"] = True

            st.success(mensagem)

            # ------------------------------------------------------
            # 4️⃣  Redireciona para a página de avaliação
            # ------------------------------------------------------
            # Se estiver usando Streamlit >= 1.22, pode usar `st.switch_page`
            # Caso contrário, usamos `st.experimental_rerun` e mudamos a URL
            try:
                # Streamlit 1.22+ (recomendado)
                st.switch_page("pages/avaliacao.py")
            except AttributeError:
                # Versões anteriores – força recarregamento da aplicação
                # e, na próxima execução, a lógica de redirecionamento
                # no app principal levará o usuário para /avaliacao
                st.experimental_rerun()
        else:
            st.error(mensagem)


if __name__ == "__main__":
    main()
