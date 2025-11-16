"""
Funções de validação utilizadas no PETDor.
"""

def validar_email(email: str) -> bool:
    """
    Valida o formato básico de um e-mail.
    Aqui pode ser simples, pois a validação final é feita no servidor SMTP.
    """
    if not email or "@" not in email or "." not in email:
        return False
    return True


def validar_senha(senha: str) -> bool:
    """
    A senha deve ter pelo menos 6 caracteres.
    """
    return senha is not None and len(senha) >= 6


def validar_nome(nome: str) -> bool:
    """
    O nome deve ter pelo menos 2 caracteres reais.
    """
    return nome is not None and len(nome.strip()) >= 2
