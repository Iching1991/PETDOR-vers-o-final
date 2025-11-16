"""
Validators para o PETDor
Contém funções de validação para:
- e-mail
- senha
- nome de usuário
- confirmação de senha
"""

import re

def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida um e-mail simples.
    Retorna (True, "") se válido, ou (False, mensagem) se inválido.
    """
    if not email or not email.strip():
        return False, "O e-mail não pode estar vazio."
    
    # Regex simples de validação de e-mail
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if re.match(padrao, email):
        return True, ""
    return False, "Formato de e-mail inválido."

def validar_senha(senha: str) -> tuple[bool, str]:
    """
    Valida a senha.
    Deve ter pelo menos 6 caracteres.
    """
    if not senha:
        return False, "A senha não pode estar vazia."
    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    return True, ""

def validar_nome(nome: str) -> tuple[bool, str]:
    """
    Valida o nome do usuário.
    Deve ter pelo menos 2 caracteres não vazios.
    """
    if not nome or len(nome.strip()) < 2:
        return False, "O nome deve ter pelo menos 2 caracteres."
    return True, ""

def senhas_conferem(senha1: str, senha2: str) -> tuple[bool, str]:
    """
    Verifica se duas senhas conferem.
    """
    if senha1 != senha2:
        return False, "As senhas não conferem."
    return True, ""
