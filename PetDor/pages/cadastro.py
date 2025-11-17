"""
👤 Página de Minha Conta
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import buscar_usuario_por_id, atualizar_usuario, alterar_senha, deletar_usuario
from utils.validators import validar_nome, validar_email, validar_senha, senhas_conferem

# Configuração da página
st.set_page_config(
    page_title="Minha Conta - PETDor",
    page_icon="👤",
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
    """Renderiza a página de minha conta"""

    # Verifica se usuário está logado
    if 'usuario_id' not in st.session_state:
        st.error("❌ Você precisa estar logado para acessar esta página.")
        if st.button("🔐 Fazer Login"):
            st.markdown("""
            <meta http-equiv="refresh" content="0; url=/login">
            """, unsafe_allow_html=True)
        st.stop()

    # Busca dados do usuário
    usuario_data = buscar_usuario_por_id(st.session_state['usuario_id'])

    if not usuario_data:
        st.error("❌ Usuário não encontrado.")
        st.stop()

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">👤 Minha Conta</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Gerencie seus dados e configurações
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Inicializa session_state para formatação
    if "nome_val" not in st.session_state:
        st.session_state.nome_val = usuario_data['nome']
    if "email_val" not in st.session_state:
        st.session_state.email_val = usuario_data['email']
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

    # Informações atuais do usuário
    st.markdown("---")
    st.markdown("""
    <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**👤 Nome:** {usuario_data['nome']}")
        st.markdown(f"**📧 E-mail:** {usuario_data['email']}")

    with col2:
        st.markdown(f"**📅 Criado em:** {usuario_data['data_criacao']}")
        if usuario_data.get('is_admin', False):
            st.markdown("**🔐 Status:** Administrador")
        else:
            st.markdown("**🔐 Status:** Usuário")

    st.markdown("</div>", unsafe_allow_html=True)

    # Abas de navegação
    tab1, tab2, tab3 = st.tabs(["✏️ Editar Dados", "🔒 Alterar Senha", "⚠️ Deletar Conta"])

    with tab1:
        """Editar Dados Pessoais"""
        st.markdown("### ✏️ Editar Dados Pessoais")

        with st.form("editar_dados_form"):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                        padding: 2rem; border-radius: 15; margin: 1rem 0;">
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

            st.markdown("</div>", unsafe_allow_html=True)

            # Preview da formatação
            if st.session_state.nome_dirty or st.session_state.email_dirty:
                st.markdown("**👁️ Como ficará após formatação:**")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.info(f"👤 {formatar_nome(nome)}")
                with col_p2:
                    st.info(f"📧 {formatar_email(email)}")

            col1, col2 = st.columns([3, 1])

            with col1:
                submitted_editar = st.form_submit_button(
                    "💾 Salvar Alterações",
                    use_container_width=True,
                    type="primary"
                )

            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.nome_val = usuario_data['nome']
                    st.session_state.email_val = usuario_data['email']
                    st.session_state.nome_dirty = False
                    st.session_state.email_dirty = False
                    st.experimental_rerun()

        # Processa edição
        if submitted_editar:
            if not nome or not email:
                st.error("⚠️ Preencha todos os campos")
            else:
                # Aplica formatação final
                nome_final = formatar_nome(nome)
                email_final = formatar_email(email)

                with st.spinner("Atualizando dados..."):
                    sucesso, mensagem = atualizar_usuario(
                        st.session_state['usuario_id'],
                        nome_final if nome_final != usuario_data['nome'] else None,
                        email_final if email_final != usuario_data['email'] else None
                    )

                    if sucesso:
                        st.success(f"✅ {mensagem}")
                        st.balloons()

                        # Atualiza dados na sessão
                        st.session_state.nome = nome_final
                        usuario_data['nome'] = nome_final
                        if email_final != usuario_data['email']:
                            st.session_state.email = email_final
                            usuario_data['email'] = email_final

                        # Reseta estados
                        st.session_state.nome_dirty = False
                        st.session_state.email_dirty = False
                    else:
                        st.error(f"❌ {mensagem}")

    with tab2:
        """Alterar Senha"""
        st.markdown("### 🔒 Alterar Senha")

        with st.form("alterar_senha_form"):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FFE5B4, #FFD1DC); 
                        padding: 2rem; border-radius: 15px; margin: 1rem 0;">
            """, unsafe_allow_html=True)

            senha_atual = st.text_input(
                "🔒 Senha atual",
                type="password",
                placeholder="••••••••",
                help="Digite sua senha atual para confirmar"
            )

            nova_senha = st.text_input(
                "🔐 Nova senha",
                type="password",
                placeholder="••••••••",
                help="Digite a nova senha (mínimo 6 caracteres)"
            )

            confirmar_nova = st.text_input(
                "🔐 Confirmar nova senha",
                type="password",
                placeholder="••••••••",
                help="Digite a nova senha novamente"
            )

            st.markdown("</div>", unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                submitted_senha = st.form_submit_button(
                    "🔐 Alterar Senha",
                    use_container_width=True,
                    type="primary"
                )

            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.experimental_rerun()

        # Processa alteração de senha
        if submitted_senha:
            if not all([senha_atual, nova_senha, confirmar_nova]):
                st.error("⚠️ Preencha todos os campos")
            else:
                # Valida nova senha
                ok_senha, msg_senha = validar_senha(nova_senha)
                if not ok_senha:
                    st.error(f"❌ {msg_senha}")
                else:
                    # Verifica se senhas conferem
                    ok_conf, msg_conf = senhas_conferem(nova_senha, confirmar_nova)
                    if not ok_conf:
                        st.error(f"❌ {msg_conf}")
                    else:
                        with st.spinner("Alterando senha..."):
                            sucesso, mensagem = alterar_senha(
                                st.session_state['usuario_id'],
                                senha_atual,
                                nova_senha,
                                confirmar_nova
                            )

                            if sucesso:
                                st.success(f"✅ {mensagem}")
                                st.balloons()
                            else:
                                st.error(f"❌ {mensagem}")

    with tab3:
        """Deletar Conta"""
        st.markdown("### ⚠️ Deletar Conta")

        st.warning("""
        **⚠️ Atenção! Esta ação é irreversível.**

        Ao deletar sua conta, você perderá acesso a:
        - Todas as avaliações realizadas
        - Histórico de pets
        - Relatórios gerados
        - Dados pessoais

        **Esta ação não pode ser desfeita.**
        """)

        with st.form("deletar_conta_form"):
            senha_confirmacao = st.text_input(
                "🔒 Senha para confirmação",
                type="password",
                placeholder="••••••••",
                help="Digite sua senha para confirmar a exclusão"
            )

            st.markdown("""
            <div style="background: #fed7d7; padding: 1rem; border-radius: 8px; 
                        border-left: 4px solid #e53e3e; margin: 1rem 0;">
                <strong>⚠️ Confirmação:</strong> Digite sua senha para confirmar que deseja realmente deletar sua conta.
            </div>
            """, unsafe_allow_html=True)

            submitted_delete = st.form_submit_button(
                "🗑️ Deletar Minha Conta",
                use_container_width=True,
                type="primary",
                help="Esta ação é irreversível!"
            )

        # Processa deleção
        if submitted_delete:
            if not senha_confirmacao:
                st.error("⚠️ Digite sua senha para confirmar")
            else:
                with st.spinner("Processando exclusão..."):
                    sucesso, mensagem = deletar_usuario(
                        st.session_state['usuario_id'],
                        senha_confirmacao
                    )

                    if sucesso:
                        st.success(f"✅ {mensagem}")
                        st.balloons()
                        st.info("Sua conta foi desativada. Você pode reativá-la posteriormente se necessário.")

                        # Limpa sessão e redireciona
                        st.session_state.clear()
                        st.markdown("""
                        <meta http-equiv="refresh" content="3; url=/">
                        """, unsafe_allow_html=True)
                        st.info("Redirecionando para a página inicial...")
                    else:
                        st.error(f"❌ {mensagem}")

    # Links úteis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <a href="/" target="_self">
            <button style="background: #4CAF50; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                🏠 Voltar para Home
            </button>
        </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href="/avaliacao" target="_self">
            <button style="background: #2196F3; color: white; padding: 10px 20px; 
                           border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                📋 Nova Avaliação
            </button>
        </a>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()


