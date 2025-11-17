# ... (imports e outras funções existentes) ...

def criar_tabela_avaliacao_respostas():
    """Cria a tabela para armazenar as respostas das perguntas de avaliação."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacao_respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                avaliacao_id INTEGER NOT NULL,
                pergunta_id TEXT NOT NULL,
                resposta TEXT NOT NULL,
                FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Tabela 'avaliacao_respostas' criada/verificada")
        print("✅ Tabela 'avaliacao_respostas' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela avaliacao_respostas: {e}")
        print(f"❌ Erro: {e}")
        return False

def migrar_banco_completo():
    """Executa todas as migrações do banco de dados"""
    print("\n🔄 Executando migrações completas do PETDor...\n")
    migracoes = [
        # ... (suas outras migrações) ...
        ("Tabela de respostas de avaliação", criar_tabela_avaliacao_respostas), # Adicione esta linha
    ]
    # ... (resto da função migrar_banco_completo) ...
