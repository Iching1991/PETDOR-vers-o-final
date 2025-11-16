# especies/__init__.py
from .gatos import GATOS_CONFIG
from .gatos import Pergunta, EspecieConfig  # exportar para compatibilidade (se necessário)

_ESPECIES_MAP = {
    "Gato": GATOS_CONFIG,
    # adicione aqui outras espécies: "Cão": CAO_CONFIG, etc.
}


def get_especies_nomes():
    """Retorna lista de nomes de espécies disponíveis."""
    return list(_ESPECIES_MAP.keys())


def get_especie_config(nome: str):
    """Retorna o objeto EspecieConfig para a espécie solicitada.
    Lança KeyError se não existir.
    """
    if nome not in _ESPECIES_MAP:
        raise KeyError(f"Espécie '{nome}' não encontrada")
    return _ESPECIES_MAP[nome]
