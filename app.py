import streamlit as st
from auth import AuthManager

# Configuração da página
st.set_page_config(
    page_title="EasyNF - Sistema de Contas",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Verificar autenticação
auth = AuthManager()

# Se não estiver logado, redirecionar para login
if not auth.is_logged_in():
    st.switch_page("pages/00_🔐_Login.py")
else:
    # Se estiver logado, redirecionar para o dashboard (página dentro de pages/)
    st.switch_page("pages/00_🏠_Dashboard.py")
