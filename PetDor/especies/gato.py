"""
🐈 Configuração de avaliação para GATOS
Escala: 0 a 7 (baseada em Feline Grimace Scale e Glasgow Composite Pain Scale)
"""
from especies.base import EspecieConfig, Pergunta

CONFIG_GATOS = EspecieConfig(
    nome="Gato",
    descricao="Avaliação de dor em gatos - Escala de 0 (nunca) a 7 (sempre)",
    opcoes_escala=[
        "0 - Nunca", "1 - Raramente", "2 - Às vezes", "3 - Frequentemente",
        "4 - Quase Sempre", "5 - Sempre", "6 - Muito Frequente", "7 - Constante"
    ],
    perguntas=[
        # Postura e Atividade
        Pergunta(texto="Meu gato está com postura anormal (encolhido, rígido)", invertida=False, peso=1.0),
        Pergunta(texto="Meu gato está menos ativo ou brincalhão", invertida=False, peso=1.0),
        Pergunta(texto="Meu gato evita saltar ou subir em lugares", invertida=False, peso=1.0),
        # Alimentação e Higiene
        Pergunta(texto="O apetite do meu gato reduziu", invertida=False, peso=1.0),
        Pergunta(texto="Meu gato está se lambendo menos ou com dificuldade", invertida=False, peso=1.0),
        # Comportamento Social e Interação
        Pergunta(texto="Meu gato se esconde mais ou evita contato", invertida=False, peso=1.0),
        Pergunta(texto="Meu gato reage com dor ou agressividade ao toque", invertida=False, peso=1.0),
        Pergunta(texto="Meu gato mia mais ou com vocalização diferente", invertida=False, peso=1.0),
        # Sono e Conforto
        Pergunta(texto="Meu gato tem dificuldade para ficar confortável ou dormir", invertida=False, peso=1.0),
        Pergunta(texto="Meu gato dormiu bem durante a noite", invertida=False, peso=1.0),
    ]
)

