"""
Sistema de notificações do PETDor
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import logging
from database.connection import conectar_db
from utils.email_sender import enviar_email_notificacao

logger = logging.getLogger(__name__)


def criar_notificacao_dor(pet_id, percentual_dor, usuario_id_tutor, observacoes=""):
    """
    Cria notificação de dor detectada e envia para profissionais vinculados

    Args:
        pet_id: ID do pet
        percentual_dor: Percentual de dor detectado (0-100)
        usuario_id_tutor: ID do tutor
        observacoes: Observações da avaliação

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Determina nível de prioridade baseado no percentual de dor
        if percentual_dor >= 70:
            prioridade = 1  # Alta
            emoji = "🚨"
        elif percentual_dor >= 40:
            prioridade = 2  # Média
            emoji = "⚠️"
        else:
            prioridade = 3  # Baixa
            emoji = "ℹ️"

        # Busca nome do pet
        cursor.execute("SELECT nome FROM pets WHERE id = ?", (pet_id,))
        pet_nome = cursor.fetchone()[0] if cursor.fetchone() else "Pet"

        # Busca profissionais vinculados
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.tipo_usuario, vp.tipo_vinculo
            FROM vinculos_pets vp
            JOIN usuarios u ON vp.usuario_id = u.id
            WHERE vp.pet_id = ? AND vp.ativo = 1 
            AND u.tipo_usuario IN ('clinica', 'veterinario')
        """, (pet_id,))

        profissionais = cursor.fetchall()

        notificacoes_criadas = 0

        for prof in profissionais:
            prof_id, prof_nome, prof_email, prof_tipo, vinculo_tipo = prof

            # Mensagem personalizada
            if prof_tipo == 'clinica':
                mensagem = f"{emoji} **ATENÇÃO - DOR DETECTADA** no pet '{pet_name}' do tutor {usuario_id_tutor}"
                titulo = f"{emoji} Dor detectada - {pet_nome}"
            else:  # veterinario
                mensagem = f"{emoji} **URGENTE** - Seu paciente '{pet_nome}' apresenta {percentual_dor}% de dor"
                titulo = f"{emoji} Paciente com dor - {pet_nome}"

            # Salva notificação no banco
            cursor.execute("""
                INSERT INTO notificacoes (pet_id, usuario_id_destino, tipo_notificacao, 
                                        nivel_prioridade, mensagem)
                VALUES (?, ?, 'dor_detectada', ?, ?)
            """, (pet_id, prof_id, prioridade, mensagem))

            notificacoes_criadas += 1

            # Envia email (assíncrono, não bloqueia)
            try:
                enviar_email_notificacao(
                    destinatario=prof_email,
                    assunto=titulo,
                    corpo=f"""
                    <h2>{titulo}</h2>
                    <p><strong>Pet:</strong> {pet_nome}</p>
                    <p><strong>Nível de dor:</strong> {percentual_dor}% ({'ALTA' if prioridade == 1 else 'MÉDIA' if prioridade == 2 else 'BAIXA'})</p>
                    <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Observações:</strong> {observacoes or 'Nenhuma observação adicional'}</p>
                    <p><a href="https://petdor.app/historico?pet={pet_id}" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📊 Ver Histórico Completo</a></p>
                    """,
                    html=True
                )
                logger.info(f"Email de notificação enviado para {prof_email}")
            except Exception as e:
                logger.error(f"Erro ao enviar email para {prof_email}: {e}")

        # Notificação para o tutor também
        cursor.execute("""
            INSERT INTO notificacoes (pet_id, usuario_id_destino, tipo_notificacao, 
                                    nivel_prioridade, mensagem)
            VALUES (?, ?, 'dor_detectada', ?, ?)
        """, (pet_id, usuario_id_tutor, prioridade, f"{emoji} Seu pet '{pet_nome}' apresenta {percentual_dor}% de dor"))

        notificacoes_criadas += 1

        conn.commit()
        conn.close()

        logger.info(f"{notificacoes_criadas} notificações criadas para pet {pet_id}")
        return True, f"{notificacoes_criadas} notificações enviadas!"

    except Exception as e:
        logger.error(f"Erro ao criar notificação de dor: {e}")
        return False, f"Erro ao enviar notificações: {e}"


def listar_notificacoes_nao_lidas(usuario_id, limit=10):
    """Lista notificações não lidas do usuário"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT n.id, n.pet_id, n.tipo_notificacao, n.nivel_prioridade, 
                   n.mensagem, n.data_criacao, p.nome as pet_nome
            FROM notificacoes n
            LEFT JOIN pets p ON n.pet_id = p.id
            WHERE n.usuario_id_destino = ? AND n.lida = 0
            ORDER BY n.nivel_prioridade ASC, n.data_criacao DESC
            LIMIT ?
        """, (usuario_id, limit))

        notificacoes = []
        for row in cursor.fetchall():
            notificacoes.append({
                'id': row[0],
                'pet_id': row[1],
                'tipo': row[2],
                'prioridade': row[3],
                'mensagem': row[4],
                'data': row[5],
                'pet_nome': row[6] or 'Pet não identificado'
            })

        conn.close()
        return notificacoes

    except Exception as e:
        logger.error(f"Erro ao listar notificações: {e}")
        return []


def marcar_notificacao_lida(notificacao_id):
    """Marca uma notificação como lida"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notificacoes 
            SET lida = 1, data_lida = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (notificacao_id,))

        afetados = cursor.rowcount
        conn.commit()
        conn.close()

        return afetados > 0

    except Exception as e:
        logger.error(f"Erro ao marcar notificação como lida: {e}")
        return False


def contar_notificacoes_nao_lidas(usuario_id):
    """Conta notificações não lidas do usuário"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM notificacoes 
            WHERE usuario_id_destino = ? AND lida = 0
        """, (usuario_id,))

        count = cursor.fetchone()[0]
        conn.close()
        return count

    except Exception as e:
        logger.error(f"Erro ao contar notificações: {e}")
        return 0
