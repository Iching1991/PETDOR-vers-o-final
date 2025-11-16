"""
Módulo de páginas da aplicação PET DOR
"""
from pages.login import render_login_page
from pages.cadastro import render_cadastro_page
from pages.recuperar_senha import render_recuperar_senha_page
from pages.reset_senha import render_reset_senha_page
from pages.avaliacao import render_avaliacao_page
from pages.historico import render_historico_page
from pages.conta import render_conta_page

__all__ = [
    'render_login_page',
    'render_cadastro_page',
    'render_recuperar_senha_page',
    'render_reset_senha_page',
    'render_avaliacao_page',
    'render_historico_page',
    'render_conta_page'
]
