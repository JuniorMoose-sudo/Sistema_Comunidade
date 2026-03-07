from sqlalchemy import func, case
import streamlit as st

from database import get_session
from models import Fiel


def salvar_fiel(fiel_data):
    with get_session() as db:
        fiel = Fiel(**fiel_data)
        db.add(fiel)
        db.commit()
        db.refresh(fiel)
    return fiel


@st.cache_data(ttl=60)
def contar_fieis():
    """
    Retorna (total_de_fieis, total_dizimistas) em uma única consulta agregada.
    Resultado é cacheado por 60 segundos.
    """
    with get_session() as db:
        resultado = db.query(
            func.count(Fiel.id).label("total"),
            func.sum(
                case((Fiel.dizimista.is_(True), 1), else_=0)
            ).label("dizimistas"),
        ).one()

        total = resultado.total or 0
        dizimistas = resultado.dizimistas or 0
        return total, dizimistas

