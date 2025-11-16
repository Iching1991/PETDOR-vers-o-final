# utils/validators.py

import re

def validar_email(email: str) -> tuple[bool, str]:
    if not email or "@" not in email:
        return False, "E-mail inválido."
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(regex, email):
        return False, "Formato de e-mail incorreto."
    return True, "E-mail válido."

def validar_senha(senha: str) -> tuple[bool, str]:
    if not senha or len(senha) < 6:
        return False, "A senha deve ter ao menos 6 caracteres."
    return True, "Senha válida."

def validar_nome(nome: str) -> tuple[bool, str]:
    if not nome or len(nome.strip()) < 2:
        return False, "O nome deve ter ao menos 2 caracteres."
    return True, "Nome válido."

def senhas_conferem(senha: str, confirmar_senha: str) -> tuple[bool, str]:
    if senha != confirmar_senha:
        return False, "As senhas não conferem."
    return True, "Senhas conferem."


