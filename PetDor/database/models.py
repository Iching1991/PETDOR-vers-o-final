def vincular_profissional_ao_pet(pet_id, usuario_id, tipo_vinculo):
    """
    Vincula um profissional (clínica/veterinário) a um pet

    Args:
        pet_id: ID do pet
        usuario_id: ID do profissional
        tipo_vinculo: 'clinica' ou 'veterinario'

    Returns:
        Tupla (sucesso, mensagem, vinculo_id)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se pet existe
        cursor.execute("SELECT id FROM pets WHERE id = ?", (pet_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Pet não encontrado", None

        # Verifica se usuário é do tipo correto
        cursor.execute("""
            SELECT id, tipo_usuario FROM usuarios 
            WHERE id = ? AND tipo_usuario IN ('clinica', 'veterinario')
        """, (usuario_id,))

        row = cursor.fetchone()
        if not row or row[1] != tipo_vinculo:
            conn.close()
            return False, f"Usuário deve ser do tipo {tipo_vinculo}", None

        # Verifica se vínculo já existe
        cursor.execute("""
            SELECT id FROM vinculos_pets 
            WHERE pet_id = ? AND usuario_id = ? AND tipo_vinculo = ?
        """, (pet_id, usuario_id, tipo_vinculo))

        if cursor.fetchone():
            conn.close()
            return False, "Este profissional já está vinculado a este pet", None

        # Cria vínculo
        cursor.execute("""
            INSERT INTO vinculos_pets (pet_id, usuario_id, tipo_vinculo, ativo)
            VALUES (?, ?, ?, 1)
        """, (pet_id, usuario_id, tipo_vinculo))

        vinculo_id = cursor.lastrowid

        # Cria notificação para o tutor (se existir)
        cursor.execute("""
            SELECT u.id FROM vinculos_pets vp
            JOIN usuarios u ON vp.usuario_id = u.id
            WHERE vp.pet_id = ? AND vp.tipo_vinculo = 'tutor'
        """, (pet_id,))

        tutor_row = cursor.fetchone()
        if tutor_row:
            tutor_id = tutor_row[0]
            cursor.execute("""
                INSERT INTO notificacoes (pet_id, usuario_id_destino, tipo_notificacao, 
                                        nivel_prioridade, mensagem)
                VALUES (?, ?, 'vinculo_criado', 2, ?)
            """, (pet_id, tutor_id, f"Novo profissional vinculado ao pet: {tipo_vinculo}"))

        conn.commit()
        conn.close()

        logger.info(f"Vínculo criado: Pet {pet_id} - {tipo_vinculo} {usuario_id} (ID: {vinculo_id})")
        return True, f"Profissional vinculado com sucesso!", vinculo_id

    except Exception as e:
        logger.error(f"Erro ao vincular profissional: {e}")
        return False, f"Erro ao vincular profissional: {e}", None


def desvincular_profissional_do_pet(pet_id, usuario_id, tipo_vinculo):
    """Remove vínculo entre pet e profissional"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Desativa vínculo (soft delete)
        cursor.execute("""
            UPDATE vinculos_pets 
            SET ativo = 0, data_desativacao = CURRENT_TIMESTAMP
            WHERE pet_id = ? AND usuario_id = ? AND tipo_vinculo = ? AND ativo = 1
        """, (pet_id, usuario_id, tipo_vinculo))

        afetados = cursor.rowcount

        if afetados > 0:
            conn.commit()
            conn.close()
            logger.info(f"Vínculo desativado: Pet {pet_id} - {tipo_vinculo} {usuario_id}")
            return True, "Profissional desvinculado com sucesso!", afetados
        else:
            conn.close()
            return False, "Vínculo não encontrado", 0

    except Exception as e:
        logger.error(f"Erro ao desvincular: {e}")
        return False, f"Erro ao desvincular: {e}", 0


def listar_profissionais_do_pet(pet_id):
    """Lista todos os profissionais vinculados a um pet"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.tipo_usuario, vp.data_criacao, vp.ativo
            FROM vinculos_pets vp
            JOIN usuarios u ON vp.usuario_id = u.id
            WHERE vp.pet_id = ? AND vp.ativo = 1 AND u.tipo_usuario IN ('clinica', 'veterinario')
            ORDER BY vp.data_criacao DESC
        """, (pet_id,))

        profissionais = []
        for row in cursor.fetchall():
            profissionais.append({
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'tipo': row[3],
                'data_vinculo': row[4],
                'ativo': bool(row[5])
            })

        conn.close()
        return profissionais

    except Exception as e:
        logger.error(f"Erro ao listar profissionais: {e}")
        return []


def listar_pets_do_profissional(usuario_id):
    """Lista todos os pets vinculados a um profissional"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT p.id, p.nome, p.especie, p.raca, p.idade, p.peso, u.nome as tutor_nome,
                   vp.data_criacao as data_vinculo
            FROM vinculos_pets vp
            JOIN pets p ON vp.pet_id = p.id
            JOIN usuarios u ON p.tutor_id = u.id
            WHERE vp.usuario_id = ? AND vp.ativo = 1 AND vp.tipo_vinculo IN ('clinica', 'veterinario')
            ORDER BY vp.data_criacao DESC
        """, (usuario_id,))

        pets = []
        for row in cursor.fetchall():
            pets.append({
                'id': row[0],
                'nome': row[1],
                'especie': row[2],
                'raca': row[3],
                'idade': row[4],
                'peso': row[5],
                'tutor_nome': row[6],
                'data_vinculo': row[7]
            })

        conn.close()
        return pets

    except Exception as e:
        logger.error(f"Erro ao listar pets do profissional: {e}")
        return []
