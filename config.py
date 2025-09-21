import os
from supabase import create_client, Client

# Configurações do Supabase
# Carrega credenciais do Supabase com fallback seguro (secrets.toml -> env vars)
try:
    import streamlit as st  # Import tardio para ambientes sem Streamlit
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    except Exception:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações da aplicação
APP_TITLE = "Sistema de Controle de Contas - Obras"
APP_ICON = "🏗️"

# Status das parcelas
PARCELA_STATUS = {
    "PENDENTE": "Pendente",
    "PAGA": "Paga",
    "VENCIDA": "Vencida"
}

# Status do material
MATERIAL_STATUS = {
    "ESTOQUE": "Estoque",
    "EM_USO": "Em Uso"
}