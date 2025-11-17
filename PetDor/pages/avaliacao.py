"""
📋 Página de Avaliação de Dor do Pet - PETDor

Responsável por:
- Exibir formulário de avaliação de dor para um pet selecionado.
- Listar pets do tutor logado.
- Redirecionar para cadastro de pet se nenhum for encontrado.
- Salvar a avaliação no banco de dados, incluindo respostas detalhadas.
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
from auth.user import buscar_usuario_por_id
from database.connection import conectar_db
from config import APP_CONFIG

# Importa as classes base e as configurações de espécie
from especies.base import EspecieConfig, Pergunta
from especies.cao import CONFIG_CAES
from especies.gato import CONFIG_GATOS

# Configuração da página
st.set_page_config(
    page_title="Avaliar Pet - " + APP_CONFIG["titulo"],
    page_icon="📋",
    layout="centered"
)


def listar_pets_do_tutor(usuario_id):
    """Lista pets cadastrados pelo tutor (usuario_id)."""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, especie
        FROM pets
        WHERE tutor_id = ?
        ORDER BY nome
    """, (usuario_id,))
    rows = cursor.fetchall()
    conn.close()

    pets = []
    for row in rows:
        pets.append({
            "id": row["id"] if isinstance(row, dict) else row[0],
            "nome": row["nome"] if isinstance(row, dict) else row[1],
            "especie": row["especie"] if isinstance(row, dict) else row[2],
        })
    return pets


def salvar_avaliacao(pet_id, usuario_id, percentual_dor, respostas_perguntas: Dict[str, str], observacoes):
    """Salva avaliação no banco com respostas das perguntas."""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Salva a avaliação principal
        cursor.execute("""
            INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes)
            VALUES (?, ?, ?, ?)
        """, (pet_id, usuario_id, percentual_dor, observacoes))

        avaliacao_id = cursor.lastrowid

        # Salva respostas das perguntas na nova tabela
        for pergunta_id, resposta_valor in respostas_perguntas.items():
            cursor.execute("""
                INSERT INTO avaliacao_respostas (avaliacao_id, pergunta_id, resposta)
                VALUES (?, ?, ?)
            """, (avaliacao_id, pergunta_id, resposta_valor))

        conn.commit()
        conn.close()
        return True, "Avaliação salva com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar avaliação: {e}"


