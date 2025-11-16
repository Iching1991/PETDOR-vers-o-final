"""
validators.py - Pacote utilitário PETDor
Validações para autenticação e cadastro de usuários
"""

import re

def validar_email(email: str) -> tuple[bool, str]:
    """Valida e-mail; retorna (True, "") se válido ou (False, mensagem) se inválido"""
    if not email or not email.strip():
        return False, "O e-mail não pode estar vazio."
    
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if re.match(padrao, email):
        return True, ""
    
    return False, "Formato de e-mail inválido."

def validar_senha(senha: str) -> tuple[bool, str]:
    """Valida senha mínima de 6 caracteres"""
    if not senha:
        return False, "A senha não pode estar vazia."
    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    return True, ""

def validar_nome(nome: str) -> tuple[bool, str]:
    """Valida nome do usuário com pelo menos 2 caracteres não vazios"""
    if not nome or len(nome.strip()) < 2:
        return False, "O nome deve ter pelo menos 2 caracteres."
    return True, ""

def senhas_conferem(senha1: str, senha2: str) -> tuple[bool, str]:
    """Confirma se duas senhas conferem"""
    if senha1 != senha2:
        return False, "As senhas não conferem."
    return True, ""
