"""
Script para popular o banco de dados com dados de exemplo
para todas as tabelas, facilitando testes de todas as funções.

Uso recomendado (após ativar o venv):

    python reset_database.py
    python seed_database.py

Em seguida, rode:

    streamlit run app.py
"""

from datetime import date, timedelta

from database import get_session
from models import (
    LancamentoFinanceiro,
    Fiel,
    Projeto,
    AtaReuniao,
    Configuracao,
    RepasseParoquia,
)


def seed_configuracoes(db):
    """Configurações básicas da paróquia usadas pelo sistema."""
    configs = {
        "nome_paroquia": "Paróquia São José",
        "responsavel_paroquia": "Pe. João da Silva",
        "telefone_paroquia": "(11) 3333-3333",
        "email_paroquia": "secretaria@paroquiasaojose.org.br",
        "data_prestacao_contas": "05",
        "coordenador_local": "Maria da Silva",
        "limite_aprovacao_comunidade": "5000.00",
    }

    for chave, valor in configs.items():
        existing = (
            db.query(Configuracao)
            .filter(Configuracao.chave == chave)
            .first()
        )
        if existing:
            existing.valor = str(valor)
        else:
            db.add(Configuracao(chave=chave, valor=str(valor)))


def seed_fieis(db):
    hoje = date.today()
    fieis = [
        Fiel(
            nome="João da Silva",
            telefone="(11) 99999-0001",
            email="joao@example.com",
            endereco="Rua A, 123",
            familia="Silva",
            batismo=True,
            eucaristia=True,
            crisma=True,
            matrimonio=True,
            dizimista=True,
            ministrios="Coral, Liturgia",
            data_cadastro=hoje - timedelta(days=60),
            ativo=True,
            observacoes="Coordenador de liturgia.",
        ),
        Fiel(
            nome="Maria Oliveira",
            telefone="(11) 99999-0002",
            email="maria@example.com",
            endereco="Rua B, 456",
            familia="Oliveira",
            batismo=True,
            eucaristia=True,
            crisma=True,
            matrimonio=False,
            dizimista=True,
            ministrios="Catequese",
            data_cadastro=hoje - timedelta(days=30),
            ativo=True,
            observacoes="Catequista.",
        ),
        Fiel(
            nome="Carlos Souza",
            telefone="(11) 99999-0003",
            email="carlos@example.com",
            endereco="Rua C, 789",
            familia="Souza",
            batismo=True,
            eucaristia=False,
            crisma=False,
            matrimonio=False,
            dizimista=False,
            ministrios="",
            data_cadastro=hoje - timedelta(days=10),
            ativo=True,
            observacoes="Novo na comunidade.",
        ),
        Fiel(
            nome="Ana Pereira",
            telefone="(11) 99999-0004",
            email="ana@example.com",
            endereco="Rua D, 101",
            familia="Pereira",
            batismo=True,
            eucaristia=True,
            crisma=False,
            matrimonio=False,
            dizimista=True,
            ministrios="Jovens",
            data_cadastro=hoje - timedelta(days=5),
            ativo=True,
            observacoes="Participa do grupo de jovens.",
        ),
    ]
    db.add_all(fieis)


def _mes_ano_relativo(meses_atras: int) -> date:
    """Retorna uma data no dia 10, N meses atrás a partir de hoje."""
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month - meses_atras
    while mes <= 0:
        mes += 12
        ano -= 1
    return date(ano, mes, 10)


def seed_lancamentos_financeiros(db):
    """Cria lançamentos de entradas e saídas nos últimos 6 meses."""
    lancamentos = []

    categorias_entradas = ["Dízimo", "Oferta", "Doação", "Eventos"]
    categorias_saidas = ["Manutenção", "Eventos", "Caridade", "Administrativo"]

    for meses_atras in range(0, 6):
        data_base = _mes_ano_relativo(meses_atras)

        # Entradas
        for i, cat in enumerate(categorias_entradas):
            lancamentos.append(
                LancamentoFinanceiro(
                    data=data_base + timedelta(days=i),
                    categoria=cat,
                    tipo="Entrada",
                    valor=100.0 + (meses_atras * 20) + i * 10,
                    descricao=f"{cat} - mês -{meses_atras}",
                    comprovante=f"E{meses_atras}{i}",
                    aprovado=True,
                )
            )

        # Saídas
        for i, cat in enumerate(categorias_saidas):
            lancamentos.append(
                LancamentoFinanceiro(
                    data=data_base + timedelta(days=10 + i),
                    categoria=cat,
                    tipo="Saída",
                    valor=50.0 + (meses_atras * 15) + i * 5,
                    descricao=f"{cat} - mês -{meses_atras}",
                    comprovante=f"S{meses_atras}{i}",
                    aprovado=True,
                )
            )

    db.add_all(lancamentos)


