"""
Geração de relatórios em PDF
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from fpdf import FPDF
from datetime import datetime
import os
import tempfile


class PDFRelatorio(FPDF):
    """Classe customizada para relatórios PETDor"""

    def header(self):
        """Cabeçalho do PDF"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'PETDor - Relatório de Avaliação', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


def gerar_relatorio_pdf(pet_nome, especie, percentual, pontuacao_total, 
                        pontuacao_maxima, usuario_nome, idade):
    """
    Gera relatório PDF da avaliação

    Args:
        pet_nome: Nome do pet
        especie: Espécie do pet
        percentual: Percentual de dor
        pontuacao_total: Pontuação obtida
        pontuacao_maxima: Pontuação máxima possível
        usuario_nome: Nome do usuário/veterinário
        idade: Idade do pet

    Returns:
        Caminho do arquivo PDF gerado
    """
    pdf = PDFRelatorio()
    pdf.add_page()

    # Informações do paciente
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Dados do Paciente', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Nome: {pet_nome}', 0, 1)
    pdf.cell(0, 8, f'Espécie: {especie}', 0, 1)
    pdf.cell(0, 8, f'Idade: {idade} anos', 0, 1)
    pdf.cell(0, 8, f'Data da Avaliação: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)
    pdf.cell(0, 8, f'Avaliador: {usuario_nome}', 0, 1)
    pdf.ln(10)

    # Resultado
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Resultado da Avaliação', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Pontuação: {pontuacao_total}/{pontuacao_maxima}', 0, 1)
    pdf.cell(0, 8, f'Percentual de Dor: {percentual:.1f}%', 0, 1)
    pdf.ln(5)

    # Interpretação
    if percentual < 30:
        nivel = "Baixo"
        cor = (40, 167, 69)  # Verde
        recomendacao = "Monitoramento de rotina. Sem sinais significativos de dor."
    elif percentual < 60:
        nivel = "Moderado"
        cor = (255, 193, 7)  # Amarelo
        recomendacao = "Atenção necessária. Considere intervenção veterinária."
    else:
        nivel = "Alto"
        cor = (220, 53, 69)  # Vermelho
        recomendacao = "Intervenção urgente recomendada. Consulte veterinário imediatamente."

    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(*cor)
    pdf.cell(0, 8, f'Nível de Dor: {nivel}', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, f'Recomendação: {recomendacao}')
    pdf.ln(10)

    # Observações
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 5, 
        'Observação: Este relatório é uma ferramenta de apoio à decisão clínica. '
        'A avaliação final deve ser realizada por um médico veterinário qualificado.')

    # Salva em arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)

    return temp_file.name
