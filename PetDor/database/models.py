"""
Módulo de modelos e funções de acesso a dados do PETDOR.
Contém funções para interagir com as tabelas do banco de dados.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.connection import conectar_db

# --- Funções para Usuários ---

def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo email."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()
    return dict(usuario) if usuario else None

def buscar_usuario_por_id(usuario_id: int) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    return dict(usuario) if usuario else None

def criar_usuario(nome: str, email: str, senha_hash: str, tipo_usuario: str = 'tutor', token_confirmacao: str = None) -> Optional[int]:
    """Cria um novo usuário no banco de dados."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        data_registro = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, data_registro, tipo_usuario, token_confirmacao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, email, senha_hash, data_registro, tipo_usuario, token_confirmacao))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def atualizar_usuario(usuario_id: int, **kwargs) -> bool:
    """Atualiza campos de um usuário."""
    conn = conectar_db()
    cursor = conn.cursor()
    set_clauses = []
    values = []
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)

    if not set_clauses:
        conn.close()
        return False

    values.append(usuario_id)
    query = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = ?"

    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

def desativar_usuario(usuario_id: int, motivo: str) -> bool:
    """Desativa um usuário (soft delete)."""
    data_desativacao = datetime.now().isoformat()
    return atualizar_usuario(usuario_id, data_desativacao=data_desativacao, motivo_desativacao=motivo)

def ativar_usuario(usuario_id: int) -> bool:
    """Ativa um usuário desativado."""
    return atualizar_usuario(usuario_id, data_desativacao=None, motivo_desativacao=None)

def confirmar_email_usuario(token_confirmacao: str) -> bool:
    """Confirma o email de um usuário usando o token."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET email_confirmado = 1, token_confirmacao = NULL WHERE token_confirmacao = ?", (token_confirmacao,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

# --- Funções para Pets ---

def criar_pet(tutor_id: int, nome: str, especie: str, raca: str = None, data_nascimento: str = None, sexo: str = None, peso: float = None, observacoes: str = None) -> Optional[int]:
    """Cria um novo pet para um tutor."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pets (tutor_id, nome, especie, raca, data_nascimento, sexo, peso, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tutor_id, nome, especie, raca, data_nascimento, sexo, peso, observacoes))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        return None
    finally:
        conn.close()

def buscar_pets_por_tutor(tutor_id: int) -> List[Dict[str, Any]]:
    """Busca todos os pets de um tutor."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
    pets = cursor.fetchall()
    conn.close()
    return [dict(pet) for pet in pets]

def buscar_pet_por_id(pet_id: int) -> Optional[Dict[str, Any]]:
    """Busca um pet pelo ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
    pet = cursor.fetchone()
    conn.close()
    return dict(pet) if pet else None

def atualizar_pet(pet_id: int, **kwargs) -> bool:
    """Atualiza campos de um pet."""
    conn = conectar_db()
    cursor = conn.cursor()
    set_clauses = []
    values = []
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)

    if not set_clauses:
        conn.close()
        return False

    values.append(pet_id)
    query = f"UPDATE pets SET {', '.join(set_clauses)} WHERE id = ?"

    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

def deletar_pet(pet_id: int) -> bool:
    """Deleta um pet pelo ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

# --- Funções para Avaliações de Dor ---

def buscar_avaliacoes_usuario(usuario_id: int) -> List[Dict[str, Any]]:
    """Busca todas as avaliações de dor de um usuário, incluindo dados do pet."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            a.id AS avaliacao_id,
            a.data_avaliacao,
            a.percentual_dor,
            a.observacoes,
            p.nome AS pet_nome,
            p.especie AS pet_especie
        FROM avaliacoes a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.usuario_id = ?
        ORDER BY a.data_avaliacao DESC
    """, (usuario_id,))
    avaliacoes = cursor.fetchall()
    conn.close()
    return [dict(av) for av in avaliacoes]

def buscar_avaliacao_por_id(avaliacao_id: int) -> Optional[Dict[str, Any]]:
    """Busca uma avaliação de dor pelo ID, incluindo dados do pet."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            a.id AS avaliacao_id,
            a.data_avaliacao,
            a.percentual_dor,
            a.observacoes,
            p.nome AS pet_nome,
            p.especie AS pet_especie,
            p.raca AS pet_raca,
            p.data_nascimento AS pet_data_nascimento,
            p.sexo AS pet_sexo,
            p.peso AS pet_peso
        FROM avaliacoes a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.id = ?
    """, (avaliacao_id,))
    avaliacao = cursor.fetchone()
    conn.close()
    return dict(avaliacao) if avaliacao else None

def deletar_avaliacao(avaliacao_id: int) -> bool:
    """Deleta uma avaliação de dor pelo ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM avaliacoes WHERE id = ?", (avaliacao_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

