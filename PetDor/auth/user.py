def cadastrar_usuario(nome, email, senha, confirmar_senha, tipo_usuario="tutor"):
    """
    Cadastra um novo usuário com validação de tipo

    Args:
        nome: Nome do usuário
        email: Email do usuário
        senha: Senha do usuário
        confirmar_senha: Confirmação da senha
        tipo_usuario: Tipo de usuário ('tutor', 'clinica', 'veterinario')

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Validações básicas
        if not all([nome, email, senha, confirmar_senha]):
            return False, "Preencha todos os campos obrigatórios"

        # Validação de tipo de usuário
        tipos_validos = ['tutor', 'clinica', 'veterinario']
        if tipo_usuario not in tipos_validos:
            return False, f"Tipo de usuário inválido. Escolha entre: {', '.join(tipos_validos)}"

        # Validações existentes (nome, email, senha)
        ok_nome, msg_nome = validar_nome(nome)
        if not ok_nome:
            return False, msg_nome

        ok_email, msg_email = validar_email(email)
        if not ok_email:
            return False, msg_email

        ok_senha, msg_senha = validar_senha(senha)
        if not ok_senha:
            return False, msg_senha

        ok_conf, msg_conf = senhas_conferem(senha, confirmar_senha)
        if not ok_conf:
            return False, msg_conf

        # Hash da senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        # Cria usuário com tipo
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Este e-mail já está cadastrado"

        # Insere usuário
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo, tipo_usuario)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (nome, email, senha_hash, data_criacao, tipo_usuario))

        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Usuário cadastrado: {email} (ID: {usuario_id}, Tipo: {tipo_usuario})")

        # Mensagem personalizada baseada no tipo
        tipos_msg = {
            'tutor': "Bem-vindo ao PETDor! Agora você pode cadastrar seus pets e monitorar sua saúde.",
            'clinica': "Bem-vindo ao PETDor! Sua clínica agora pode receber notificações de dor dos pets vinculados.",
            'veterinario': "Bem-vindo ao PETDor! Você receberá notificações de dor dos pets que acompanhar."
        }

        return True, f"Conta criada com sucesso! {tipos_msg.get(tipo_usuario, 'Bem-vindo ao PETDor!')}"

    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, f"Erro interno no sistema: {e}"


def buscar_usuario_por_id(usuario_id):
    """Busca dados completos do usuário incluindo tipo"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo, is_admin, tipo_usuario,
                   data_desativacao, motivo_desativacao
            FROM usuarios 
            WHERE id = ?
        """, (usuario_id,))

        row = cursor.fetchone()

        if row:
            usuario = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'data_criacao': row[3],
                'ativo': bool(row[4]),
                'is_admin': bool(row[5]),
                'tipo_usuario': row[6] or 'tutor',  # Default para usuários antigos
                'data_desativacao': row[7],
                'motivo_desativacao': row[8]
            }
            conn.close()
            return usuario

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None

