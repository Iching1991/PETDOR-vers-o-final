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


def formatar_nome(nome: str) -> str:
    """Formata o nome em Title Case (primeira letra maiúscula, resto minúsculo)."""
    if not nome:
        return ""
    return " ".join(nome.strip().split()).title()


def formatar_email(email: str) -> str:
    """Converte e-mail para minúsculas e remove espaços extras."""
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

    # Inicializa session_state para formatação
    if "nome_val" not in st.session_state:
        st.session_state.nome_val = ""
    if "email_val" not in st.session_state:
        st.session_state.email_val = ""
    if "nome_dirty" not in st.session_state:
        st.session_state.nome_dirty = False
    if "email_dirty" not in st.session_state:
        st.session_state.email_dirty = False

    # Callbacks para formatação
    def on_change_nome():
        st.session_state.nome_dirty = True
        st.session_state.nome_val = formatar_nome(st.session_state.nome_input)

    def on_change_email():
        st.session_state.email_dirty = True
        st.session_state.email_val = formatar_email(st.session_state.email_input)

    # Formulário de cadastro
    with st.form("cadastro_form", clear_on_submit=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        """, unsafe_allow_html=True)

        # Nome com formatação automática
        st.text_input(
            "👤 Nome completo",
            key="nome_input",
            value=st.session_state.nome_val,
            placeholder="João Silva",
            help="Ao sair do campo, o nome será formatado automaticamente",
            on_change=on_change_nome,
        )

        nome = st.session_state.nome_val if st.session_state.nome_dirty else st.session_state.nome_input

        # Email com formatação automática
        st.text_input(
            "📧 E-mail",
            key="email_input",
            value=st.session_state.email_val,
            placeholder="seu@email.com",
            help="Ao sair do campo, o e-mail será colocado em minúsculas automaticamente",
            on_change=on_change_email,
        )

        email = st.session_state.email_val if st.session_state.email_dirty else st.session_state.email_input

        # Campos de senha
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

        # Preview da formatação
        if st.session_state.nome_dirty or st.session_state.email_dirty:
            st.markdown("**👁️ Como será salvo:**")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.info(f"👤 {formatar_nome(nome)}")
            with col_p2:
                st.info(f"📧 {formatar_email(email)}")

        col1, col2 = st.columns([3, 1])

        with col1:
            submitted = st.form_submit_button(
                "📝 Cadastrar",
                use_container_width=True,
                type="primary"
            )

        with col2:
            limpar = st.form_submit_button("❌ Limpar", use_container_width=True)

    # Botão limpar
    if limpar:
        st.session_state.nome_val = ""
        st.session_state.email_val = ""
        st.session_state.nome_input = ""
        st.session_state.email_input = ""
        st.session_state.nome_dirty = False
        st.session_state.email_dirty = False
        st.experimental_rerun()

    # Processa cadastro
    if submitted:
        # Garante formatação final
        nome_final = formatar_nome(nome)
        email_final = formatar_email(email)

        if not all([nome_final, email_final, senha, confirmar_senha]):
            st.error("⚠️ Preencha todos os campos")
        else:
            with st.spinner("Cadastrando..."):
                sucesso, mensagem = cadastrar_usuario(
                    nome_final,
                    email_final,
                    senha,
                    confirmar_senha
                )

            if sucesso:
                st.success(f"✅ {mensagem}")
                st.balloons()
                st.info("👉 Faça login para acessar o sistema")

                # Reseta campos
                st.session_state.nome_val = ""
                st.session_state.email_val = ""
                st.session_state.nome_input = ""
                st.session_state.email_input = ""
                st.session_state.nome_dirty = False
                st.session_state.email_dirty = False

                # Link para login
                st.markdown("---")
                st.markdown("""
                <a href="/login" target="_self">
                    <button style="background: #4CAF50; color: white; padding: 12px 24px; 
                                   border: none; border-radius: 8px; font-size: 16px; 
                                   cursor: pointer; width: 100%;">
                        🔐 Ir para Login
                    </button>
                </a>
                """, unsafe_allow_html=True)
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
