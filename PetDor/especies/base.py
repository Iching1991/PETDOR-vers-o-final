"""
Módulo base para configuração de espécies e perguntas de avaliação de dor.
Define as classes EspecieConfig e Pergunta.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Pergunta:
    """Representa uma pergunta de avaliação de dor."""
    texto: str
    id: Optional[str] = None # ID único para a pergunta
    invertida: bool = False # Se True, uma resposta alta indica MENOS dor (ex: "Meu cão foi brincalhão")
    peso: float = 1.0       # Peso da pergunta no cálculo da pontuação total

    def __post_init__(self):
        if self.id is None:
            # Gera um ID padrão a partir do texto, se não for fornecido
            self.id = self.texto.lower().replace(" ", "_").replace("?", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c").replace("ã", "a").replace("õ", "o")


@dataclass
class EspecieConfig:
    """Configuração completa para uma espécie, incluindo perguntas e escala."""
    nome: str
    descricao: str
    perguntas: List[Pergunta] = field(default_factory=list)
    # A escala é definida pelas opções de texto. O valor numérico será o índice.
    opcoes_escala: List[str] = field(default_factory=lambda: ["0 - Nunca", "1 - Raramente", "2 - Às vezes", "3 - Frequentemente", "4 - Sempre"]) 

    def get_valor_numerico_resposta(self, resposta_texto: str) -> int:
        """Mapeia uma resposta em texto para seu valor numérico na escala (índice)."""
        try:
            # Remove o prefixo numérico "X - " se existir, para encontrar o índice correto
            clean_resposta_texto = resposta_texto.split(' - ', 1)[-1]
            # Find the index of the clean text in the options
            for i, option in enumerate(self.opcoes_escala):
                if option.split(' - ', 1)[-1] == clean_resposta_texto:
                    return i
            return 0 # Fallback
        except ValueError:
            return 0 # Retorna 0 se a resposta não for encontrada (segurança)

    def get_pontuacao_maxima_por_pergunta(self) -> int:
        """Retorna a pontuação máxima que uma única pergunta pode atingir (N-1)."""
        return len(self.opcoes_escala) - 1

    def calcular_percentual_dor(self, respostas: Dict[str, str]) -> int:
        """
        Calcula o percentual de dor baseado nas respostas das perguntas,
        considerando a configuração da espécie e perguntas invertidas.
        """
        pontuacao_obtida = 0.0
        pontuacao_total_possivel = 0.0

        max_valor_escala = self.get_pontuacao_maxima_por_pergunta()

        for pergunta_obj in self.perguntas:
            pergunta_id = pergunta_obj.id
            resposta_texto = respostas.get(pergunta_id)

            if resposta_texto is None:
                continue

            valor_resposta_numerico = self.get_valor_numerico_resposta(resposta_texto)

            # Aplica a lógica de inversão
            if pergunta_obj.invertida:
                valor_resposta_ponderado = (max_valor_escala - valor_resposta_numerico) * pergunta_obj.peso
            else:
                valor_resposta_ponderado = valor_resposta_numerico * pergunta_obj.peso

            pontuacao_obtida += valor_resposta_ponderado
            pontuacao_total_possivel += max_valor_escala * pergunta_obj.peso # Sempre soma o máximo possível para cada pergunta

        if pontuacao_total_possivel == 0:
            return 0

        percentual = (pontuacao_obtida / pontuacao_total_possivel) * 100
        return int(round(percentual))
