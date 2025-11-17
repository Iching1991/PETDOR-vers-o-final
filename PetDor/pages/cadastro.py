"""
📝 Página de Cadastro
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import cadastrar_usuario

# Configuração da página
st.set_page_config(
    page_title="Cadastro - PETDor",
    page_icon="📝",
    layout="centered"
)


def formatar_nome(nome):
    """
    Formata o nome com a primeira letra de cada palavra em maiúscula
    e as demais em minúscula (Title Case)

    Args:
        nome: Nome a ser formatado

    Returns:
        Nome formatado
    """
    if not nome:
        return ""

    # Remove espaços extras e converte para Title Case
    nome_limpo = " ".join(nome.strip().split())
    return nome_limpo.title()


def formatar_email(email):
    """
    Converte email para minúsculas

    Args:
        email: Email a ser formatado

    Returns:
        Email em minúsculas
    """
    if not email:
        return ""

    return email.strip().lower()


def main():
    """Renderiza a página de cadastro"""

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📝 Cadastro</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Crie sua conta no PETDor
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de cadastro
    with st.form("cadastro_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        """, unsafe_allow_html=True)

        # Nome com formatação automática
        nome = st.text_input(
            "👤 Nome completo",
            placeholder="João Silva",
            help="Digite seu nome completo (será formatado automaticamente)",
            key="nome_input"
        )

        # Email com formatação automática
        email_input = st.text_input(
            "📧 E-mail",
            placeholder="seu@email.com",
            help="Digite um e-mail válido (será convertido para minúsculas)",
            key="email_input"
        )

        # Senha
        senha = st.text_input(
            "🔒 Senha",
            type="password",
            placeholder="••••••••",
            help="Mínimo 6 caracteres"
        )

        confirmar_senha = st.text_input(
            "🔒 Confirmar senha",
            type="password",
            placeholder="••••••••",
            help="Digite a senha novamente"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Exibe valores formatados (visualização)
        if nome or email_input:
            st.markdown("""
            <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; 
                        border-left: 4px solid #3182ce; margin: 1rem 0;">
            """, unsafe_allow_html=True)

            nome_formatado = formatar_nome(nome)
            email_formatado = formatar_email(email_input)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**👤 Nome:** {nome_formatado}")

            with col2:
                st.markdown(f"**📧 E-mail:** {email_formatado}")

            st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            submitted = st.form_submit_button(
                "📝 Cadastrar",
                use_container_width=True,
                type="primary"
            )

        with col2:
            if st.form_submit_button("❌ Limpar", use_container_width=True):
                st.rerun()

    # Processa cadastro
    if submitted:
        if not all([nome, email_input, senha, confirmar_senha]):
            st.error("⚠️ Preencha todos os campos")
        else:
            # Aplica formatação
            nome_final = formatar_nome(nome)
            email_final = formatar_email(email_input)

            with st.spinner("Cadastrando..."):
                sucesso, mensagem = cadastrar_usuario(nome_final, email_final, senha, confirmar_senha)

                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.balloons()
                    st.info("👉 Faça login para acessar o sistema")

                    # Botão para ir ao login
                    if st.button("🔐 Ir para Login", use_container_width=True, type="primary"):
                        st.markdown("""
                        <meta http-equiv="refresh" content="0; url=/login">
                        """, unsafe_allow_html=True)
                        st.info("Redirecionando...")
                else:
                    st.error(f"❌ {mensagem}")

    # Links úteis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <a href="/login" target="_self">
            <button style="background: #2196F3; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                🔐 Já tenho conta
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


if __name__ == "__main__":
    main()

