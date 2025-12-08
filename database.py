<<<<<<< HEAD
import os
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# A URL de conexão é lida dos segredos do Streamlit para segurança no deploy.
# Para desenvolvimento local, o Streamlit também lerá o .streamlit/secrets.toml
DATABASE_URL = st.secrets["DATABASE_URL"]

# Configurar e criar engine do SQLAlchemy
# A URL já inclui sslmode, então não são necessários connect_args extras para isso.
# Adicionamos outras configurações recomendadas para pooling.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar tabelas no banco de dados"""
    # Importar modelos aqui para evitar importações circulares
    from models import Base
    
    try:
        # Tenta criar as tabelas no banco de dados configurado
        Base.metadata.create_all(bind=engine)
        
        # Verifica a conexão e imprime a versão do banco para confirmação
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
            print(f"✅ Banco de dados conectado com sucesso: {db_version}")
            
        print("✅ Tabelas verificadas/criadas com sucesso!")
        
    except Exception as e:
        # Se houver qualquer erro durante a inicialização, ele será exibido.
        # Isso evita que a aplicação continue em um estado inconsistente.
        print(f"❌ Erro fatal ao inicializar o banco de dados: {e}")
        # É importante relançar a exceção ou tratar o erro de forma apropriada
        # para que o Streamlit pare a execução e exiba o erro.
=======
import os
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# A URL de conexão é lida dos segredos do Streamlit para segurança no deploy.
# Para desenvolvimento local, o Streamlit também lerá o .streamlit/secrets.toml
DATABASE_URL = st.secrets["DATABASE_URL"]

# Configurar e criar engine do SQLAlchemy
# A URL já inclui sslmode, então não são necessários connect_args extras para isso.
# Adicionamos outras configurações recomendadas para pooling.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar tabelas no banco de dados"""
    # Importar modelos aqui para evitar importações circulares
    from models import Base
    
    try:
        # Tenta criar as tabelas no banco de dados configurado
        Base.metadata.create_all(bind=engine)
        
        # Verifica a conexão e imprime a versão do banco para confirmação
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
            print(f"✅ Banco de dados conectado com sucesso: {db_version}")
            
        print("✅ Tabelas verificadas/criadas com sucesso!")
        
    except Exception as e:
        # Se houver qualquer erro durante a inicialização, ele será exibido.
        # Isso evita que a aplicação continue em um estado inconsistente.
        print(f"❌ Erro fatal ao inicializar o banco de dados: {e}")
        # É importante relançar a exceção ou tratar o erro de forma apropriada
        # para que o Streamlit pare a execução e exiba o erro.
>>>>>>> f89581adbff20f6d55465e46566f7270d9d3de28
        raise