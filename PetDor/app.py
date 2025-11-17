"""
Aplicativo principal PETDor
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from database.connection import init_database
from database.migration import adicionar_colunas_desativacao
from auth.user import buscar_usuario_por_id
from config import APP_CONFIG

# Configuração da página
st.set_page_config(
    page_title=APP_CONFIG['titulo'],
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Função principal do app"""
    # Inicializa banco de dados e migrações
    if 'db_initialized' not in st.session_state:
        init_database()
        adicionar_colunas_desativacao()  # Migração para colunas de desativação
        st.session_state['db_initialized'] = True
        st.session_state['migracoes_executadas'] = True

    # Header
    st.title("🐾 " + APP_CONFIG['titulo'])
    st.markdown("---")

    # Sidebar com navegação
    st.sidebar.title("Navegação")

    if 'usuario_id' in st.session_state:
        # Usuário logado
        usuario_data = buscar_usuario_por_id(st.session_state['usuario_id'])

        if usuario_data:
            st.sidebar.success(f"👋 {usuario_data['nome']}")
        else:
            st.sidebar.success(f"👋 Usuário")

        pages = {
            "📋 Avaliar Pet": "pages/avaliacao.py",
            "📊 Histórico": "pages/historico.py",
            "👤 Minha Conta": "pages/conta.py",
        }

        # Adiciona Admin se for admin
        if usuario_data and usuario_data.get('is_admin', False):
            pages["🔐 Admin"] = "pages/admin.py"

        pages["🚪 Sair"] = None

        for nome, pagina in pages.items():
            if pagina:
                if st.sidebar.button(nome, use_container_width=True):
                    st.switch_page(pagina)
            else:
                if st.sidebar.button(nome, use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
    else:
        # Usuário não logado
        pages = {
            "🔐 Login": "pages/login.py",
            "📝 Cadastro": "pages/cadastro.py",
            "🔑 Recuperar Senha": "pages/recuperar_senha.py"
        }

        for nome, pagina in pages.items():
            if st.sidebar.button(nome, use_container_width=True):
                st.switch_page(pagina)

    # Conteúdo principal (página inicial)
    if 'usuario_id' not in st.session_state:
        # Página de boas-vindas para não logados
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <h2 style="color: #2d3748; margin-bottom: 1rem;">
                Bem-vindo ao PETDor! 🐾
            </h2>
            <p style="color: #718096; font-size: 1.2rem; line-height: 1.8;">
                Sistema profissional de avaliação de dor em animais de companhia.<br>
                Baseado em escalas científicas validadas para cães e gatos.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                        padding: 2rem; border-radius: 15px; margin: 2rem 0;">
                <h3 style="color: #2d3748; text-align: center; margin-bottom: 1.5rem;">
                    ✨ Recursos Principais
                </h3>
                <ul style="color: #4a5568; font-size: 1.1rem; line-height: 2;">
                    <li>📋 Avaliações baseadas em escalas científicas</li>
                    <li>🐕 Suporte para cães e gatos</li>
                    <li>📊 Histórico completo de avaliações</li>
                    <li>📄 Relatórios em PDF profissionais</li>
                    <li>🔒 Dados seguros e privados</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("🔐 Fazer Login", use_container_width=True, type="primary"):
                    st.switch_page("pages/login.py")

            with col_btn2:
                if st.button("📝 Criar Conta", use_container_width=True):
                    st.switch_page("pages/cadastro.py")
    else:
        # Dashboard para usuários logados
        usuario_data = buscar_usuario_por_id(st.session_state['usuario_id'])
        nome_usuario = usuario_data['nome'] if usuario_data else 'Usuário'

        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem;">
            <h2 style="color: #2d3748;">
                Olá, {nome_usuario}! 👋
            </h2>
            <p style="color: #718096; font-size: 1.1rem;">
                O que você gostaria de fazer hoje?
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC);
                        padding: 2rem; border-radius: 15px; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <h3 style="color: #2d3748; margin: 0;">Nova Avaliação</h3>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Avaliar Pet", use_container_width=True, type="primary"):
                st.switch_page("pages/avaliacao.py")

        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FFE5B4, #FFD1DC);
                        padding: 2rem; border-radius: 15px; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h3 style="color: #2d3748; margin: 0;">Histórico</h3>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver Histórico", use_container_width=True):
                st.switch_page("pages/historico.py")

        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #E0BBE4, #D4A5A5);
                        padding: 2rem; border-radius: 15px; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">👤</div>
                <h3 style="color: #2d3748; margin: 0;">Minha Conta</h3>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Configurações", use_container_width=True):
                st.switch_page("pages/conta.py")

        # Estatísticas rápidas
        st.markdown("<br><br>", unsafe_allow_html=True)

        from database.models import get_estatisticas_usuario

        stats = get_estatisticas_usuario(st.session_state['usuario_id'])

        if stats and stats.get('total_avaliacoes', 0) > 0:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #2d3748; text-align: center; margin-bottom: 1rem;">
                    📈 Suas Estatísticas
                </h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Avaliações Realizadas", stats.get('total_avaliacoes', 0))

            with col2:
                st.metric("Pacientes Únicos", stats.get('total_pets', 0))

            with col3:
                media = stats.get('media_percentual', 0)
                st.metric("Média de Dor", f"{media:.1f}%")

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Versão:** {APP_CONFIG['versao']}")

    with col2:
        st.markdown(f"**Autor:** {APP_CONFIG['autor']}")

    with col3:
        st.markdown("**[📚 Documentação](#)** | **[💬 Suporte](#)**")


if __name__ == "__main__":
    main()



