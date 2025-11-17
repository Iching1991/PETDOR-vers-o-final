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
    # Inicializa banco de dados
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state['db_initialized'] = True

    # Header
    st.title("🐾 " + APP_CONFIG['titulo'])
    st.markdown("---")

    # Sidebar com navegação
    st.sidebar.title("Navegação")

    if 'usuario_id' in st.session_state:
        # Usuário logado
        st.sidebar.success(f"👋 {st.session_state.get('email', 'Usuário')}")

        pages = {
            "📋 Avaliar Pet": "pages/avaliacao.py",
            "📊 Histórico": "pages/historico.py",
            "👤 Minha Conta": "pages/conta.py",
            "🚪 Sair": None
        }

        for nome, pagina in pages.items():
            if pagina:
                if st.sidebar.button(nome):
                    st.switch_page(pagina)
            else:
                if st.sidebar.button(nome):
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
            if st.sidebar.button(nome):
                st.switch_page(pagina)

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Versão:** {APP_CONFIG['versao']}")
    with col2:
        st.markdown(f"**Autor:** {APP_CONFIG['autor']}")
    with col3:
        st.markdown("**[Sobre o PETDor](#)")

if __name__ == "__main__":
    main()
