"""
🔑 Página de Recuperação de Senha
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.password_reset import criar_token_reset, buscar_usuario_por_email
from utils.email_sender import enviar_email_reset

# Configuração da página
st.set_page_config(
    page_title="Recuperar Senha - PETDor",
    page_icon="🔑",
    layout="centered"
)


def main():
    """Renderiza a página de recuperação de senha"""

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">🔑 Recuperar Senha</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Enviaremos um link para redefinir sua senha
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de recuperação
    with st.form("recuperar_senha_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        """, unsafe_allow_html=True)

        st.info("""
        📧 **Como funciona:**
        1. Digite seu e-mail cadastrado
        2. Clique em "Enviar Link"
        3. Verifique sua caixa de entrada
        4. Clique no link recebido para redefinir sua senha

        ⏱️ O link expira em 1 hora por segurança.
        """)

        email = st.text_input(
            "📧 E-mail cadastrado",
            placeholder="seu@email.com",
            help="Digite o e-mail usado no cadastro"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            submitted = st.form_submit_button(
                "📧 Enviar Link",
                use_container_width=True,
                type="primary"
            )

        with col2:
            if st.form_submit_button("❌ Limpar", use_container_width=True):
                st.experimental_rerun()

    # Processa recuperação
    if submitted:
        if not email:
            st.error("⚠️ Digite seu e-mail")
        else:
            with st.spinner("Processando..."):
                # Verifica se o email existe
                usuario = buscar_usuario_por_email(email)

                if not usuario:
                    # Por segurança, não informamos se o email existe ou não
                    st.success("""
                    ✅ **Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha.**

                    📧 Verifique sua caixa de entrada (e spam) nos próximos minutos.
                    """)
                else:
                    # Gera token
                    sucesso_token, token = criar_token_reset(usuario['id'])

                    if sucesso_token:
                        # Envia email
                        sucesso_email, mensagem_email = enviar_email_reset(email, token)

                        if sucesso_email:
                            st.success("""
                            ✅ **Link de recuperação enviado com sucesso!**

                            📧 Verifique sua caixa de entrada (e spam).

                            ⏱️ O link expira em 1 hora.
                            """)

                            st.info(f"📨 {mensagem_email}")
                        else:
                            st.error(f"❌ Erro ao enviar e-mail: {mensagem_email}")
                    else:
                        st.error("❌ Erro ao gerar token de recuperação")

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
        <a href="/cadastro" target="_self">
            <button style="background: #4CAF50; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                📝 Criar Conta
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
