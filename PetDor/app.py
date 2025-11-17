"""
Aplicativo principal PETDOR
Versão com Dark Mode, Mobile-friendly e tema PETDor
"""

import sys
from pathlib import Path
import streamlit as st

# Ajusta path do projeto
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# UI styles and assets
from styles import carregar_css

# Import database functions (no execution on import)
from database.connection import conectar_db, init_database
from database.migration import criar_tabelas, migrar_banco_completo
from auth.user import buscar_usuario_por_id
from config import APP_CONFIG

# Streamlit config (theme is also set via .streamlit/config.toml)
st.set_page_config(
    page_title=APP_CONFIG.get("titulo", "PETDor"),
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
carregar_css()

# Small helper to render the logo
def render_logo(width=220):
    try:
        with open(Path(__file__).parent / "assets" / "logo.svg", "r", encoding="utf-8") as f:
            svg = f.read()
            st.markdown(f"<div style='display:flex; align-items:center; gap:12px'>{svg}</div>", unsafe_allow_html=True)
    except Exception:
        st.title("🐾 " + APP_CONFIG.get("titulo", "PETDor"))

# Card component (mobile-friendly)
def card(emoji, title, href):
    st.markdown(f"""
    <div class="petdor-card">
        <div style="font-size:2.2rem;margin-bottom:8px;">{emoji}</div>
        <h3 style="margin:0 0 8px 0;">{title}</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"[Ir →]({href})", unsafe_allow_html=True)

def exibir_home_publica():
    st.markdown("<div style='display:flex;align-items:center;gap:16px'>", unsafe_allow_html=True)
    render_logo()
    st.markdown(f"<div style='margin-left:8px'><h2 style='margin:0;color:#E6EEF8'>{APP_CONFIG.get('titulo','PETDor')}</h2><div class='muted'>{APP_CONFIG.get('tagline','Avaliação profissional de dor em animais')}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="petdor-card">
      <h3 style="margin-top:0">✨ Recursos Principais</h3>
      <ul class="muted">
        <li>📋 Avaliações baseadas em escalas científicas</li>
        <li>🐕 Suporte para cães e gatos</li>
        <li>📊 Histórico completo de avaliações</li>
        <li>📄 Relatórios em PDF profissionais</li>
        <li>🔒 Dados seguros e privados</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='petdor-cta'>", unsafe_allow_html=True)
        if st.button("🔐 Fazer Login", key="login_cta"):
            st.experimental_set_query_params(page="login")
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='petdor-cta'>", unsafe_allow_html=True)
        if st.button("📝 Criar Conta", key="cadastro_cta"):
            st.experimental_set_query_params(page="cadastro")
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def exibir_dashboard(usuario):
    render_logo(180)
    st.markdown(f"### Olá, **{usuario.get('nome','Usuário')}** 👋")
    st.markdown(f"<div class='muted'>Perfil: {usuario.get('tipo_usuario','tutor').title()}</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar actions
    st.sidebar.title("Navegação")
    st.sidebar.markdown(f"👋 {usuario.get('nome','Usuário')}")
    if st.sidebar.button("📋 Avaliar Pet", use_container_width=True):
        st.experimental_set_query_params(page="avaliacao")
        st.experimental_rerun()
    if st.sidebar.button("📊 Histórico", use_container_width=True):
        st.experimental_set_query_params(page="historico")
        st.experimental_rerun()
    if st.sidebar.button("👤 Minha Conta", use_container_width=True):
        st.experimental_set_query_params(page="conta")
        st.experimental_rerun()
    if usuario.get("is_admin"):
        if st.sidebar.button("🔐 Administração", use_container_width=True):
            st.experimental_set_query_params(page="admin")
            st.experimental_rerun()
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.experimental_rerun()

    # Main action cards (responsive)
    cols = st.columns([1,1,1])
    with cols[0]:
        card("📋", "Nova Avaliação", "/avaliacao")
    with cols[1]:
        card("📊", "Histórico", "/historico")
    with cols[2]:
        card("👤", "Minha Conta", "/conta")

    # Stats
    try:
        from database.models import get_estatisticas_usuario
        stats = get_estatisticas_usuario(usuario["id"])
        if stats and stats.get("total_avaliacoes",0) > 0:
            st.markdown("### 📈 Suas Estatísticas")
            c1, c2, c3 = st.columns(3)
            c1.metric("Avaliações", stats.get("total_avaliacoes",0))
            c2.metric("Pacientes", stats.get("total_pets",0))
            c3.metric("Média de Dor", f"{stats.get('media_percentual',0):.1f}%")
    except Exception:
        st.info("📊 Estatísticas aparecerão após sua primeira avaliação.")

def main():
    # Inicializa DB e migrações apenas 1x por sessão
    if "db_initialized" not in st.session_state:
        with st.spinner("Inicializando banco de dados..."):
            conectar_db()
            criar_tabelas()
            migrar_banco_completo()
            init_database()
        st.session_state["db_initialized"] = True

    # Optional: redirect flag
    if st.session_state.get("redirect_to_avaliacao"):
        st.session_state["redirect_to_avaliacao"] = False
        st.experimental_set_query_params(page="avaliacao")
        st.experimental_rerun()

    usuario_id = st.session_state.get("usuario_id")
    if not usuario_id:
        exibir_home_publica()
        return

    usuario = buscar_usuario_por_id(usuario_id)
    if not usuario:
        st.error("Erro ao carregar usuário. Faça login novamente.")
        st.session_state.clear()
        st.experimental_rerun()
        return

    exibir_dashboard(usuario)

if __name__ == "__main__":
    main()
