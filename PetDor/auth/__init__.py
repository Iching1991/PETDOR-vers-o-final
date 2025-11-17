"""
Modulo de autenticacao do PETDor
"""
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from .user import (
    cadastrar_usuario,
    autenticar_usuario,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    atualizar_usuario,
    alterar_senha,
    deletar_usuario
)

__all__ = [
    'cadastrar_usuario',
    'autenticar_usuario',
    'buscar_usuario_por_id',
    'buscar_usuario_por_email',
    'atualizar_usuario',
    'alterar_senha',
    'deletar_usuario'
]
