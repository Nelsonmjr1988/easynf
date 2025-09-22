import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auth import AuthManager
from database import DatabaseManager

st.set_page_config(
    page_title="Logs do Sistema",
    page_icon="📊",
    layout="wide"
)

# Verificar autenticação
auth = AuthManager()
auth.require_auth()

# Verificar se é administrador
if not auth.is_admin():
    st.error("🔒 Acesso negado. Apenas administradores podem visualizar os logs.")
    st.stop()

st.title("📊 Logs do Sistema")
st.markdown("Rastreamento de todas as ações realizadas no sistema")

# Inicializar banco de dados
db = DatabaseManager()

# Filtros
st.subheader("🔍 Filtros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    acao_filtro = st.selectbox(
        "Ação",
        ["Todas"] + ["LOGIN", "LOGOUT", "REGISTER", "CREATE", "UPDATE", "DELETE", "VIEW"]
    )

with col2:
    usuario_filtro = st.selectbox(
        "Usuário",
        ["Todos"] + [f"{u['nome']} ({u['funcao']})" for u in db.get_usuarios()]
    )

with col3:
    tabela_filtro = st.selectbox(
        "Tabela Afetada",
        ["Todas"] + ["usuarios", "notas", "parcelas", "fornecedores", "locais_aplicacao"]
    )

with col4:
    dias_filtro = st.selectbox(
        "Período",
        ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todos"]
    )

# Aplicar filtros
logs = db.get_logs(limit=1000)

# Filtrar por ação
if acao_filtro != "Todas":
    logs = [log for log in logs if log['acao'] == acao_filtro]

# Filtrar por usuário
if usuario_filtro != "Todas":
    usuario_nome = usuario_filtro.split(' (')[0]
    logs = [log for log in logs if (log.get('usuarios') or {}).get('nome') == usuario_nome]

# Filtrar por tabela
if tabela_filtro != "Todas":
    logs = [log for log in logs if log.get('tabela_afetada') == tabela_filtro]

# Filtrar por período
if dias_filtro != "Todos":
    dias = int(dias_filtro.split(' ')[1].replace('dias', ''))
    data_limite = datetime.now() - timedelta(days=dias)
    logs = [log for log in logs if datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')) >= data_limite]

# Estatísticas
st.subheader("📈 Estatísticas")

col1, col2, col3, col4 = st.columns(4)

total_logs = len(logs)
logins_hoje = len([log for log in logs if log['acao'] == 'LOGIN' and 
                  datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).date() == datetime.now().date()])
acoes_hoje = len([log for log in logs if 
                 datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).date() == datetime.now().date()])
usuarios_ativos = len(set(log['usuario_id'] for log in logs if log['usuario_id']))

col1.metric("Total de Logs", total_logs)
col2.metric("Logins Hoje", logins_hoje)
col3.metric("Ações Hoje", acoes_hoje)
col4.metric("Usuários Ativos", usuarios_ativos)

# Tabela de logs
st.subheader("📋 Logs Detalhados")

if logs:
    # Preparar dados para exibição
    logs_data = []
    for log in logs:
        usuario_info = log.get('usuarios', {})
        logs_data.append({
            'Data/Hora': datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S'),
            'Usuário': usuario_info.get('nome', 'Sistema'),
            'Função': usuario_info.get('funcao', 'N/A'),
            'Empresa': usuario_info.get('empresa', 'N/A'),
            'Ação': log['acao'],
            'Tabela': log.get('tabela_afetada', 'N/A'),
            'Registro ID': log.get('registro_id', 'N/A'),
            'IP': log.get('ip_address', 'N/A')
        })
    
    df_logs = pd.DataFrame(logs_data)
    
    # Exibir tabela
    st.dataframe(
        df_logs,
        use_container_width=True,
        hide_index=True
    )
    
    # Botão para exportar
    if st.button("📥 Exportar Logs"):
        csv = df_logs.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"logs_sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Detalhes de um log específico
    st.subheader("🔍 Detalhes do Log")
    
    if len(logs) > 0:
        log_selecionado = st.selectbox(
            "Selecionar Log para Detalhes",
            options=[f"{i+1}. {log['acao']} - {log.get('usuarios', {}).get('nome', 'Sistema')} - {datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')}" 
                    for i, log in enumerate(logs[:50])]  # Limitar a 50 para performance
        )
        
        if log_selecionado:
            log_idx = int(log_selecionado.split('.')[0]) - 1
            log_detalhado = logs[log_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Informações Básicas:**")
                st.write(f"• **Data/Hora:** {datetime.fromisoformat(log_detalhado['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')}")
                st.write(f"• **Ação:** {log_detalhado['acao']}")
                st.write(f"• **Tabela:** {log_detalhado.get('tabela_afetada', 'N/A')}")
                st.write(f"• **Registro ID:** {log_detalhado.get('registro_id', 'N/A')}")
                st.write(f"• **IP:** {log_detalhado.get('ip_address', 'N/A')}")
            
            with col2:
                st.write("**Usuário:**")
                usuario_info = log_detalhado.get('usuarios', {})
                st.write(f"• **Nome:** {usuario_info.get('nome', 'Sistema')}")
                st.write(f"• **Função:** {usuario_info.get('funcao', 'N/A')}")
                st.write(f"• **Empresa:** {usuario_info.get('empresa', 'N/A')}")
            
            # Dados anteriores e novos
            if log_detalhado.get('dados_anteriores'):
                st.write("**Dados Anteriores:**")
                st.json(log_detalhado['dados_anteriores'])
            
            if log_detalhado.get('dados_novos'):
                st.write("**Dados Novos:**")
                st.json(log_detalhado['dados_novos'])

else:
    st.info("Nenhum log encontrado com os filtros aplicados.")

# Ações administrativas
st.subheader("⚙️ Ações Administrativas")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Atualizar Logs", width='stretch'):
        st.rerun()

with col2:
    if st.button("📊 Relatório de Atividade", width='stretch'):
        st.info("Funcionalidade em desenvolvimento")

with col3:
    if st.button("🗑️ Limpar Logs Antigos", width='stretch'):
        st.warning("Esta ação não pode ser desfeita!")
        if st.button("✅ Confirmar Limpeza"):
            st.info("Funcionalidade em desenvolvimento")

# Informações do sistema
st.sidebar.markdown("### ℹ️ Informações")
st.sidebar.markdown("""
**Sistema de Logs:**
- Registra todas as ações dos usuários
- Mantém histórico de alterações
- Rastreamento de acessos
- Auditoria completa

**Filtros Disponíveis:**
- Por ação realizada
- Por usuário
- Por tabela afetada
- Por período de tempo

**Exportação:**
- Download em CSV
- Relatórios personalizados
- Análise de dados
""")

# Estatísticas na sidebar
st.sidebar.markdown("### 📊 Estatísticas Rápidas")
st.sidebar.metric("Logs Hoje", acoes_hoje)
st.sidebar.metric("Usuários Online", usuarios_ativos)
st.sidebar.metric("Ações Mais Comuns", "LOGIN" if logs else "N/A")
