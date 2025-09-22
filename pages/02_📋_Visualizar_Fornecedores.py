import streamlit as st
import pandas as pd
from database import DatabaseManager
from utils import formatar_moeda

st.set_page_config(
    page_title="Visualizar Fornecedores",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Visualizar Fornecedores")

# Inicializar banco de dados
db = DatabaseManager()

# Filtros
st.subheader("🔍 Filtros")
col1, col2, col3 = st.columns(3)

with col1:
    filtro_nome = st.text_input("Nome do Fornecedor", placeholder="Digite o nome...")

with col2:
    filtro_cnpj = st.text_input("CNPJ", placeholder="Digite o CNPJ...")

with col3:
    filtro_vendedor = st.text_input("Vendedor", placeholder="Digite o vendedor...")

# Aplicar filtros
filtros = {}
if filtro_nome:
    filtros['nome'] = filtro_nome
if filtro_cnpj:
    filtros['cnpj'] = filtro_cnpj
if filtro_vendedor:
    filtros['vendedor'] = filtro_vendedor

# Buscar fornecedores
fornecedores = db.get_fornecedores(filtros)

if fornecedores:
    st.subheader(f"📊 Fornecedores Encontrados ({len(fornecedores)})")
    
    # Criar DataFrame
    df = pd.DataFrame(fornecedores)
    
    # Formatar colunas
    df['ID'] = df['id']
    df['Nome'] = df['nome']
    df['CNPJ'] = df['cnpj']
    df['Telefone'] = df['telefone']
    df['Vendedor'] = df['vendedor'].fillna('Não informado')
    df['Criado em'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
    
    # Mostrar tabela
    st.dataframe(
        df[['ID', 'Nome', 'CNPJ', 'Telefone', 'Vendedor', 'Criado em']],
        column_config={
            'ID': 'ID',
            'Nome': 'Nome',
            'CNPJ': 'CNPJ',
            'Telefone': 'Telefone',
            'Vendedor': 'Vendedor',
            'Criado em': 'Criado em'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Fornecedores", len(fornecedores))
    
    with col2:
        vendedores_unicos = df['vendedor'].nunique()
        st.metric("Vendedores Únicos", vendedores_unicos)
    
    with col3:
        st.metric("Com Vendedor", len(df[df['vendedor'] != 'Não informado']))
    
    with col4:
        st.metric("Sem Vendedor", len(df[df['vendedor'] == 'Não informado']))
        
else:
    st.warning("Nenhum fornecedor encontrado com os filtros aplicados.")
    
    if not filtros:
        st.info("💡 Cadastre o primeiro fornecedor clicando em 'Lançar Fornecedor' no menu lateral.")

# Botões de ação
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("➕ Novo Fornecedor", type="primary", use_container_width=True):
        st.switch_page("pages/01_📝_Lançar_Fornecedor.py")

with col2:
    if st.button("🏠 Página Inicial", use_container_width=True):
        st.switch_page("pages/00_🏠_Dashboard.py")

with col3:
    if st.button("🔄 Atualizar", use_container_width=True):
        st.rerun()

# Informações sobre o sistema
st.sidebar.markdown("### ℹ️ Informações")
st.sidebar.markdown("""
**Funcionalidades:**
- Visualizar todos os fornecedores
- Filtrar por nome, CNPJ ou vendedor
- Estatísticas dos fornecedores
- Navegação para outras páginas

**Campos:**
- **ID:** Identificador único
- **Nome:** Nome da empresa
- **CNPJ:** Documento único
- **Telefone:** Contato principal
- **Vendedor:** Responsável comercial
- **Criado em:** Data do cadastro
""")