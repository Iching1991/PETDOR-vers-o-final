# Adicionar no início do arquivo models.py, na função get_estatisticas_usuario:

def get_estatisticas_usuario(usuario_id):
    """Obtém estatísticas do usuário"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Busca tipo de usuário
        cursor.execute("""
            SELECT tipo_usuario FROM usuarios WHERE id = ?
        """, (usuario_id,))

        row = cursor.fetchone()
        tipo_usuario = row[0] if row else None

        # Resto das estatísticas...
        # (manter o código existente)

        stats = {
            'total_avaliacoes': total_avaliacoes,
            'total_pets': total_pets,
            'media_percentual': media_percentual,
            'tipo_usuario': tipo_usuario  # Novo campo
        }

        conn.close()
        return stats

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return None
