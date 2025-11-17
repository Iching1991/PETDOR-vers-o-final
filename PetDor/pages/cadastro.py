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

        nome = st.text_input(
            "👤 Nome completo",
            placeholder="João Silva",
            help="Digite seu nome completo"
        )

        email = st.text_input(
            "📧 E-mail",
            placeholder="seu@email.com",
            help="Digite um e-mail válido"
        )

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
        if not all([nome, email, senha, confirmar_senha]):
            st.error("⚠️ Preencha todos os campos")
        else:
            with st.spinner("Cadastrando..."):
                sucesso, mensagem = cadastrar_usuario(nome, email, senha, confirmar_senha)

                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.balloons()
                    st.info("👉 Faça login para acessar o sistema")

                    # Botão para ir ao login
                    if st.button("🔐 Ir para Login", use_container_width=True, type="primary"):
                        st.switch_page("pages/login.py")
                else:
                    st.error(f"❌ {mensagem}")

    # Links úteis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔐 Já tenho conta", use_container_width=True):
            st.switch_page("pages/login.py")

    with col2:
        if st.button("🏠 Voltar para Home", use_container_width=True):
            st.switch_page("app.py")


if __name__ == "__main__":
    main()
