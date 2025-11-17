"""
Modelos de dados do PETDOR
"""

from database.connection import conectar_db

# -------------------------------
# Usuários
# -------------------------------
def buscar_usuario_por_id(usuario_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, data_criacao, ativo FROM usuarios WHERE id = ?", (usuario_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "data_criacao": row["data_criacao"],
            "ativo": bool(row["ativo"])
        }
    return None

def buscar_usuario_por_email(email):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, ativo FROM usuarios WHERE email = ?", (email.lower().strip(),))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "ativo": bool(row["ativo"])
        }
    return None

