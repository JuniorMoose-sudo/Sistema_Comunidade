import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import calendar
from io import BytesIO
from sqlalchemy import func, extract, case

# Importar módulos do projeto
from database import init_db, get_session
from models import (
    LancamentoFinanceiro,
    Fiel,
    Projeto,
    AtaReuniao,
    Configuracao,
)
from auth import require_login, can_write
from services.financeiro import (
    salvar_lancamento,
    obter_lancamentos,
    calcular_dashboard_financeiro,
    calcular_totais_periodo,
)
from services.fieis import salvar_fiel, contar_fieis
from services.projetos import salvar_projeto, obter_projetos_por_status
from services.atas import salvar_ata, obter_atas, obter_atas_por_periodo
from utils.pdf import gerar_relatorio_pdf
from utils.config import load_dynamic_config, set_config_value
from components.ui import render_header, render_metric_card

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Gestão Comunitária Católica",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar banco de dados e autenticação
init_db()
require_login()  # Força o login

# --- CONSTANTES E CONFIGURAÇÕES ---
PARISH_INFO = load_dynamic_config()


# Função para login/logout


# Funções para lançamentos financeiros foram extraídas para services.financeiro

# Funções de fiéis, projetos, atas e PDF foram extraídas para services/ e utils/pdf.py

def render_sidebar_userinfo():
    """Colocar isso dentro do with st.sidebar: do seu layout."""
    if "auth" in st.session_state and st.session_state["auth"] is not None:
        st.markdown(f"👤 **Logado como:** {st.session_state['auth']['name']}  \n({st.session_state['auth']['role']})")
        if st.button("Sair"):
            st.session_state["auth"] = None
            st.rerun()
    else:
        st.write("Não autenticado")

