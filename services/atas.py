from sqlalchemy import extract

from database import get_session
from models import AtaReuniao


def salvar_ata(ata_data):
    """Salva uma nova ata de reunião no banco de dados."""
    with get_session() as db:
        ata = AtaReuniao(**ata_data)
        db.add(ata)
        db.commit()
        db.refresh(ata)
    return ata


def obter_atas():
    """Obtém todas as atas de reunião ordenadas por data."""
    with get_session() as db:
        return db.query(AtaReuniao).order_by(AtaReuniao.data_reuniao.desc()).all()


def obter_atas_por_periodo(mes=None, ano=None):
    """Obtém as atas de reunião para um período específico, ordenadas por data."""
    with get_session() as db:
        query = db.query(AtaReuniao)
        if mes and ano:
            query = query.filter(
                extract('month', AtaReuniao.data_reuniao) == mes,
                extract('year', AtaReuniao.data_reuniao) == ano,
            )
        return query.order_by(AtaReuniao.data_reuniao.desc()).all()