def main():
    """Renderiza a página de avaliação de dor"""

    # 1. Verifica se o usuário está logado
    if 'usuario_id' not in st.session_state:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.info("Faça login ou crie uma conta para continuar.")
        st.markdown("""
        <a href="/login" target="_self">
            <button style="background: #4CAF50; color: white; padding: 12px 24px; 
                           border: none; border-radius: 8px; font-size: 16px; 
                           cursor: pointer; width: 100%; margin-top: 1rem;">
                🔐 Ir para Login
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.stop() # Para a execução da página se não estiver logado

    usuario_id = st.session_state['usuario_id']
    usuario_data = buscar_usuario_por_id(usuario_id)
    nome_usuario = usuario_data['nome'] if usuario_data else "Usuário"

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📋 Avaliar Dor do Pet</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Olá, {nome_usuario}! Selecione um pet e registre sua avaliação.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Lista pets do tutor
    pets_do_tutor = listar_pets_do_tutor(usuario_id)

    if not pets_do_tutor:
        st.info("Você ainda não tem pets cadastrados. Cadastre um para começar a avaliar!")
        st.markdown("""
        <a href="/cadastro_pet" target="_self">
            <button style="background: #2196F3; color: white; padding: 12px 24px; 
                           border: none; border-radius: 8px; font-size: 16px; 
                           cursor: pointer; width: 100%; margin-top: 1rem;">
                ➕ Cadastrar Novo Pet
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.stop() # Para a execução se não houver pets

    # 3. Seleção do pet para avaliação
    st.markdown("---")
    st.subheader("Selecione o Pet para Avaliar")

    nomes_pets_formatados = [f"{pet['nome']} ({pet['especie']})" for pet in pets_do_tutor]

    escolha_pet_str = st.selectbox(
        "Escolha um pet",
        options=nomes_pets_formatados,
        help="Selecione o pet que você deseja avaliar."
    )

    pet_escolhido = next((pet for pet in pets_do_tutor if f"{pet['nome']} ({pet['especie']})" == escolha_pet_str), None)

    if not pet_escolhido:
        st.warning("Nenhum pet selecionado ou encontrado. Por favor, selecione um pet.")
        st.stop()

    st.write(f"Você está avaliando: **{pet_escolhido['nome']}** (Espécie: {pet_escolhido['especie']})")

    # 4. Carrega a configuração de perguntas para a espécie selecionada
    especie_config: Optional[EspecieConfig] = None
    if pet_escolhido['especie'] == "Cão":
        especie_config = CONFIG_CAES
    elif pet_escolhido['especie'] == "Gato":
        especie_config = CONFIG_GATOS
    else:
        # Fallback para espécies não configuradas
        st.warning(f"Não há perguntas objetivas configuradas para a espécie '{pet_escolhido['especie']}'. Usando avaliação manual.")
        # Cria uma configuração genérica para evitar erros
        especie_config = EspecieConfig(
            nome="Genérico",
            descricao="Avaliação genérica",
            perguntas=[],
            opcoes_escala=["0 - Não se aplica", "1 - Leve", "2 - Moderada", "3 - Severa"] # Escala genérica
        )

    if not especie_config:
        st.error("Configuração de perguntas não encontrada para esta espécie.")
        st.stop()

    # 5. Formulário de avaliação de dor
    st.markdown("### 🩺 Avaliação Detalhada")

    # Inicializa respostas_perguntas na sessão para persistir entre reruns
    if 'respostas_perguntas' not in st.session_state:
        st.session_state['respostas_perguntas'] = {}

    if especie_config.perguntas:
        st.markdown(f"**{especie_config.descricao}**")
        with st.form("perguntas_objetivas_form"):
            for i, pergunta in enumerate(especie_config.perguntas):
                # Usa o ID da pergunta para o dicionário de respostas
                pergunta_id = pergunta.id 

                # Define o valor padrão do radio button a partir da sessão, se existir
                default_index = 0
                if pergunta_id in st.session_state['respostas_perguntas']:
                    try:
                        # Encontra o índice da resposta salva na lista de opções
                        default_index = especie_config.opcoes_escala.index(st.session_state['respostas_perguntas'][pergunta_id])
                    except ValueError:
                        default_index = 0 # Fallback se a resposta salva não estiver nas opções

                resposta = st.radio(
                    f"**{i+1}. {pergunta.texto}**", # Texto da pergunta no label do radio
                    options=especie_config.opcoes_escala,
                    key=f"pergunta_{pergunta_id}_{pet_escolhido['id']}",
                    horizontal=True,
                    index=default_index # Usa o valor padrão da sessão
                )
                st.session_state['respostas_perguntas'][pergunta_id] = resposta # Salva a resposta na sessão

            submitted_perguntas = st.form_submit_button(
                "Calcular Percentual de Dor",
                use_container_width=True,
                type="secondary"
            )

            if submitted_perguntas:
                # O percentual é calculado diretamente do st.session_state['respostas_perguntas']
                st.session_state['percentual_calculado'] = especie_config.calcular_percentual_dor(st.session_state['respostas_perguntas'])
                st.rerun() # Recarrega para exibir o percentual calculado

    # Exibe o percentual calculado e permite ajuste manual
    percentual_calculado = st.session_state.get('percentual_calculado', 0)
    st.markdown("### 📊 Percentual de Dor Calculado")
    st.metric("Nível de Dor Estimado", f"{percentual_calculado}%", delta=None)

    st.markdown("### ⚖️ Ajuste Manual (opcional)")
    percentual_final = st.slider(
        "Ajuste o percentual de dor (baseado na sua observação)",
        min_value=0, max_value=100, value=percentual_calculado, step=5,
        key="percentual_final_slider"
    )

    observacoes = st.text_area(
        "📝 Observações (opcional)",
        placeholder="Descreva sinais de dor, comportamento, medicamentos em uso, etc.",
        height=150,
        key="observacoes_textarea"
    )

    # Salva a avaliação final
    if st.button("💾 Salvar Avaliação Completa", use_container_width=True, type="primary"):
        respostas_para_salvar = st.session_state.get('respostas_perguntas', {})

        sucesso, mensagem = salvar_avaliacao(
            pet_id=pet_escolhido["id"],
            usuario_id=usuario_id,
            percentual_dor=percentual_final,
            respostas_perguntas=respostas_para_salvar,
            observacoes=observacoes
        )

        if sucesso:
            st.success(mensagem)
            st.balloons()
            # Limpa as variáveis de sessão para uma nova avaliação
            if 'respostas_perguntas' in st.session_state:
                del st.session_state['respostas_perguntas']
            if 'percentual_calculado' in st.session_state:
                del st.session_state['percentual_calculado']

            st.markdown("""
            <a href="/historico" target="_self">
                <button style="background: #4CAF50; color: white; padding: 12px 24px; 
                               border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                    📊 Ver Histórico
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.error(mensagem)


if __name__ == "__main__":
    main()