def build_menu_options():
    """Retorna lista de opções do menu dependendo do papel do usuário."""
    opcoes = ["🏠 Dashboard", "💰 Finanças", "👥 Fiéis", "🏗️ Projetos", "📝 Atas de Reunião", "📊 Relatórios"]
    if can_write():
        opcoes.append("⚙️ Configurações")
    return opcoes

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .community-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #3B82F6;
    }
    .warning-card {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #F59E0B;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #10B981 0%, #3B82F6 100%);
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
render_header(PARISH_INFO)

# --- BARRA LATERAL ---
with st.sidebar:
    render_sidebar_userinfo() # Added
    st.image("https://img.icons8.com/color/96/000000/church.png", width=80)
    st.title("🏛️ Menu")

    menu = st.radio(
        "Navegação",
        build_menu_options(), # Changed to use build_menu_options()
        index=0,
        label_visibility="collapsed"
    )
    st.markdown("---")

    # Informações da comunidade
    st.markdown("### ℹ️ Informações")
    st.info(f"**Coordenador:** {PARISH_INFO['coordenador_local']}")

    # Próxima prestação de contas
    hoje = date.today()
    dia_repasses = int(PARISH_INFO['data_prestacao_contas'])

    if hoje.day > dia_repasses:
        proximo_mes = hoje.month + 1 if hoje.month < 12 else 1
        ano = hoje.year if hoje.month < 12 else hoje.year + 1
        proxima_data = date(ano, proximo_mes, dia_repasses)
    else:
        proxima_data = date(hoje.year, hoje.month, dia_repasses)

    dias_restantes = (proxima_data - hoje).days

    st.markdown(f"""
    <div class="warning-card">
        <strong>⏰ Próxima prestação:</strong><br>
        {proxima_data.strftime('%d/%m/%Y')}<br>
        <small>({dias_restantes} dias restantes)</small>
    </div>
    """, unsafe_allow_html=True)

    # Status do banco
    try:
        with get_session() as db:
            total_lancamentos = db.query(func.count(LancamentoFinanceiro.id)).scalar()
            st.caption(f"📊 {total_lancamentos} lançamentos no banco")
    except:
        st.caption("📊 Banco de dados conectado")

# --- PÁGINA: DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard da Comunidade")

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            entrada_total, saldo = calcular_dashboard_financeiro()
            render_metric_card(
                "Saldo Total",
                f"R$ {saldo:,.2f}",
                subtitle=f"Total de Entradas: R$ {entrada_total:,.2f}",
                color="#10B981" if saldo >= 0 else "#EF4444",
            )
        except Exception:
            st.error("Erro ao carregar dados financeiros")

    with col2:
        try:
            total_fieis, dizimistas = contar_fieis()
            render_metric_card(
                "Fiéis",
                f"{total_fieis}",
                subtitle=f"{dizimistas} dizimistas ativos",
                color="#3B82F6",
            )
        except Exception:
            st.error("Erro ao carregar dados dos fiéis")

    with col3:
        try:
            with get_session() as db:
                projetos_ativos = (
                    db.query(func.count(Projeto.id))
                    .filter(Projeto.status == "Em Andamento")
                    .scalar()
                    or 0
                )

            render_metric_card(
                "Projetos Ativos",
                f"{projetos_ativos}",
                subtitle="Em execução",
                color="#F59E0B",
            )
        except Exception:
            st.error("Erro ao carregar projetos")

    with col4:
        try:
            with get_session() as db:
                total_repasses = (
                    db.query(func.sum(LancamentoFinanceiro.valor))
                    .filter(
                        LancamentoFinanceiro.categoria == "Repasse Paroquial",
                        LancamentoFinanceiro.tipo == "Saída",
                    )
                    .scalar()
                    or 0
                )

            render_metric_card(
                "Repassado à Paróquia",
                f"R$ {total_repasses:,.2f}",
                subtitle="Total histórico",
                color="#8B5CF6",
            )
        except Exception:
            st.error("Erro ao carregar repasses")

    st.markdown("---")

    # Gráficos
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📈 Movimentação Financeira (Últimos 6 Meses)")
        try:
            with get_session() as db:
                # Obter dados dos últimos 6 meses (lógica corrigida)
                mes_atual = hoje.month
                ano_atual = hoje.year

                # Período de 6 meses (mês atual + 5 anteriores)
                mes_inicio = mes_atual - 5
                ano_inicio = ano_atual
                if mes_inicio <= 0:
                    mes_inicio += 12
                    ano_inicio -= 1

                # Define o primeiro dia do período de 6 meses
                seis_meses_atras = date(ano_inicio, mes_inicio, 1)

                lancamentos = db.query(
                    extract('month', LancamentoFinanceiro.data).label('mes'),
                    extract('year', LancamentoFinanceiro.data).label('ano'),
                    LancamentoFinanceiro.tipo,
                    func.sum(LancamentoFinanceiro.valor).label('total')
                ).filter(
                    LancamentoFinanceiro.data >= seis_meses_atras
                ).group_by(
                    'mes', 'ano', LancamentoFinanceiro.tipo
                ).order_by('ano', 'mes').all()

                if lancamentos:
                    # Preparar dados para o gráfico
                    meses = []
                    entradas = []
                    saidas = []

                    for lancamento in lancamentos:
                        mes_ano = f"{int(lancamento.mes)}/{int(lancamento.ano)}"
                        if mes_ano not in meses:
                            meses.append(mes_ano)

                        if lancamento.tipo == 'Entrada':
                            entradas.append(lancamento.total)
                            saidas.append(0)
                        else:
                            saidas.append(lancamento.total)
                            entradas.append(0)

                    if meses:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=meses,
                            y=entradas,
                            name='Entradas',
                            marker_color='#10B981'
                        ))
                        fig.add_trace(go.Bar(
                            x=meses,
                            y=saidas,
                            name='Saídas',
                            marker_color='#EF4444'
                        ))

                        fig.update_layout(
                            barmode='group',
                            height=400,
                            showlegend=True,
                            plot_bgcolor='white'
                        )

                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Aguardando dados financeiros para exibir gráfico")

    with col_b:
        st.subheader("🎯 Status dos Projetos")
        try:
            with get_session() as db:
                projetos_status = db.query(
                    Projeto.status,
                    func.count(Projeto.id).label('quantidade')
                ).group_by(Projeto.status).all()

                if projetos_status:
                    df_status = pd.DataFrame(projetos_status, columns=['Status', 'Quantidade'])
                    fig = px.pie(
                        df_status,
                        values='Quantidade',
                        names='Status',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Nenhum projeto cadastrado")

# --- PÁGINA: FINANÇAS ---
elif menu == "💰 Finanças":
    st.title("💰 Gestão Financeira")

    tab1, tab2, tab3, tab4 = st.tabs([
        "💸 Novo Lançamento", "📜 Histórico", "📊 Análise", "🏦 Repasses à Paróquia"
    ])

    with tab1:
        with st.form("novo_lancamento", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_lancamento = col1.date_input("Data", hoje, disabled=not can_write())
            tipo = col2.selectbox("Tipo", ["Entrada", "Saída"], disabled=not can_write())

            if tipo == "Entrada":
                categorias = [
                    "Dízimo", "Oferta", "Doação", "Eventos",
                    "Venda de Produtos", "Outras Receitas"
                ]
            else:
                categorias = [
                    "Manutenção", "Materiais Litúrgicos",
                    "Eventos", "Caridade", "Administrativo",
                    "Formações", "Outras Despesas"
                ]

            categoria = st.selectbox("Categoria", categorias, disabled=not can_write())
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f", disabled=not can_write())
            descricao = st.text_area("Descrição", disabled=not can_write())

            col_a, col_b = st.columns(2)
            comprovante = col_a.text_input("Nº Comprovante (opcional)", disabled=not can_write())
            aprovado = col_b.checkbox("Aprovado pelo coordenador", disabled=not can_write())

            if st.form_submit_button("💾 Salvar Lançamento", disabled=not can_write()):
                if not can_write():
                    st.warning("Seu perfil não permite adicionar informações.")
                else:
                    lancamento_data = {
                        "data": data_lancamento,
                        "categoria": categoria,
                        "tipo": tipo,
                        "valor": valor,
                        "descricao": descricao,
                        "comprovante": comprovante,
                        "aprovado": aprovado
                    }

                    try:
                        salvar_lancamento(lancamento_data)
                        st.success("✅ Lançamento salvo com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")
    with tab2:
        st.subheader("Histórico de Lançamentos")

        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda x: calendar.month_name[x])
        with col_f2:
            filtro_ano = st.selectbox("Ano", list(range(2020, hoje.year + 1)), index=len(range(2020, hoje.year + 1))-1)
        with col_f3:
            filtro_tipo = st.selectbox("Tipo", ["Todos", "Entrada", "Saída"])

        try:
            # Obter lançamentos filtrados
            lancamentos = obter_lancamentos(filtro_mes, filtro_ano)

            if filtro_tipo != "Todos":
                lancamentos = [l for l in lancamentos if l.tipo == filtro_tipo]

            if lancamentos:
                # Converter para DataFrame
                df_lancamentos = pd.DataFrame([{
                    'Data': l.data.strftime('%d/%m/%Y'),
                    'Categoria': l.categoria,
                    'Tipo': l.tipo,
                    'Valor': f"R$ {l.valor:,.2f}",
                    'Descrição': l.descricao,
                    'Aprovado': '✅' if l.aprovado else '❌'
                } for l in lancamentos])

                st.dataframe(df_lancamentos, use_container_width=True, hide_index=True)

                # Estatísticas
                entradas = sum(l.valor for l in lancamentos if l.tipo == 'Entrada')
                saidas = sum(l.valor for l in lancamentos if l.tipo == 'Saída')

                col_e1, col_e2, col_e3 = st.columns(3)
                col_e1.metric("Total Entradas", f"R$ {entradas:,.2f}")
                col_e2.metric("Total Saídas", f"R$ {saidas:,.2f}")
                col_e3.metric("Saldo do Período", f"R$ {entradas - saidas:,.2f}")
            else:
                st.info("Nenhum lançamento encontrado para o período selecionado")
        except Exception as e:
            st.error(f"Erro ao carregar lançamentos: {str(e)}")

    with tab4:
        st.subheader("Lançar Repasse para a Paróquia")

        st.info("Esta seção lança o valor do repasse à paróquia como uma despesa no sistema financeiro.")

        with st.form("lancar_repasse", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_repasse = col1.date_input("Data do Repasse", hoje, disabled=not can_write())
            valor = col2.number_input("Valor Repassado (R$)", min_value=0.01, format="%.2f", disabled=not can_write())

            descricao = st.text_area("Descrição (opcional)", "Repasse para a paróquia", disabled=not can_write())
            comprovante = st.text_input("Nº Comprovante (opcional)", disabled=not can_write())

            if st.form_submit_button("💾 Lançar Repasse como Despesa", disabled=not can_write()):
                if not can_write():
                    st.warning("Seu perfil não permite adicionar informações.")
                else:
                    lancamento_data = {
                        "data": data_repasse,
                        "categoria": "Repasse Paroquial",
                        "tipo": "Saída",
                        "valor": valor,
                        "descricao": descricao,
                        "comprovante": comprovante,
                        "aprovado": True  # Repasses são tipicamente aprovados
                    }

                    try:
                        salvar_lancamento(lancamento_data)
                        st.success("✅ Repasse lançado como despesa com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")
# --- PÁGINA: FIÉIS ---
elif menu == "👥 Fiéis":
    st.title("👥 Gestão de Fiéis")

    tab1, tab2 = st.tabs(["📝 Cadastrar Fiel", "📊 Estatísticas"])

    with tab1:
        with st.form("cadastro_fiel", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo *", disabled=not can_write())
            telefone = col2.text_input("Telefone", disabled=not can_write())

            email = st.text_input("E-mail", disabled=not can_write())
            endereco = st.text_input("Endereço", disabled=not can_write())
            familia = st.text_input("Família (Sobrenome)", disabled=not can_write())

            st.subheader("Sacramentos Recebidos")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            batismo = col_s1.checkbox("Batismo", disabled=not can_write())
            eucaristia = col_s2.checkbox("Eucaristia", disabled=not can_write())
            crisma = col_s3.checkbox("Crisma", disabled=not can_write())
            matrimonio = col_s4.checkbox("Matrimônio", disabled=not can_write())

            st.subheader("Envolvimento")
            col_e1, col_e2 = st.columns(2)
            dizimista = col_e1.checkbox("É Dizimista", disabled=not can_write())
            ministerios = col_e2.multiselect("Ministérios",
                ["Coral", "Liturgia", "Catequese", "Jovens", "Acolhida", "Outros"], disabled=not can_write())

            observacoes = st.text_area("Observações", disabled=not can_write())

            if st.form_submit_button("💾 Cadastrar Fiel", disabled=not can_write()):
                if not can_write():
                    st.warning("Seu perfil não permite adicionar informações.")
                else:
                    fiel_data = {
                        "nome": nome,
                        "telefone": telefone,
                        "email": email,
                        "endereco": endereco,
                        "familia": familia,
                        "batismo": batismo,
                        "eucaristia": eucaristia,
                        "crisma": crisma,
                        "matrimonio": matrimonio,
                        "dizimista": dizimista,
                        "ministrios": ", ".join(ministerios) if ministerios else "",
                        "observacoes": observacoes,
                        "ativo": True
                    }

                    try:
                        salvar_fiel(fiel_data)
                        st.success(f"✅ {nome} cadastrado(a) com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar: {str(e)}")
    with tab2:
        try:
            total_fieis, dizimistas = contar_fieis()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Fiéis", total_fieis)
            col2.metric("Dizimistas Ativos", dizimistas)
            col3.metric("Percentual Dizimistas",
                       f"{(dizimistas/total_fieis*100):.1f}%" if total_fieis > 0 else "0%")

            # Sacramentos - consulta agregada única
            with get_session() as db:
                resultado = db.query(
                    func.sum(
                        case((Fiel.batismo.is_(True), 1), else_=0)
                    ).label("batizados"),
                    func.sum(
                        case((Fiel.eucaristia.is_(True), 1), else_=0)
                    ).label("eucaristia_count"),
                    func.sum(
                        case((Fiel.crisma.is_(True), 1), else_=0)
                    ).label("crismados"),
                    func.sum(
                        case((Fiel.matrimonio.is_(True), 1), else_=0)
                    ).label("casados"),
                ).one()

                batizados = resultado.batizados or 0
                eucaristia_count = resultado.eucaristia_count or 0
                crismados = resultado.crismados or 0
                casados = resultado.casados or 0

                fig = go.Figure(
                    data=[
                        go.Bar(
                            name="Sacramentos",
                            x=["Batismo", "Eucaristia", "Crisma", "Matrimônio"],
                            y=[batizados, eucaristia_count, crismados, casados],
                        )
                    ]
                )
                fig.update_layout(title="Sacramentos Recebidos", height=400)
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao carregar estatísticas: {str(e)}")

# --- PÁGINA: PROJETOS ---
# --- PÁGINA: PROJETOS ---
elif menu == "🏗️ Projetos":
    st.title("🏗️ Projetos da Comunidade")

    st.markdown(f"""
    <div class="warning-card">
        <strong>⚠️ Atenção:</strong> Projetos acima de R$ {PARISH_INFO['limite_aprovacao_comunidade']:,.2f}
        precisam de aprovação prévia da paróquia.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Novo Projeto", "📊 Acompanhamento"])

    # ----------------------------------------
    # TAB 1 - NOVO PROJETO
    # ----------------------------------------
    with tab1:
        with st.form("novo_projeto", clear_on_submit=True):
            nome = st.text_input("Nome do Projeto *", disabled=not can_write())

            col1, col2 = st.columns(2)
            tipo = col1.selectbox("Tipo", [
                "Reforma/Estrutural", "Equipamentos", "Evento",
                "Ação Social", "Litúrgico", "Outro"
            ], disabled=not can_write())
            custo_estimado = col2.number_input("Custo Estimado (R$)", min_value=0.01, disabled=not can_write())

            descricao = st.text_area("Descrição", disabled=not can_write())
            prazo = st.date_input("Prazo Desejado", min_value=hoje, disabled=not can_write())
            prioridade = st.select_slider(
                "Prioridade",
                options=["Baixa", "Média", "Alta", "Urgente"],
                disabled=not can_write()
            )

            # Verificar se precisa aprovação da paróquia
            precisa_aprovacao = custo_estimado > PARISH_INFO['limite_aprovacao_comunidade']

            if precisa_aprovacao:
                st.warning("⚠️ Este projeto precisa de aprovação da paróquia!")
                justificativa = st.text_area("Justificativa para a Paróquia", disabled=not can_write())
                aprovado_paroquia = False
            else:
                justificativa = ""
                aprovado_paroquia = st.checkbox("Aprovado pelo coordenador", disabled=not can_write())

            if st.form_submit_button("💾 Salvar Projeto", disabled=not can_write()):
                if not can_write():
                    st.warning("Seu perfil não permite adicionar informações.")
                else:
                    projeto_data = {
                        "nome": nome,
                        "tipo": tipo,
                        "descricao": descricao,
                        "custo_estimado": custo_estimado,
                        "prazo": prazo,
                        "prioridade": prioridade,
                        "status": "Planejamento",
                        "aprovado_paroquia": aprovado_paroquia,
                        "justificativa": justificativa
                    }

                    try:
                        salvar_projeto(projeto_data)
                        st.success("✅ Projeto salvo com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")

    # ----------------------------------------
    # TAB 2 - ACOMPANHAMENTO
    # ----------------------------------------
    with tab2:
        try:
            projetos = obter_projetos_por_status()

            if projetos:
                for projeto in projetos:
                    with st.expander(f"{projeto.nome} - R$ {projeto.custo_estimado:,.2f} ({projeto.status})"):

                        col1, col2 = st.columns(2)

                        col1.write(f"**Tipo:** {projeto.tipo}")
                        col1.write(f"**Prioridade:** {projeto.prioridade}")
                        col1.write(
                            f"**Prazo:** {projeto.prazo.strftime('%d/%m/%Y') if projeto.prazo else 'Não definido'}"
                        )

                        col2.write(f"**Aprovado Paróquia:** {'✅ Sim' if projeto.aprovado_paroquia else '❌ Não'}")

                        if projeto.descricao:
                            st.write(f"**Descrição:** {projeto.descricao}")

                        # Controles de status
                        col_b1, col_b2, col_b3 = st.columns(3)

                        # INICIAR
                        if projeto.status == 'Planejamento' and projeto.aprovado_paroquia:
                            if col_b1.button("▶️ Iniciar", key=f"iniciar_{projeto.id}", disabled=not can_write()):
                                if not can_write():
                                    st.warning("Seu perfil não permite iniciar projetos.")
                                else:
                                    with get_session() as db:
                                        projeto_db = db.query(Projeto).filter(Projeto.id == projeto.id).first()
                                        if projeto_db:
                                            projeto_db.status = 'Em Andamento'
                                            projeto_db.data_inicio = hoje
                                            db.commit()
                                            st.rerun()

                        # CONCLUIR
                        elif projeto.status == 'Em Andamento':
                            if col_b2.button("✅ Concluir", key=f"concluir_{projeto.id}", disabled=not can_write()):
                                if not can_write():
                                    st.warning("Seu perfil não permite concluir projetos.")
                                else:
                                    with get_session() as db:
                                        projeto_db = db.query(Projeto).filter(Projeto.id == projeto.id).first()
                                        if projeto_db:
                                            projeto_db.status = 'Concluído'
                                            projeto_db.data_conclusao = hoje
                                            db.commit()
                                            st.rerun()

                        # CANCELAR
                        if col_b3.button("🗑️ Cancelar", key=f"cancelar_{projeto.id}", disabled=not can_write()):
                            if not can_write():
                                st.warning("Seu perfil não permite cancelar projetos.")
                            else:
                                with get_session() as db:
                                    projeto_db = db.query(Projeto).filter(Projeto.id == projeto.id).first()
                                    if projeto_db:
                                        projeto_db.status = 'Cancelado'
                                        db.commit()
                                        st.rerun()

            else:
                st.info("Nenhum projeto cadastrado")

        except Exception as e:
            st.error(f"Erro ao carregar projetos: {str(e)}")

# --- PÁGINA: ATAS DE REUNIÃO ---
elif menu == "📝 Atas de Reunião":
    st.title("📝 Atas de Reunião")

    tab1, tab2 = st.tabs(["➕ Nova Ata", "📂 Histórico"])

    with tab1:
        with st.form("nova_ata", clear_on_submit=True):
            st.subheader("Registrar Nova Ata de Reunião")

            col1, col2 = st.columns(2)
            data_reuniao = col1.date_input("Data da Reunião", hoje, disabled=not can_write())
            tipo_reuniao = col2.text_input("Tipo da Reunião", "Ex: Reunião do Conselho", disabled=not can_write())

            participantes = st.text_area("Participantes (um por linha)", disabled=not can_write())
            decisoes = st.text_area("Principais Decisões Tomadas", disabled=not can_write())
            acoes = st.text_area("Ações a Serem Tomadas (com prazos, se houver)", disabled=not can_write())
            responsaveis = st.text_area("Responsáveis pelas Ações", disabled=not can_write())

            if st.form_submit_button("💾 Salvar Ata", disabled=not can_write()):
                if not can_write():
                    st.warning("Seu perfil não permite adicionar informações.")
                else:
                    ata_data = {
                        "data_reuniao": data_reuniao,
                        "tipo": tipo_reuniao,
                        "participantes": participantes,
                        "decisoes": decisoes,
                        "acoes": acoes,
                        "responsaveis": responsaveis
                    }
                    try:
                        salvar_ata(ata_data)
                        st.success("✅ Ata de reunião salva com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar a ata: {e}")
    with tab2:
        st.subheader("Histórico de Atas")
        try:
            atas = obter_atas()
            if atas:
                for ata in atas:
                    with st.expander(f"**{ata.data_reuniao.strftime('%d/%m/%Y')}** - {ata.tipo}"):
                        st.markdown(f"#### Participantes")
                        st.text(ata.participantes)

                        st.markdown(f"#### Decisões Tomadas")
                        st.text(ata.decisoes)

                        st.markdown(f"#### Ações e Responsáveis")
                        st.text(f"Ações: {ata.acoes}")
                        st.text(f"Responsáveis: {ata.responsaveis}")

                        st.caption(f"Registrado em: {ata.created_at.strftime('%d/%m/%Y %H:%M') if ata.created_at else 'N/A'}")

            else:
                st.info("Nenhuma ata de reunião registrada.")
        except Exception as e:
            st.error(f"Erro ao carregar o histórico de atas: {e}")

# --- PÁGINA: RELATÓRIOS ---
elif menu == "📊 Relatórios":
    st.title("📊 Relatórios para Paróquia")

    st.markdown(f"""
    <div class="warning-card">
        <strong>📅 Próximo envio:</strong> {proxima_data.strftime('%d/%m/%Y')}
        (em {dias_restantes} dias)<br>
        <strong>📧 Enviar para:</strong> {PARISH_INFO['email']}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        # Padrão para o mês anterior
        default_month_index = hoje.month - 2 if hoje.month > 1 else 11
        mes_relatorio = st.selectbox("Selecione o mês do relatório",
            list(range(1, 13)), format_func=lambda x: calendar.month_name[x], index=default_month_index)
    with col2:
        default_year_index = len(range(2020, hoje.year + 1)) - (1 if hoje.month > 1 else 2)
        ano_relatorio = st.selectbox("Ano",
            list(range(2020, hoje.year + 1)), index=default_year_index)

    if st.button("📄 Gerar Prévia do Relatório", type="primary"):
        try:
            # Coletar dados para o relatório
            entradas_mes, saidas_mes = calcular_totais_periodo(mes_relatorio, ano_relatorio)
            with get_session() as db:
                novos_fieis_mes = db.query(func.count(Fiel.id)).filter(
                    extract('month', Fiel.data_cadastro) == mes_relatorio,
                    extract('year', Fiel.data_cadastro) == ano_relatorio
                ).scalar() or 0

                projetos_novos = db.query(func.count(Projeto.id)).filter(
                    extract('month', Projeto.created_at) == mes_relatorio,
                    extract('year', Projeto.created_at) == ano_relatorio
                ).scalar() or 0

                reunioes_realizadas = db.query(func.count(AtaReuniao.id)).filter(
                    extract('month', AtaReuniao.data_reuniao) == mes_relatorio,
                    extract('year', AtaReuniao.data_reuniao) == ano_relatorio
                ).scalar() or 0

            # Organizar dados em um dicionário
            dados_relatorio = {
                "nome_comunidade": "Nossa Senhora das Graças",
                "entradas_mes": entradas_mes,
                "saidas_mes": saidas_mes,
                "saldo_mes": entradas_mes - saidas_mes,
                "novos_fieis": novos_fieis_mes,
                "novos_projetos": projetos_novos,
                "reunioes_realizadas": reunioes_realizadas,
            }

            st.session_state['dados_relatorio'] = dados_relatorio
            st.session_state['periodo_relatorio'] = f"{calendar.month_name[mes_relatorio]}_{ano_relatorio}"

        except Exception as e:
            st.session_state.pop('dados_relatorio', None) # Limpa em caso de erro
            st.error(f"Erro ao gerar relatório: {str(e)}")

    # Exibe a prévia e o botão de download se os dados foram gerados
    if 'dados_relatorio' in st.session_state:
        dados = st.session_state['dados_relatorio']

        st.markdown("---")
        st.success("✅ Prévia do relatório gerada. Verifique os dados abaixo e baixe o PDF.")

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📈 Resumo Financeiro")
            st.write(f"**Total de Entradas:** R$ {dados['entradas_mes']:,.2f}")
            st.write(f"**Total de Saídas:** R$ {dados['saidas_mes']:,.2f}")
            st.write(f"**Saldo do Mês:** R$ {dados['saldo_mes']:,.2f}")

        with col_b:
            st.subheader("📋 Atividades da Comunidade")
            st.write(f"**Novos fiéis cadastrados:** {dados['novos_fieis']}")
            st.write(f"**Projetos iniciados:** {dados['novos_projetos']}")
            st.write(f"**Reuniões realizadas:** {dados['reunioes_realizadas']}")

        # Gera o PDF em bytes e oferece para download
        pdf_bytes = gerar_relatorio_pdf(st.session_state['periodo_relatorio'].replace("_", "/"), dados)
        st.download_button(
            label="📥 Baixar Relatório em PDF",
            data=pdf_bytes,
            file_name=f"relatorio_{st.session_state['periodo_relatorio']}.pdf",
            mime="application/pdf"
        )

# --- PÁGINA: CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    if not can_write(): # Added permission check
        st.error("Acesso negado. Apenas administradores podem acessar Configurações.")
        st.stop() # Stop rendering the page for unauthorized users
    st.title("⚙️ Configurações do Sistema")

    tab1, tab2, tab3 = st.tabs(["🏛️ Paróquia", "🔐 Segurança", "🗄️ Banco de Dados"])

    with tab1:
        st.subheader("Configurações da Paróquia")

        with st.form("config_paroquia"):
            col1, col2 = st.columns(2)
            # Carrega os valores atuais para o formulário
            nome = col1.text_input("Nome da Paróquia", value=PARISH_INFO['nome'], disabled=not can_write())
            responsavel = col2.text_input("Responsável", value=PARISH_INFO['responsavel'], disabled=not can_write())

            telefone = st.text_input("Telefone", value=PARISH_INFO['telefone'], disabled=not can_write())
            email = st.text_input("E-mail", value=PARISH_INFO['email'], disabled=not can_write())

            coordenador = st.text_input("Coordenador da Comunidade", value=PARISH_INFO['coordenador_local'], disabled=not can_write())

            dia_repasse = st.number_input("Dia para prestação de contas",
                min_value=1, max_value=28, value=int(PARISH_INFO['data_prestacao_contas']), disabled=not can_write())

            limite = st.number_input("Limite para aprovação da comunidade (R$)",
                min_value=0.0, value=PARISH_INFO['limite_aprovacao_comunidade'], format="%.2f", disabled=not can_write())

            if st.form_submit_button("💾 Salvar Configurações", disabled=not can_write()):
                if not can_write():
                    st.warning("Seu perfil não permite alterar configurações.")
                else:
                    try:
                        with get_session() as db:
                            set_config_value(db, "nome_paroquia", nome)
                            set_config_value(db, "responsavel_paroquia", responsavel)
                            set_config_value(db, "telefone_paroquia", telefone)
                            set_config_value(db, "email_paroquia", email)
                            set_config_value(db, "coordenador_local", coordenador)
                            set_config_value(db, "data_prestacao_contas", str(dia_repasse).zfill(2))
                            set_config_value(db, "limite_aprovacao_comunidade", limite)

                        st.success("✅ Configurações salvas com sucesso!")
                        st.info("As alterações serão aplicadas imediatamente.")
                        # Forçar o rerun para recarregar o PARISH_INFO
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erro ao salvar configurações: {e}")
    with tab3:
        st.subheader("Status do Banco de Dados")

        try:
            with get_session() as db:
                # Estatísticas
                total_lancamentos = db.query(func.count(LancamentoFinanceiro.id)).scalar()
                total_fieis = db.query(func.count(Fiel.id)).scalar()
                total_projetos = db.query(func.count(Projeto.id)).scalar()

                col1, col2, col3 = st.columns(3)
                col1.metric("Lançamentos", total_lancamentos)
                col2.metric("Fiéis", total_fieis)
                col3.metric("Projetos", total_projetos)

                # Backup
                st.subheader("🗃️ Backup de Dados")

                if st.button("📥 Exportar Backup CSV"):
                    # Exportar dados para CSV (apenas lançamentos, como antes)
                    lancamentos = db.query(LancamentoFinanceiro).all()

                    df_lancamentos = pd.DataFrame(
                        [
                            {
                                "id": l.id,
                                "data": l.data,
                                "categoria": l.categoria,
                                "tipo": l.tipo,
                                "valor": l.valor,
                                "descricao": l.descricao,
                            }
                            for l in lancamentos
                        ]
                    )

                    st.download_button(
                        label="📥 Baixar Lançamentos (CSV)",
                        data=df_lancamentos.to_csv(index=False),
                        file_name=f"backup_lancamentos_{hoje.strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )

                # Exportação completa para Excel (finanças, fiéis, projetos)
                if st.button("📊 Exportar Dados para Excel"):
                    lancamentos = db.query(LancamentoFinanceiro).all()
                    fieis = db.query(Fiel).all()
                    projetos = db.query(Projeto).all()

                    df_lancamentos = pd.DataFrame(
                        [
                            {
                                "id": l.id,
                                "data": l.data,
                                "categoria": l.categoria,
                                "tipo": l.tipo,
                                "valor": l.valor,
                                "descricao": l.descricao,
                                "aprovado": l.aprovado,
                            }
                            for l in lancamentos
                        ]
                    )

                    df_fieis = pd.DataFrame(
                        [
                            {
                                "id": f.id,
                                "nome": f.nome,
                                "telefone": f.telefone,
                                "email": f.email,
                                "endereco": f.endereco,
                                "familia": f.familia,
                                "dizimista": f.dizimista,
                                "data_cadastro": f.data_cadastro,
                                "ativo": f.ativo,
                            }
                            for f in fieis
                        ]
                    )

                    df_projetos = pd.DataFrame(
                        [
                            {
                                "id": p.id,
                                "nome": p.nome,
                                "tipo": p.tipo,
                                "status": p.status,
                                "prioridade": p.prioridade,
                                "custo_estimado": p.custo_estimado,
                                "custo_real": p.custo_real,
                                "prazo": p.prazo,
                                "data_inicio": p.data_inicio,
                                "data_conclusao": p.data_conclusao,
                            }
                            for p in projetos
                        ]
                    )

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df_lancamentos.to_excel(
                            writer, index=False, sheet_name="Lancamentos"
                        )
                        df_fieis.to_excel(writer, index=False, sheet_name="Fieis")
                        df_projetos.to_excel(writer, index=False, sheet_name="Projetos")

                    output.seek(0)

                    st.download_button(
                        label="📥 Baixar Backup Completo (Excel)",
                        data=output.getvalue(),
                        file_name=f"backup_completo_{hoje.strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

                st.info("✅ Banco de dados conectado com sucesso!")

        except Exception as e:
            st.error(f"❌ Erro na conexão com o banco: {str(e)}")

# --- RODAPÉ ---
st.markdown("---")
st.caption(f"⛪ Sistema de Gestão Comunitária Católica | v1.0 | Última atualização: {hoje.strftime('%d/%m/%Y')}")
