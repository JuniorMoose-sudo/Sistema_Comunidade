import streamlit as st

from database import get_session
from models import Projeto
from utils.logger import get_logger


logger = get_logger(__name__)


def salvar_projeto(projeto_data):
    with get_session() as db:
        projeto = Projeto(**projeto_data)
        db.add(projeto)
        db.commit()
        db.refresh(projeto)

    logger.info(
        "Novo projeto salvo: id=%s, nome=%s, status=%s",
        projeto.id,
        projeto.nome,
        projeto.status,
    )
    return projeto


@st.cache_data(ttl=60)
def obter_projetos_por_status(status=None):
    """Retorna lista de projetos filtrados por status (ou todos).

    Resultado é cacheado por 60 segundos para aliviar o banco.
    """
    with get_session() as db:
        query = db.query(Projeto)
        if status:
            query = query.filter(Projeto.status == status)
        return query.order_by(Projeto.prioridade.desc()).all()

