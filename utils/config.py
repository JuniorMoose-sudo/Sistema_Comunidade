from typing import Any

import streamlit as st

from database import get_session
from models import Configuracao


def get_config_value(db, key: str, default: Any):
    """Obtém um valor de configuração do banco. Retorna o padrão se não encontrado."""
    config = db.query(Configuracao).filter(Configuracao.chave == key).first()
    if config is not None:
        try:
            return type(default)(config.valor)
        except (ValueError, TypeError):
            return default

    # Se não existe no banco, cria com o valor padrão
    set_config_value(db, key, default)
    return default


def set_config_value(db, key: str, value: Any):
    """Define um valor de configuração no banco."""
    config = db.query(Configuracao).filter(Configuracao.chave == key).first()
    if config:
        config.valor = str(value)
    else:
        config = Configuracao(chave=key, valor=str(value))
        db.add(config)
    db.commit()


@st.cache_data
def load_dynamic_config():
    """Carrega as configurações dinâmicas da paróquia a partir do banco.

    Cacheado para evitar consultas repetidas a cada renderização.
    """
    with get_session() as db:
        key_map = {
            "nome": "nome_paroquia",
            "responsavel": "responsavel_paroquia",
            "telefone": "telefone_paroquia",
            "email": "email_paroquia",
            "data_prestacao_contas": "data_prestacao_contas",
            "coordenador_local": "coordenador_local",
            "limite_aprovacao_comunidade": "limite_aprovacao_comunidade",
        }
        defaults = {
            "nome": "Paróquia São José",
            "responsavel": "Pe. João da Silva",
            "telefone": "(11) 3333-3333",
            "email": "secretaria@paroquiasaojose.org.br",
            "data_prestacao_contas": "05",
            "coordenador_local": "Maria da Silva",
            "limite_aprovacao_comunidade": 5000.00,
        }

        config = {}
        for key, default_val in defaults.items():
            db_key = key_map.get(key, key)
            config[key] = get_config_value(db, db_key, default_val)
        return config

