import streamlit as st
from streamlit_option_menu import option_menu
from config import APP_TITLE, APP_ICON
from auth import AuthManager

# Configuração da página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticação
auth = AuthManager()
if not auth.is_logged_in():
    st.switch_page("pages/00_🔐_Login.py")
    st.stop()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
        color: white;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
# Informações do usuário logado
usuario_atual = auth.get_current_user()
if usuario_atual:
    st.sidebar.markdown("### 👤 Usuário Logado")
    st.sidebar.write(f"**Nome:** {usuario_atual['nome']}")
    st.sidebar.write(f"**Função:** {usuario_atual['funcao']}")
    st.sidebar.write(f"**Empresa:** {usuario_atual['empresa']}")
    
    if st.sidebar.button("🚪 Logout"):
        auth.logout()
        st.rerun()

st.markdown(f"""
<div class="main-header">
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>Sistema completo para controle de contas e parcelas em obras</p>
</div>
""", unsafe_allow_html=True)

# Menu de navegação
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Principal",
        options=[
            "🏠 Dashboard",
            "🏢 Lançar Fornecedor",
            "📋 Visualizar Fornecedores",
            "📝 Lançar Nota", 
            "📋 Visualizar Notas",
            "📊 Relatórios",
            "⚙️ Configurações"
        ],
        icons=[
            "house",
            "building",
            "list-ul",
            "pencil-square", 
            "list-ul",
            "graph-up",
            "gear"
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#667eea", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "0px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )
    
    # Adicionar página de logs apenas para administradores
    if auth.is_admin():
        st.markdown("---")
        if st.button("📊 Logs do Sistema", width='stretch'):
            st.switch_page("pages/05_📊_Logs.py")

# Página Dashboard
if selected == "🏠 Dashboard":
    st.title("🏠 Dashboard")
    
    # Importar dados
    from database import DatabaseManager
    from utils import formatar_moeda
    
    db = DatabaseManager()
    notas = db.get_notas()
    locais = db.get_locais_aplicacao()
    
    if not notas:
        st.info("""
        ## 👋 Bem-vindo ao Sistema de Controle de Contas!
        
        Para começar, você precisa:
        
        1. **Configurar os locais de aplicação** na página de Configurações
        2. **Lançar sua primeira nota** na página Lançar Nota
        3. **Visualizar e gerenciar** suas notas na página Visualizar Notas
        4. **Gerar relatórios** na página Relatórios
        
        Use o menu lateral para navegar entre as páginas.
        """)
    else:
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        total_valor = sum(nota['valor_total'] for nota in notas)
        
        # Contar parcelas
        todas_parcelas = []
        for nota in notas:
            parcelas = db.get_parcelas_by_nota(nota['id'])
            todas_parcelas.extend(parcelas)
        
        parcelas_pagas = len([p for p in todas_parcelas if p['status'] == 'PAGA'])
        parcelas_pendentes = len([p for p in todas_parcelas if p['status'] == 'PENDENTE'])
        parcelas_vencidas = len([p for p in todas_parcelas if p['status'] == 'VENCIDA'])
        
        col1.metric("Total de Notas", len(notas))
        col2.metric("Valor Total", formatar_moeda(total_valor))
        col3.metric("Parcelas Pagas", parcelas_pagas)
        col4.metric("Parcelas Pendentes", parcelas_pendentes)
        
        # Gráfico de status das parcelas
        if todas_parcelas:
            st.subheader("📊 Status das Parcelas")
            
            import plotly.express as px
            
            status_data = {
                'Status': ['Pagas', 'Pendentes', 'Vencidas'],
                'Quantidade': [parcelas_pagas, parcelas_pendentes, parcelas_vencidas],
                'Cor': ['#28a745', '#ffc107', '#dc3545']
            }
            
            fig = px.pie(
                values=status_data['Quantidade'],
                names=status_data['Status'],
                title="Distribuição das Parcelas por Status",
                color_discrete_sequence=status_data['Cor']
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Resumo")
                st.write(f"**Total de Parcelas:** {len(todas_parcelas)}")
                st.write(f"**Taxa de Pagamento:** {(parcelas_pagas/len(todas_parcelas)*100):.1f}%")
                st.write(f"**Parcelas Vencidas:** {parcelas_vencidas}")
                
                if parcelas_vencidas > 0:
                    st.warning(f"⚠️ Você tem {parcelas_vencidas} parcela(s) vencida(s)!")
    
    # Notas recentes
    st.subheader("📋 Notas Recentes")
    
    if notas:
        # Ordenar por data de emissão (mais recentes primeiro)
        notas_recentes = sorted(notas, key=lambda x: x['data_emissao'], reverse=True)[:5]
        
        for nota in notas_recentes:
            with st.expander(f"📄 {nota['numero_nota']} - {nota['fornecedor']} - {formatar_moeda(nota['valor_total'])}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Fornecedor:** {nota['fornecedor']}")
                    st.write(f"**Valor:** {formatar_moeda(nota['valor_total'])}")
                    st.write(f"**Data de Emissão:** {nota['data_emissao']}")
                
                with col2:
                    local_nome = next((l['nome'] for l in locais if l['id'] == nota['local_aplicacao']), 'N/A')
                    st.write(f"**Local:** {local_nome}")
                    st.write(f"**Parcelas:** {nota['num_parcelas']}")
                    st.write(f"**Status:** {'Parcelada' if nota['eh_parcelada'] else 'À vista'}")
    
    # Ações rápidas
    st.subheader("⚡ Ações Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Lançar Nova Nota", use_container_width=True):
            st.switch_page("pages/01_📝_Lançar_Nota.py")
    
    with col2:
        if st.button("📋 Ver Todas as Notas", use_container_width=True):
            st.switch_page("pages/02_📋_Visualizar_Notas.py")
    
    with col3:
        if st.button("📊 Gerar Relatório", use_container_width=True):
            st.switch_page("pages/03_📊_Relatórios.py")

# Redirecionar para páginas específicas
elif selected == "🏢 Lançar Fornecedor":
    st.switch_page("pages/01_📝_Lançar_Fornecedor.py")

elif selected == "📋 Visualizar Fornecedores":
    st.switch_page("pages/02_📋_Visualizar_Fornecedores.py")

elif selected == "📝 Lançar Nota":
    st.switch_page("pages/01_📝_Lançar_Nota.py")

elif selected == "📋 Visualizar Notas":
    st.switch_page("pages/02_📋_Visualizar_Notas.py")

elif selected == "📊 Relatórios":
    st.switch_page("pages/03_📊_Relatórios.py")

elif selected == "⚙️ Configurações":
    st.switch_page("pages/04_⚙️_Configurações.py")

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Sistema de Controle de Contas para Obras v1.0.0</p>
    <p>Desenvolvido com ❤️ usando Streamlit e Supabase</p>
</div>
""", unsafe_allow_html=True)
import streamlit as st
from auth import AuthManager

st.set_page_config(
    page_title="EasyNF - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

auth = AuthManager()
if not auth.is_logged_in():
    st.switch_page("pages/00_🔐_Login.py")
    st.stop()

import pandas as pd
from database import DatabaseManager
from utils import formatar_moeda

st.title("🏠 Dashboard")

user = auth.get_current_user()
if user:
    st.sidebar.markdown("### 👤 Usuário Logado")
    st.sidebar.write(f"**Nome:** {user.get('nome','')} ")
    st.sidebar.write(f"**Função:** {user.get('funcao','')} ")
    st.sidebar.write(f"**Empresa:** {user.get('empresa','')} ")
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        auth.logout()
        st.switch_page("pages/00_🔐_Login.py")

# Remover entradas default de páginas do Streamlit na sidebar
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()
notas = db.get_notas()
locais = db.get_locais_aplicacao()

st.subheader("📋 Notas Recentes")
if notas:
    notas_recentes = sorted(notas, key=lambda x: x['data_emissao'], reverse=True)[:5]
    for nota in notas_recentes:
        with st.expander(f"📄 {nota['numero_nota']} - {nota['fornecedor']} - {formatar_moeda(nota['valor_total'])}"):
            st.write(f"Fornecedor: {nota['fornecedor']}")
            st.write(f"Valor: {formatar_moeda(nota['valor_total'])}")
            st.write(f"Data de Emissão: {nota['data_emissao']}")
else:
    st.info("Sem notas cadastradas ainda.")


