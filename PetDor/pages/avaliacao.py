"""
📝 Página de Avaliação de Dor - Design Wellness
Integra sistema modular de espécies (especies/)
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Importa sistema modular de espécies
from especies import get_especies_nomes, get_especie_config
from database.models import salvar_avaliacao
from utils.pdf_generator import gerar_relatorio_pdf
from config import get_nivel_dor

def render_avaliacao_page(usuario):
    """Renderiza página de avaliação com design wellness"""
    # Header
    st.markdown("""
    <div class="wellness-card" style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📝 Nova Avaliação</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Avalie o bem-estar do seu paciente com precisão científica
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Dados do paciente
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">🐾 Dados do Paciente</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        nome_pet = st.text_input(
            "🐕 Nome do Paciente",
            placeholder="Ex: Rex, Luna, Max..

