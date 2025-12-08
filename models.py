from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class LancamentoFinanceiro(Base):
    __tablename__ = "lancamentos_financeiros"
    
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    categoria = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'Entrada' ou 'Saída'
    valor = Column(Float, nullable=False)
    descricao = Column(Text)
    comprovante = Column(String(255))
    aprovado = Column(Boolean, default=False)
    comunidade_id = Column(Integer, default=1)  # Para multi-comunidades futuras
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Fiel(Base):
    __tablename__ = "fieis"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    telefone = Column(String(20))
    email = Column(String(100))
    endereco = Column(String(200))
    familia = Column(String(100))
    
    # Sacramentos
    batismo = Column(Boolean, default=False)
    data_batismo = Column(Date)
    eucaristia = Column(Boolean, default=False)
    data_eucaristia = Column(Date)
    crisma = Column(Boolean, default=False)
    data_crisma = Column(Date)
    matrimonio = Column(Boolean, default=False)
    data_matrimonio = Column(Date)
    
    # Envolvimento
    dizimista = Column(Boolean, default=False)
    ministrios = Column(Text)  # JSON ou lista separada por vírgula
    comunidade_id = Column(Integer, default=1)
    data_cadastro = Column(Date, server_default=func.now())
    ativo = Column(Boolean, default=True)
    observacoes = Column(Text)

class Projeto(Base):
    __tablename__ = "projetos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(50))
    descricao = Column(Text)
    custo_estimado = Column(Float, default=0.0)
    custo_real = Column(Float, default=0.0)
    prazo = Column(Date)
    prioridade = Column(String(20))  # 'Baixa', 'Média', 'Alta', 'Urgente'
    status = Column(String(20))  # 'Planejamento', 'Em Andamento', 'Concluído', 'Cancelado'
    aprovado_paroquia = Column(Boolean, default=False)
    data_inicio = Column(Date)
    data_conclusao = Column(Date)
    justificativa = Column(Text)
    comunidade_id = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RepasseParoquia(Base):
    __tablename__ = "repasses_paroquia"
    
    id = Column(Integer, primary_key=True, index=True)
    mes_ano = Column(String(7), nullable=False)  # Formato: 'MM/YYYY'
    valor_repassado = Column(Float, nullable=False)
    data_repasse = Column(Date, nullable=False)
    comprovante = Column(String(255))
    observacoes = Column(Text)
    comunidade_id = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AtaReuniao(Base):
    __tablename__ = "atas_reunioes"
    
    id = Column(Integer, primary_key=True, index=True)
    data_reuniao = Column(Date, nullable=False)
    tipo = Column(String(50))
    participantes = Column(Text)
    decisoes = Column(Text)
    acoes = Column(Text)
    responsaveis = Column(Text)
    arquivo_ata = Column(String(255))
    comunidade_id = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Configuracao(Base):
    __tablename__ = "configuracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    comunidade_id = Column(Integer, default=1)