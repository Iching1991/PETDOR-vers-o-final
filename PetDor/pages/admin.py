"""
🔐 Página Admin - Estatísticas e Métricas do PETDor
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.models import (
    get_estatisticas_gerais_usuarios,
    buscar_avaliacoes_usuario,
    get_estatisticas_usuario
)
from database.models import buscar_usuario_por_email, buscar_usuario_por_id
from auth.user import buscar_usuario_por_id
import logging

logger = logging.getLogger(__name__)

def render_admin_page(usuario):
    """Renderiza página de administração"""

    # Verifica se é admin (você pode ajustar essa lógica)
    if not usuario.get('is_admin', False):
        st.error("❌ Acesso negado. Esta página é restrita a administradores.")
        st.stop()

    # Header
    st.markdown("""
    <div class="wellness-card" style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">🔐 Painel Administrativo</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Estatísticas e métricas do PETDor
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar com filtros
    st.sidebar.title("📊 Filtros")

    # Período
    periodo = st.sidebar.selectbox(
        "Período",
        ["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Todo período"],
        index=2
    )

    # Tipo de estatística
    secao = st.sidebar.radio(
        "Seção",
        ["📈 Usuários", "📊 Avaliações", "📋 Usuários Detalhados"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Acesso Admin**")
    st.sidebar.info(f"👤 {usuario['nome']}")
    st.sidebar.caption(f"ID: {usuario['id']}")

    # Conteúdo principal baseado na seção
    if secao == "📈 Usuários":
        render_secao_usuarios(periodo)
    elif secao == "📊 Avaliações":
        render_secao_avaliacoes(periodo)
    elif secao == "📋 Usuários Detalhados":
        render_secao_usuarios_detalhados()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.9rem;">
        <p>🔐 Painel Administrativo PETDor | Dados atualizados em tempo real</p>
    </div>
    """, unsafe_allow_html=True)


def render_secao_usuarios(periodo):
    """Renderiza estatísticas de usuários"""
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">👥 Estatísticas de Usuários</h3>
    </div>
    """, unsafe_allow_html=True)

    # Estatísticas gerais
    stats = get_estatisticas_gerais_usuarios()

    if stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "👥 Total de Usuários",
                f"{stats['total_usuarios']:,}",
                delta=f"+{stats['total_usuarios']}"
            )

        with col2:
            st.metric(
                "✅ Usuários Ativos",
                f"{stats['total_ativos']:,}",
                delta=f"+{stats['total_ativos'] - stats['total_desativados']}"
            )

        with col3:
            st.metric(
                "❌ Usuários Desativados",
                f"{stats['total_desativados']:,}",
                delta=f"-{stats['total_desativados']}",
                delta_color="inverse"
            )

        with col4:
            st.metric(
                "📉 Taxa de Churn",
                f"{stats['taxa_desativacao']:.1f}%",
                delta=f"{stats['taxa_desativacao']:.1f}%"
            )

        # Gráfico de distribuição
        st.subheader("📊 Distribuição de Status")

        import matplotlib.pyplot as plt
        import numpy as np

        labels = ['Ativos', 'Desativados']
        sizes = [stats['total_ativos'], stats['total_desativados']]
        colors = ['#28a745', '#dc3545']
        explode = (0, 0.1)  # explode 1st slice

        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title('Distribuição de Usuários por Status', fontsize=14, fontweight='bold')

        st.pyplot(fig1)

        # Tabela de resumo
        st.subheader("📋 Resumo Detalhado")

        resumo_data = {
            'Métrica': ['Total Cadastrados', 'Ativos', 'Desativados', 'Taxa de Churn'],
            'Quantidade': [
                stats['total_usuarios'],
                stats['total_ativos'],
                stats['total_desativados'],
                f"{stats['taxa_desativacao']:.2f}%"
            ],
            'Status': ['📊 Total', '✅ Ativo', '❌ Inativo', '📉 Churn']
        }

        df_resumo = pd.DataFrame(resumo_data)
        st.dataframe(df_resumo, use_container_width=True)

        # Análise de churn
        st.subheader("🔍 Análise de Churn")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"""
            **Retenção:** {100 - stats['taxa_desativacao']:.1f}%

            **Interpretação:**
            - ✅ **Baixo churn (< 10%)**: Excelente retenção
            - ⚠️ **Médio churn (10-25%)**: Atenção necessária
            - ❌ **Alto churn (> 25%)**: Investigar motivos
            """)

        with col2:
            if stats['total_desativados'] > 0:
                st.warning(f"""
                **{stats['total_desativados']} usuários desativaram a conta**

                **Possíveis ações:**
                - 📧 Enviar pesquisa de satisfação
                - 📊 Analisar padrões de uso
                - 💡 Melhorar onboarding
                """)
            else:
                st.success("🎉 Nenhum usuário desativou a conta!")

    else:
        st.error("❌ Erro ao carregar estatísticas de usuários")


