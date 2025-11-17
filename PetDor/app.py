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
from database.migration import adicionar_colunas_desativacao, adicionar_campo_admin
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
        adicionar_colunas_desativacao()
        adicionar_campo_admin()
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

        # Links do menu lateral - ROTAS CORRETAS
        st.sidebar.markdown("""
        <a href="/avaliacao" target="_self">
            <button style="background: #4CAF50; color: white; padding: 10px; 
                           border: none; border-radius: 8px; cursor: pointer; 
                           width: 100%; margin: 5px 0; text-align: left;">
                📋 Avaliar Pet
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("""
        <a href="/historico" target="_self">
            <button style="background: #2196F3; color: white; padding: 10px; 
                           border: none; border-radius: 8px; cursor: pointer; 
                           width: 100%; margin: 5px 0; text-align: left;">
                📊 Histórico
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("""
        <a href="/conta" target="_self">
            <button style="background: #FF9800; color: white; padding: 10px; 
                           border: none; border-radius: 8px; cursor: pointer; 
                           width: 100%; margin: 5px 0; text-align: left;">
                👤 Minha Conta
            </button>
        </a>
        """, unsafe_allow_html=True)

        # Adiciona Admin se for admin
        if usuario_data and usuario_data.get('is_admin', False):
            st.sidebar.markdown("""
            <a href="/admin" target="_self">
                <button style="background: #9C27B0; color: white; padding: 10px; 
                               border: none; border-radius: 8px; cursor: pointer; 
                               width: 100%; margin: 5px 0; text-align: left;">
                    🔐 Admin
                </button>
            </a>
            """, unsafe_allow_html=True)

        # Botão Sair
        if st.sidebar.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.experimental_rerun()
    else:
        # Usuário não logado
        st.sidebar.markdown("""
        <a href="/login" target="_self">
            <button style="background: #4CAF50; color: white; padding: 10px; 
                           border: none; border-radius: 8px; cursor: pointer; 
                           width: 100%; margin: 5px 0; text-align: left;">
                🔐 Login
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("""
        <a href="/cadastro" target="_self">
            <button style="background: #2196F3; color: white; padding: 10px; 
                           border: none; border-radius: 8px; cursor: pointer; 
                           width: 100%; margin: 5px 0; text-align: left;">
                📝 Cadastro
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.sidebar.markdown("""
        <a href="/recuperar_senha" target="_self">
            <button style="background: #FF9800; color: white; padding: 10px; 
                           border: none; border-radius: 8px; cursor: pointer; 
                           width: 100%; margin: 5px 0; text-align: left;">
                🔑 Recuperar Senha
            </button>
        </a>
        """, unsafe_allow_html=True)

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
                st.markdown("""
                <a href="/login" target="_self">
                    <button style="background: #4CAF50; color: white; padding: 12px 24px; 
                                   border: none; border-radius: 8px; font-size: 16px; 
                                   cursor: pointer; width: 100%;">
                        🔐 Fazer Login
                    </button>
                </a>
                """, unsafe_allow_html=True)

            with col_btn2:
                st.markdown("""
                <a href="/cadastro" target="_self">
                    <button style="background: #2196F3; color: white; padding: 12px 24px; 
                                   border: none; border-radius: 8px; font-size: 16px; 
                                   cursor: pointer; width: 100%;">
                        📝 Criar Conta
                    </button>
                </a>
                """, unsafe_allow_html=True)
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

            st.markdown("""
            <a href="/avaliacao" target="_self">
                <button style="background: #4CAF50; color: white; padding: 10px 20px; 
                               border: none; border-radius: 8px; cursor: pointer; 
                               width: 100%; margin-top: 10px;">
                    Avaliar Pet
                </button>
            </a>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FFE5B4, #FFD1DC);
                        padding: 2rem; border-radius: 15px; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h3 style="color: #2d3748; margin: 0;">Histórico</h3>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <a href="/historico" target="_self">
                <button style="background: #2196F3; color: white; padding: 10px 20px; 
                               border: none; border-radius: 8px; cursor: pointer; 
                               width: 100%; margin-top: 10px;">
                    Ver Histórico
                </button>
            </a>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #E0BBE4, #D4A5A5);
                        padding: 2rem; border-radius: 15px; text-align: center; height: 200px;
                        display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">👤</div>
                <h3 style="color: #2d3748; margin: 0;">Minha Conta</h3>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <a href="/conta" target="_self">
                <button style="background: #FF9800; color: white; padding: 10px 20px; 
                               border: none; border-radius: 8px; cursor: pointer; 
                               width: 100%; margin-top: 10px;">
                    Configurações
                </button>
            </a>
            """, unsafe_allow_html=True)

        # Estatísticas rápidas
        st.markdown("<br><br>", unsafe_allow_html=True)

        try:
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
        except ImportError:
            st.info("📊 Estatísticas disponíveis após sua primeira avaliação!")

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



if __name__ == "__main__":
    main()

