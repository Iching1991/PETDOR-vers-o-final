def adicionar_campos_confirmacao_email():
    """Adiciona campos para confirmação de email"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'email_confirmado' not in colunas:
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN email_confirmado INTEGER DEFAULT 0
            """)
            print("✅ Campo 'email_confirmado' adicionado")

        if 'token_confirmacao' not in colunas:
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN token_confirmacao TEXT UNIQUE
            """)
            print("✅ Campo 'token_confirmacao' adicionado")

        if 'data_expiracao_token' not in colunas:
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN data_expiracao_token TEXT
            """)
            print("✅ Campo 'data_expiracao_token' adicionado")

        conn.commit()
        conn.close()
        logger.info("Campos de confirmação de email adicionados")
        return True

    except Exception as e:
        logger.error(f"Erro ao adicionar campos de confirmação: {e}")
        print(f"❌ Erro: {e}")
        return False


def migrar_banco_completo():
    """Executa todas as migrações"""
    print("🔄 Executando migrações completas...")

    adicionar_colunas_desativacao()
    adicionar_campo_admin()
    adicionar_campo_tipo_usuario()
    adicionar_campos_confirmacao_email()  # Nova migração
    criar_tabela_compartilhamentos()
    criar_tabela_notificacoes()

    print("✅ Todas as migrações concluídas!")
