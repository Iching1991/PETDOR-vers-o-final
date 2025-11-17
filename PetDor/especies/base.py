"""
Base para configuração de espécies e perguntas de avaliação de dor.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Pergunta:
    """Representa uma pergunta de avaliação de dor."""
    texto: str
    invertida: bool = False # Se True, uma resposta alta indica MENOS dor (ex: "Meu cão foi brincalhão")
    peso: float = 1.0       # Peso padrão para a pergunta no cálculo da dor

@dataclass
class EspecieConfig:
    """Configuração completa para uma espécie, incluindo perguntas e escala."""
    nome: str
    escala_min: int
    escala_max: int
    descricao: str
    perguntas: List[Pergunta] = field(default_factory=list)

    @property
    def opcoes_escala(self):
        """Retorna as opções de escala para as perguntas (0 a 7, por exemplo)."""
        return [str(i) for i in range(self.escala_min, self.escala_max + 1)]

    def get_pergunta_por_id(self, id_pergunta: str) -> Optional[Pergunta]:
        """Busca uma pergunta pelo seu ID (texto)."""
        for p in self.perguntas:
            if p.texto == id_pergunta:
                return p
        return None
