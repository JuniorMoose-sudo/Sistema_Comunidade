"""
Script para resetar o banco de dados
Deleta todas as tabelas e as recria vazias
"""

import streamlit as st
from sqlalchemy import text
from database import engine, Base
from models import LancamentoFinanceiro, Fiel, Projeto, AtaReuniao, Configuracao

def reset_database():
    """Deleta todas as tabelas e as recria"""

    print("🔄 Iniciando reset do banco de dados...")

    try:
        # Dropar todas as tabelas
        print("🗑️  Deletando tabelas existentes...")
        Base.metadata.drop_all(bind=engine)

        # Recriar tabelas
        print("📝 Recriando tabelas vazias...")
        Base.metadata.create_all(bind=engine)

        # Verificar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
            print(f"✅ Banco de dados resetado com sucesso!")
            print(f"📊 Versão do banco: {db_version}")

        return True

    except Exception as e:
        print(f"❌ Erro ao resetar banco de dados: {e}")
        return False

if __name__ == "__main__":
    reset_database()
