import os

import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from utils.logger import get_logger


USE_WERKZEUG = True

# Carrega variáveis de ambiente de um arquivo .env, se existir
load_dotenv()

logger = get_logger(__name__)

# Usuários e senhas lidos do ambiente
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS_HASH = os.getenv("ADMIN_PASS_HASH")
ADMIN_PASS = os.getenv("ADMIN_PASS")  # fallback em texto puro (não recomendado)

USER_USER = os.getenv("USER_USER", "usuario")
USER_PASS_HASH = os.getenv("USER_PASS_HASH")
USER_PASS = os.getenv("USER_PASS")  # fallback em texto puro (não recomendado)


def _maybe_hash(pwd: str) -> str:
    """Hash da senha se werkzeug estiver disponível, senão retorna texto puro."""
    if USE_WERKZEUG:
        return generate_password_hash(pwd)
    return pwd


def _check_password(stored_hash: str | None, stored_plain: str | None, provided: str) -> bool:
    """Verifica senha utilizando hash (preferencial) ou texto puro como fallback."""
    if stored_hash:
        if USE_WERKZEUG:
            try:
                return check_password_hash(stored_hash, provided)
            except ValueError:
                # Hash em formato inválido (ex.: gerado por outro algoritmo/sistema)
                logger.error(
                    "Hash de senha inválido configurado. "
                    "Verifique ADMIN_PASS_HASH/USER_PASS_HASH no .env."
                )
        # Se por algum motivo o hash estiver presente mas werkzeug desabilitado, faz comparação direta
        return stored_hash == provided
    if stored_plain is not None:
        return stored_plain == provided
    return False


def authenticate(username: str, password: str):
    """
    Autentica contra valores definidos em variáveis de ambiente.
    Retorna dict {"role": "admin"/"usuario", "name": username} ou None.
    """
    # Admin
    if username == ADMIN_USER and _check_password(ADMIN_PASS_HASH, ADMIN_PASS, password):
        logger.info("Login bem-sucedido para usuário admin '%s'", username)
        return {"role": "admin", "name": username}

    # Usuário comum
    if username == USER_USER and _check_password(USER_PASS_HASH, USER_PASS, password):
        logger.info("Login bem-sucedido para usuário comum '%s'", username)
        return {"role": "usuario", "name": username}

    logger.warning("Tentativa de login falhou para usuário '%s'", username)
    return None


def show_login():
    """
    Exibe a tela de login (form).
    Ao autenticar com sucesso, grava em st.session_state['auth'] e faz st.rerun().
    """
    st.set_page_config(page_title="Login")
    st.title("🔐 Acesso ao Sistema")
    st.info("Entre com suas credenciais")

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            user = authenticate(username.strip(), password)
            if user:
                st.session_state["auth"] = user
                st.success(f"Bem-vindo, {user['name']}!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")


def require_login():
    """
    Interrompe a execução (st.stop) e exibe login se não estiver autenticado.
    Deve ser chamado logo após init_db() e init_auth_defaults().
    """
    if "auth" not in st.session_state or st.session_state.get("auth") is None:
        show_login()
        st.stop()


def can_write() -> bool:
    """Retorna True se o usuário logado for admin (pode mudar dados)."""
    return st.session_state.get("auth", {}).get("role") == "admin"

