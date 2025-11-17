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
    id: Optional[str] = None # ID único para a pergunta, se necessário
    invertida: bool = False # Se a pontuação da pergunta deve ser invertida (ex: "pouca energia" -> mais dor)
    peso: float = 1.0 # Peso da pergunta no cálculo da pontuação total (pode ser ajustado)

    def __post_init__(self):
        if self.id is None:
            # Gera um ID padrão a partir do texto, se não for fornecido
            self.id = self.texto.lower().replace(" ", "_").replace("?", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c").replace("ã", "a").replace("õ", "o")


@dataclass
class EspecieConfig:
    """Configuração completa para uma espécie, incluindo escala e perguntas."""
    nome: str
    escala_min: int
    escala_max: int
    descricao: str
    perguntas: List[Pergunta] = field(default_factory=list)
    opcoes_escala: List[str] = field(default_factory=lambda: ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]) # Escala padrão de 0 a 4
    # Você pode adicionar mais campos aqui, como imagens de referência, etc.