def render_secao_avaliacoes(periodo):
    """Renderiza estatísticas de avaliações"""
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">📊 Estatísticas de Avaliações</h3>
    </div>
    """, unsafe_allow_html=True)

    try:
        with get_db() as conn:
            cur = conn.cursor()

            # Total de avaliações
            cur.execute("SELECT COUNT(*) FROM avaliacoes")
            total_avaliacoes = cur.fetchone()[0] or 0

            # Usuários que fizeram avaliações
            cur.execute("""
                SELECT COUNT(DISTINCT usuario_id) FROM avaliacoes
            """)
            usuarios_avaliadores = cur.fetchone()[0] or 0

            # Média geral de dor
            cur.execute("SELECT AVG(percentual) FROM avaliacoes")
            media_geral = cur.fetchone()[0] or 0

            # Avaliações por espécie
            cur.execute("""
                SELECT especie, COUNT(*) as total, AVG(percentual) as media
                FROM avaliacoes 
                GROUP BY especie
                ORDER BY total DESC
            """)
            avaliacoes_especie = cur.fetchall()

            # Top 5 pets mais avaliados
            cur.execute("""
                SELECT pet_nome, COUNT(*) as total
                FROM avaliacoes 
                GROUP BY pet_nome
                ORDER BY total DESC
                LIMIT 5
            """)
            top_pets = cur.fetchall()

        # Métricas principais
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📋 Total de Avaliações", f"{total_avaliacoes:,}")

        with col2:
            st.metric("👥 Usuários Ativos", f"{usuarios_avaliadores:,}")

        with col3:
            st.metric("📈 Média de Dor", f"{media_geral:.1f}%")

        # Avaliações por espécie
        if avaliacoes_especie:
            st.subheader("🐾 Avaliações por Espécie")

            df_especies = pd.DataFrame(
                avaliacoes_especie,
                columns=['Espécie', 'Total', 'Média de Dor (%)']
            )

            st.dataframe(df_especies, use_container_width=True)

            # Gráfico de barras
            fig, ax = plt.subplots(figsize=(10, 6))
            especies = [row[0] for row in avaliacoes_especie]
            totais = [row[1] for row in avaliacoes_especie]

            bars = ax.bar(especies, totais, color=['#28a745' if i == 0 else '#ffc107' for i in range(len(especies))])
            ax.set_ylabel('Número de Avaliações')
            ax.set_title('Avaliações por Espécie', fontsize=14, fontweight='bold')
            ax.tick_params(axis='x', rotation=45)

            # Adiciona valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')

            st.pyplot(fig)

        # Top pets
        if top_pets:
            st.subheader("🏆 Top 5 Pets Mais Avaliados")

            top_data = {
                '🐕 Pet': [row[0] for row in top_pets],
                '📊 Avaliações': [row[1] for row in top_pets]
            }

            df_top = pd.DataFrame(top_data)
            st.dataframe(df_top, use_container_width=True)

            # Gráfico horizontal
            fig, ax = plt.subplots(figsize=(10, 6))
            pets = [row[0] for row in top_pets]
            counts = [row[1] for row in top_pets]

            y_pos = np.arange(len(pets))
            bars = ax.barh(y_pos, counts, color='#17a2b8')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(pets)
            ax.invert_yaxis()  # labels read top-to-bottom
            ax.set_xlabel('Número de Avaliações')
            ax.set_title('Top 5 Pets Mais Avaliados', fontsize=14, fontweight='bold')

            # Adiciona valores nas barras
            for i, v in enumerate(counts):
                ax.text(v + 0.5, i, str(v), va='center')

            st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Erro ao carregar estatísticas de avaliações: {e}")


def render_secao_usuarios_detalhados():
    """Renderiza lista detalhada de usuários"""
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">👥 Usuários Detalhados</h3>
    </div>
    """, unsafe_allow_html=True)

    try:
        with get_db() as conn:
            cur = conn.cursor()

            # Busca todos os usuários com suas estatísticas
            cur.execute("""
                SELECT 
                    u.id, u.nome, u.email, u.data_criacao, u.ativo,
                    COUNT(a.id) as total_avaliacoes,
                    AVG(a.percentual) as media_dor
                FROM usuarios u
                LEFT JOIN avaliacoes a ON u.id = a.usuario_id
                GROUP BY u.id, u.nome, u.email, u.data_criacao, u.ativo
                ORDER BY u.data_criacao DESC
            """)

            usuarios_data = cur.fetchall()

        if usuarios_data:
            # Prepara dados para DataFrame
            dados = []
            for row in usuarios_data:
                usuario = {
                    'ID': row[0],
                    'Nome': row[1],
                    'Email': row[2],
                    'Criado em': row[3],
                    'Status': '✅ Ativo' if row[4] else '❌ Inativo',
                    'Avaliações': row[5] or 0,
                    'Média Dor': f"{row[6]:.1f}%" if row[6] else "N/A"
                }
                dados.append(usuario)

            df_usuarios = pd.DataFrame(dados)

            # Filtros
            st.subheader("🔍 Filtros de Usuários")
            col1, col2, col3 = st.columns(3)

            with col1:
                status_filtro = st.selectbox("Status", ["Todos", "Ativos", "Inativos"])

            with col2:
                min_avaliacoes = st.slider("Mínimo de Avaliações", 0, 50, 0)

            with col3:
                ordenar_por = st.selectbox("Ordenar por", ["Data de Criação", "Nome", "Avaliações"])

            # Aplica filtros
            df_filtrado = df_usuarios.copy()

            if status_filtro == "Ativos":
                df_filtrado = df_filtrado[df_filtrado['Status'] == '✅ Ativo']
            elif status_filtro == "Inativos":
                df_filtrado = df_filtrado[df_filtrado['Status'] == '❌ Inativo']

            df_filtrado = df_filtrado[df_filtrado['Avaliações'] >= min_avaliacoes]

            if ordenar_por == "Nome":
                df_filtrado = df_filtrado.sort_values('Nome')
            elif ordenar_por == "Avaliações":
                df_filtrado = df_filtrado.sort_values('Avaliações', ascending=False)
            else:
                df_filtrado = df_filtrado.sort_values('Criado em', ascending=False)

            # Exibe tabela
            st.subheader(f"📋 Lista de Usuários ({len(df_filtrado)} encontrados)")

            # Configuração da tabela
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["✅ Ativo", "❌ Inativo"],
                        required=True
                    ),
                    "Média Dor": st.column_config.NumberColumn(
                        "Média Dor",
                        format="%.1f%%"
                    ),
                    "Avaliações": st.column_config.NumberColumn(
                        "Avaliações",
                        format="%d"
                    )
                },
                hide_index=True
            )

            # Estatísticas da tabela filtrada
            if len(df_filtrado) > 0:
                st.markdown("---")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("👥 Total Filtrado", len(df_filtrado))

                with col2:
                    ativos_filtrados = len(df_filtrado[df_filtrado['Status'] == '✅ Ativo'])
                    st.metric("✅ Ativos", ativos_filtrados)

                with col3:
                    inativos_filtrados = len(df_filtrado[df_filtrado['Status'] == '❌ Inativo'])
                    st.metric("❌ Inativos", inativos_filtrados)

                # Botão exportar
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="📥 Exportar CSV",
                    data=csv,
                    file_name=f"usuarios_petdor_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )

        else:
            st.info("ℹ️ Nenhum usuário encontrado no sistema")

    except Exception as e:
        st.error(f"❌ Erro ao carregar usuários detalhados: {e}")
        logger.error(f"Erro na seção de usuários detalhados: {e}")


# Configuração da página
if __name__ == "__main__":
    # Simula um usuário admin para teste (remover em produção)
    usuario_teste = {
        'id': 1,
        'nome': 'Admin PETDor',
        'email': 'admin@petdor.app',
        'is_admin': True
    }

    render_admin_page(usuario_teste)
