import re

def validar_email(email: str):
    """
    Valida email e retorna (bool, mensagem)
    """
    if not email or "@" not in email:
        return False, "E-mail inválido."

    # Regex simples
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(padrao, email):
        return False, "Formato de e-mail inválido."

    return True, ""


def validar_senha(senha: str):
    """
    Valida senha e retorna (bool, mensagem)
    """
    if not senha or len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres."
    return True, ""


def validar_nome(nome: str):
    """
    Valida nome e retorna (bool, mensagem)
    """
    if not nome or len(nome.strip()) < 2:
        return False, "O nome deve ter pelo menos 2 caracteres."
    return True, ""


def senhas_conferem(senha: str, confirmar: str):
    """
    Valida se senha == confirmar
    """
    if senha != confirmar:
        return False, "As senhas não conferem."
    return True, ""
