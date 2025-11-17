from .connection import conectar_db

def migrar_banco_completo():
    """Cria todas as tabelas necessárias do PETDOR."""
    conn = conectar_db()
    cursor = conn.cursor()

    # Usuários (veterinários / tutores)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            tipo TEXT NOT NULL, -- tutor / veterinario
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Avaliações de dor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            animal_nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            escala TEXT NOT NULL,
            pontuacao INTEGER NOT NULL,
            observacoes TEXT,
            enviado_para_vet INTEGER DEFAULT 0,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Tokens para recuperação de senha
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            valido_ate DATETIME NOT NULL,
            usado INTEGER DEFAULT 0,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()

