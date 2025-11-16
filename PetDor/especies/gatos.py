# especies/gatos.py
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Pergunta:
    texto: str
    invertida: bool = False


class EspecieConfig:
    def __init__(self,
                 nome: str,
                 escala_min: int,
                 escala_max: int,
                 perguntas: List[Pergunta],
                 descricao: str = ""):
        self.nome = nome
        self.escala_min = escala_min
        self.escala_max = escala_max
        self.perguntas = perguntas
        self.descricao = descricao or ""

    def get_labels_escala(self) -> Dict[int, str]:
        """Retorna labels para cada valor da escala (padrão genérico)."""
        # Exemplo simples: trate 0..max como labels — ajuste conforme sua escala real
        labels = {}
        span = self.escala_max - self.escala_min
        for v in range(self.escala_min, self.escala_max + 1):
            if span == 0:
                labels[v] = str(v)
            else:
                pct = (v - self.escala_min) / (span) * 100
                if pct < 33:
                    labels[v] = "Sem dor / Leve"
                elif pct < 66:
                    labels[v] = "Moderada"
                else:
                    labels[v] = "Severa"
        return labels

    def get_pontuacao_maxima(self) -> int:
        """Retorna a pontuação máxima possível (soma das maiores respostas)."""
        # cada pergunta pode atingir escala_max (ou outro peso se quiser)
        return len(self.perguntas) * self.escala_max

    def calcular_percentual(self, pontuacao_total: float) -> float:
        """Converte pontuação total em percentual 0-100."""
        maximo = self.get_pontuacao_maxima()
        if maximo == 0:
            return 0.0
        return (pontuacao_total / maximo) * 100.0


# --- Definição das perguntas de gatos (exemplo) ---
GATOS_PERGUNTAS = [
    Pergunta(texto="Meu gato brinca e interage com outros animais de estimação", invertida=False),
    Pergunta(texto="Meu gato apresenta apetite normal", invertida=False),
    Pergunta(texto="Meu gato evita contato e fica escondido", invertida=True),
    Pergunta(texto="Meu gato vocaliza diferente (miados estranhos)", invertida=False),
    Pergunta(texto="Meu gato demonstra desconforto ao manipular áreas do corpo", invertida=False),
    # adicione/edite as perguntas reais conforme o seu questionário
]

GATOS_DESCRICAO = (
    "Use esta escala para avaliar comportamentos indicativos de dor em felinos. "
    "Responda com base nas últimas 24–48 horas."
)

GATOS_CONFIG = EspecieConfig(
    nome="Gato",
    escala_min=0,
    escala_max=5,
    perguntas=GATOS_PERGUNTAS,
    descricao=GATOS_DESCRICAO
)

