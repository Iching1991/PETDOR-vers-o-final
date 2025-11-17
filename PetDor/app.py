"""
Aplicativo principal PETDOR
Sistema profissional de avaliação de dor em animais de companhia
"""

import sys
from pathlib import Path
import streamlit as st

# -----------------------------------------------------------
# CONFIGURAÇÃO DO PATH DO PROJETO
# -----------------------------------------------------------
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
from database.connection import conectar_db
from database.migration import criar_tabelas

# Inicializa o banco
conectar_db()
criar_tabelas()

# -----------------------------------------------------------
# MIGRAÇÃO DO BANCO (executa apenas 1 vez no startup)
# -----------------------------------------------------------
from database.migration import migrar_banco_completo
migrar_banco_completo()

# -----------------------------------------------------------
# IMPORTAÇÕES DO SISTEMA
# -----------------------------------------------------------
from database.connection import init_database
from auth.user import buscar_usuario_por_id
from config import APP_CONFIG

# -----------------------------------------------------------
# CONFIGURAÇÃO DO STREAMLIT
# -----------------------------------------------------------
st.set_page_config(
    page_title=APP_CONFIG['titulo'],
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------------------
def main():
    """Função principal do app."""

    # Inicializa banco apenas uma vez
    if 'db_initialized' not in st.session_state:
        with st.spinner("Inicializando sistema..."):
            init_database()
            st.session_state['db_initialized'] = True

    # ================================================
    # REDIRECIONAMENTO APÓS LOGIN
    # ================================================
    if st.session_state.get("redirect_to_avaliacao", False):
        st.session_state["redirect_to_avaliacao"] = False
        st.switch_page("pages/avaliacao.py")
        st.stop()

    # --------------------------------------------------
    # VERIFICA LOGIN
    # --------------------------------------------------
    usuario_id = st.session_state.get("usuario_id")

    # Usuário não logado → página inicial + menu básico
    if not usuario_id:
        exibir_home_publica()
        return

    # Carrega dados do usuário
    usuario = buscar_usuario_por_id(usuario_id)

    if not usuario:
        st.error("Erro ao carregar usuário. Faça login novamente.")
        st.session_state.clear()
        st.switch_page("pages/login.py")
        return

    # Renderiza a interface principal
    exibir_dashboard(usuario)


# ============================================================
# PÁGINA PÚBLICA (Sem login)
# ============================================================
def exibir_home_publica():

    st.title("🐾 Bem-vindo ao PETDor")
    st.markdown("### Sistema profissional de avaliação de dor em animais de companhia")
    st.markdown("---")

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
            <li>👥 Perfis para Tutores, Clínicas e Veterinários</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.page_link("pages/login.py", label="🔐 Fazer Login", icon="🔐", use_container_width=True)

    with col2:
        st.page_link("pages/cadastro.py", label="📝 Criar Conta", icon="📝", use_container_width=True)


# ============================================================
# DASHBOARD DO USUÁRIO LOGADO
# ============================================================
def exibir_dashboard(usuario):

    nome = usuario["nome"]
    tipo = usuario.get("tipo_usuario", "tutor").title()

    st.title(f"🐾 Olá, {nome}!")
    st.markdown(f"### Perfil: **{tipo}**")
    st.markdown("O que você gostaria de fazer hoje? 👇")
    st.markdown("---")

    # --------------------------------------------------
    # MENU LATERAL
    # --------------------------------------------------
    st.sidebar.title("Navegação")
    st.sidebar.success(f"👋 {nome}")

    st.sidebar.page_link("pages/avaliacao.py", label="📋 Avaliar Pet", use_container_width=True)
    st.sidebar.page_link("pages/historico.py", label="📊 Histórico", use_container_width=True)
    st.sidebar.page_link("pages/conta.py", label="👤 Minha Conta", use_container_width=True)

    if usuario.get("is_admin"):
        st.sidebar.page_link("pages/admin.py", label="🔐 Administração", use_container_width=True)

    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # --------------------------------------------------
    # Cards principais
    # --------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        card("📋", "Nova Avaliação", "/avaliacao")

    with col2:
        card("📊", "Histórico", "/historico")

    with col3:
        card("👤", "Minha Conta", "/conta")

    # --------------------------------------------------
    # Estatísticas rápidas
    # --------------------------------------------------
    try:
        from database.models import get_estatisticas_usuario
        stats = get_estatisticas_usuario(usuario["id"])

        if stats and stats["total_avaliacoes"] > 0:
            st.markdown("### 📈 Suas Estatísticas")
            col1, col2, col3 = st.columns(3)

            col1.metric("Avaliações Realizadas", stats["total_avaliacoes"])
            col2.metric("Pacientes Únicos", stats["total_pets"])
            col3.metric("Média de Dor", f"{stats['media_percentual']:.1f}%")
    except:
        st.info("📊 Estatísticas aparecerão após sua primeira avaliação.")

    # --------------------------------------------------
    # Rodapé
    # --------------------------------------------------
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    col1.write(f"**Versão:** {APP_CONFIG['versao']}")
    col2.write(f"**Autor:** {APP_CONFIG['autor']}")
    col3.write("📚 Documentação | 💬 Suporte")


# ============================================================
# COMPONENTE DE CARD (VISUAL)
# ============================================================
def card(emoji, titulo, link):
    st.markdown(f"""
    <div style="background: white; padding: 2rem; border-radius: 15px; 
                text-align: center; box-shadow: 0 3px 12px rgba(0,0,0,0.08); 
                margin-bottom: 1rem;">
        <div style="font-size: 3rem;">{emoji}</div>
        <h3 style="margin-top: 0.5rem; color: #2d3748;">{titulo}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(titulo, link, use_container_width=True)


# -----------------------------------------------------------
# EXECUÇÃO DO APP
# -----------------------------------------------------------
if __name__ == "__main__":
    main()



