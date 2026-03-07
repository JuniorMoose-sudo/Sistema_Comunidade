from sqlalchemy import func, extract, case

from database import get_session
from models import LancamentoFinanceiro
from utils.logger import get_logger


logger = get_logger(__name__)


def salvar_lancamento(lancamento_data):
    with get_session() as db:
        lancamento = LancamentoFinanceiro(**lancamento_data)
        db.add(lancamento)
        db.commit()
        db.refresh(lancamento)

    logger.info(
        "Novo lançamento financeiro salvo: id=%s, tipo=%s, valor=%s",
        lancamento.id,
        lancamento.tipo,
        lancamento.valor,
    )
    return lancamento


def obter_lancamentos(mes=None, ano=None):
    with get_session() as db:
        query = db.query(LancamentoFinanceiro)

        if mes and ano:
            query = query.filter(
                extract('month', LancamentoFinanceiro.data) == mes,
                extract('year', LancamentoFinanceiro.data) == ano,
            )

        return query.order_by(LancamentoFinanceiro.data.desc()).all()


def calcular_dashboard_financeiro():
    """Calcula totais de entrada e saldo geral em consulta única para o dashboard."""
    with get_session() as db:
        resultados = db.query(
            func.sum(
                case(
                    (LancamentoFinanceiro.tipo == 'Entrada', LancamentoFinanceiro.valor),
                    else_=0,
                )
            ).label('total_entradas'),
            func.sum(
                case(
                    (LancamentoFinanceiro.tipo == 'Saída', LancamentoFinanceiro.valor),
                    else_=0,
                )
            ).label('total_saidas'),
        ).one()

        total_entradas = resultados.total_entradas or 0
        total_saidas = resultados.total_saidas or 0
        saldo_total = total_entradas - total_saidas

        return total_entradas, saldo_total


def calcular_totais_periodo(mes, ano):
    """Calcula totais de entrada e saída para um período específico (Relatórios)."""
    with get_session() as db:
        query = db.query(
            func.sum(
                case(
                    (LancamentoFinanceiro.tipo == 'Entrada', LancamentoFinanceiro.valor),
                    else_=0,
                )
            ).label('entradas_periodo'),
            func.sum(
                case(
                    (LancamentoFinanceiro.tipo == 'Saída', LancamentoFinanceiro.valor),
                    else_=0,
                )
            ).label('saidas_periodo'),
        ).filter(
            extract('month', LancamentoFinanceiro.data) == mes,
            extract('year', LancamentoFinanceiro.data) == ano,
        )

        resultados = query.one()
        entradas = resultados.entradas_periodo or 0
        saidas = resultados.saidas_periodo or 0

        return entradas, saidas