def seed_projetos(db):
    hoje = date.today()
    projetos = [
        Projeto(
            nome="Reforma do Telhado",
            tipo="Reforma/Estrutural",
            descricao="Troca completa do telhado da igreja.",
            custo_estimado=20000.0,
            custo_real=5000.0,
            prazo=hoje.replace(month=hoje.month + 2 if hoje.month <= 10 else 12),
            prioridade="Urgente",
            status="Em Andamento",
            aprovado_paroquia=True,
            data_inicio=hoje - timedelta(days=20),
        ),
        Projeto(
            nome="Compra de Cadeiras",
            tipo="Equipamentos",
            descricao="Aquisição de novas cadeiras para o salão.",
            custo_estimado=5000.0,
            custo_real=0.0,
            prazo=hoje.replace(month=hoje.month + 1 if hoje.month <= 11 else 12),
            prioridade="Alta",
            status="Planejamento",
            aprovado_paroquia=False,
        ),
        Projeto(
            nome="Retiro Espiritual",
            tipo="Evento",
            descricao="Retiro anual da comunidade.",
            custo_estimado=8000.0,
            custo_real=8000.0,
            prazo=hoje - timedelta(days=60),
            prioridade="Média",
            status="Concluído",
            aprovado_paroquia=True,
            data_inicio=hoje - timedelta(days=90),
            data_conclusao=hoje - timedelta(days=60),
        ),
        Projeto(
            nome="Projeto Social com Moradores de Rua",
            tipo="Ação Social",
            descricao="Atendimento semanal a moradores de rua.",
            custo_estimado=3000.0,
            custo_real=1000.0,
            prazo=None,
            prioridade="Alta",
            status="Em Andamento",
            aprovado_paroquia=True,
            data_inicio=hoje - timedelta(days=10),
        ),
    ]
    db.add_all(projetos)


def seed_atas(db):
    hoje = date.today()
    atas = [
        AtaReuniao(
            data_reuniao=hoje - timedelta(days=45),
            tipo="Reunião do Conselho",
            participantes="João; Maria; Carlos",
            decisoes="Aprovar reforma do telhado.",
            acoes="Obter orçamentos; definir cronograma.",
            responsaveis="João; Equipe de Obras",
        ),
        AtaReuniao(
            data_reuniao=hoje - timedelta(days=20),
            tipo="Reunião de Pastoral",
            participantes="Maria; Ana",
            decisoes="Planejar retiro espiritual.",
            acoes="Reservar local; preparar cronograma.",
            responsaveis="Maria; Equipe de Pastoral",
        ),
        AtaReuniao(
            data_reuniao=hoje - timedelta(days=5),
            tipo="Reunião Financeira",
            participantes="Tesoureiro; Coordenador",
            decisoes="Definir repasse paroquial e orçamento mensal.",
            acoes="Registrar lançamentos; enviar relatório à paróquia.",
            responsaveis="Tesoureiro",
        ),
    ]
    db.add_all(atas)


def seed_repasses_paroquia(db):
    hoje = date.today()
    repasses = []
    for meses_atras, valor in [(1, 1500.0), (2, 1300.0), (3, 1600.0)]:
        data_repasse = _mes_ano_relativo(meses_atras)
        mes_ano = data_repasse.strftime("%m/%Y")
        repasses.append(
            RepasseParoquia(
                mes_ano=mes_ano,
                valor_repassado=valor,
                data_repasse=data_repasse,
                comprovante=f"REP-{mes_ano}",
                observacoes="Repasse mensal à paróquia.",
            )
        )
    db.add_all(repasses)


def seed_database():
    print("🌱 Iniciando população do banco de dados com dados de exemplo...")
    with get_session() as db:
        seed_configuracoes(db)
        seed_fieis(db)
        seed_lancamentos_financeiros(db)
        seed_projetos(db)
        seed_atas(db)
        seed_repasses_paroquia(db)

        db.commit()

    print("✅ Banco de dados populado com sucesso!")


if __name__ == "__main__":
    seed_database()