def buscar_respostas_avaliacao(avaliacao_id: int) -> List[Dict[str, Any]]:
    """Busca as respostas detalhadas de uma avaliação."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pergunta_id, resposta
        FROM avaliacao_respostas
        WHERE avaliacao_id = ?
        ORDER BY id
    """, (avaliacao_id,))
    respostas = cursor.fetchall()
    conn.close()
    return [dict(r) for r in respostas]

# --- Funções para Compartilhamentos ---

def criar_compartilhamento(pet_id: int, tutor_id: int, profissional_id: int, token_acesso: str, data_expiracao: str) -> Optional[int]:
    """Cria um novo registro de compartilhamento de pet."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        data_compartilhamento = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO compartilhamentos_pet (pet_id, tutor_id, profissional_id, data_compartilhamento, ativo, token_acesso, data_expiracao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pet_id, tutor_id, profissional_id, data_compartilhamento, 1, token_acesso, data_expiracao))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def buscar_compartilhamento_por_token(token_acesso: str) -> Optional[Dict[str, Any]]:
    """Busca um compartilhamento pelo token de acesso."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compartilhamentos_pet WHERE token_acesso = ? AND ativo = 1", (token_acesso,))
    compartilhamento = cursor.fetchone()
    conn.close()
    return dict(compartilhamento) if compartilhamento else None

def desativar_compartilhamento(compartilhamento_id: int) -> bool:
    """Desativa um compartilhamento de pet."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE compartilhamentos_pet SET ativo = 0 WHERE id = ?", (compartilhamento_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

# --- Funções para Notificações ---

def criar_notificacao(usuario_id: int, pet_id: int, tipo: str, mensagem: str, nivel_prioridade: int = 2, avaliacao_id: int = None) -> Optional[int]:
    """Cria uma nova notificação."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        data_criacao = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO notificacoes (usuario_id, pet_id, avaliacao_id, tipo, mensagem, nivel_prioridade, data_criacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (usuario_id, pet_id, avaliacao_id, tipo, mensagem, nivel_prioridade, data_criacao))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        return None
    finally:
        conn.close()

def buscar_notificacoes_usuario(usuario_id: int, lidas: bool = False) -> List[Dict[str, Any]]:
    """Busca notificações para um usuário, filtrando por lidas/não lidas."""
    conn = conectar_db()
    cursor = conn.cursor()
    query = """
        SELECT n.*, p.nome AS pet_nome, p.especie AS pet_especie
        FROM notificacoes n
        JOIN pets p ON n.pet_id = p.id
        WHERE n.usuario_id = ?
    """
    params = [usuario_id]
    if not lidas:
        query += " AND n.lida = 0"
    query += " ORDER BY n.data_criacao DESC"

    cursor.execute(query, tuple(params))
    notificacoes = cursor.fetchall()
    conn.close()
    return [dict(n) for n in notificacoes]

def marcar_notificacao_como_lida(notificacao_id: int) -> bool:
    """Marca uma notificação específica como lida."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        data_leitura = datetime.now().isoformat()
        cursor.execute("UPDATE notificacoes SET lida = 1, data_leitura = ? WHERE id = ?", (data_leitura, notificacao_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        return False
    finally:
        conn.close()

def contar_notificacoes_nao_lidas(usuario_id: int) -> int:
    """Conta o número de notificações não lidas para um usuário."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notificacoes WHERE usuario_id = ? AND lida = 0", (usuario_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_estatisticas_usuario(usuario_id: int) -> Dict[str, Any]:
    """Retorna estatísticas básicas das avaliações e pets do usuário."""
    conn = conectar_db()
    cursor = conn.cursor()

    # Total de pets
    cursor.execute("SELECT COUNT(*) FROM pets WHERE tutor_id = ?", (usuario_id,))
    total_pets = cursor.fetchone()[0]

    # Total de avaliações
    cursor.execute("SELECT COUNT(*) FROM avaliacoes WHERE usuario_id = ?", (usuario_id,))
    total_avaliacoes = cursor.fetchone()[0]

    # Estatísticas de percentual de dor
    cursor.execute("""
        SELECT 
            MAX(percentual_dor), 
            MIN(percentual_dor), 
            AVG(percentual_dor)
        FROM avaliacoes 
        WHERE usuario_id = ?
    """, (usuario_id,))
    maior_percentual, menor_percentual, media_percentual = cursor.fetchone()

    conn.close()

    return {
        "total_pets": total_pets,
        "total_avaliacoes": total_avaliacoes,
        "maior_percentual": maior_percentual,
        "menor_percentual": menor_percentual,
        "media_percentual": media_percentual
    }

