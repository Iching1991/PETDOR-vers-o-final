import re

def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida o formato do e-mail.
    Retorna (True, "") se válido, ou (False, mensagem de erro) se inválido.
    """
    if not email or not email.strip():
        return False, "O e-mail não pode estar vazio."

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return False, "Formato de e-mail inválido."

    return True, ""


def validar_senha(senha: str) -> tuple[bool, str]:
    """
    Valida a senha.
    Critérios: mínimo 6 caracteres.
    Retorna (True, "") se válido, ou (False, mensagem de erro) se inválido.
    """
    if not senha or len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres."
    return True, ""


def validar_nome(nome: str) -> tuple[bool, str]:
    """
    Valida o nome do usuário.
    Deve ter ao menos 2 caracteres e não estar vazio.
    """
    if not nome or len(nome.strip()) < 2:
        return False, "O nome deve ter pelo menos 2 caracteres."
    return True, ""


def senhas_conferem(senha1: str, senha2: str) -> tuple[bool, str]:
    """
    Confere se as duas senhas são iguais.
    """
    if senha1 != senha2:
        return False, "As senhas não conferem."
    return True, ""
