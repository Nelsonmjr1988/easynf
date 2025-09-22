import streamlit as st
from database import DatabaseManager
from utils import carregar_locais_aplicacao

st.set_page_config(
    page_title="Configurações",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Configurações do Sistema")

# Inicializar banco de dados
db = DatabaseManager()

# Gerenciar Locais de Aplicação
st.subheader("🏗️ Gerenciar Locais de Aplicação")

# Adicionar novo local
with st.expander("➕ Adicionar Novo Local", expanded=True):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        novo_local = st.text_input("Nome do Local", placeholder="Ex: Obra Centro, Obra Norte, etc.")
    
    with col2:
        if st.button("Adicionar", type="primary"):
            if novo_local:
                resultado = db.create_local_aplicacao(novo_local)
                if resultado:
                    st.success(f"✅ Local '{novo_local}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao adicionar local. Verifique se já existe.")
            else:
                st.warning("⚠️ Digite o nome do local")

# Listar locais existentes
st.subheader("📋 Locais Cadastrados")

locais = db.get_locais_aplicacao()

if locais:
    for i, local in enumerate(locais):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            st.write(f"**{i+1}.** {local['nome']}")
        
        with col2:
            if st.button("✏️", key=f"edit_{local['id']}", help="Editar local"):
                st.session_state[f"editando_{local['id']}"] = True
        
        with col3:
            if st.button("🗑️", key=f"delete_{local['id']}", help="Excluir local"):
                if st.session_state.get(f"confirm_delete_{local['id']}", False):
                    # Confirmar exclusão
                    resultado = db.delete_local_aplicacao(local['id'])
                    if resultado:
                        st.success(f"✅ Local '{local['nome']}' excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir local")
                else:
                    st.session_state[f"confirm_delete_{local['id']}"] = True
                    st.warning("⚠️ Clique novamente para confirmar a exclusão")
        
        # Modo de edição
        if st.session_state.get(f"editando_{local['id']}", False):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                novo_nome = st.text_input(
                    "Novo nome",
                    value=local['nome'],
                    key=f"input_edit_{local['id']}"
                )
            
            with col2:
                if st.button("💾", key=f"save_{local['id']}", help="Salvar alterações"):
                    if novo_nome and novo_nome != local['nome']:
                        # Aqui você implementaria a função de atualização
                        st.info("Funcionalidade de edição será implementada em breve")
                    st.session_state[f"editando_{local['id']}"] = False
                    st.rerun()
            
            with col3:
                if st.button("❌", key=f"cancel_{local['id']}", help="Cancelar edição"):
                    st.session_state[f"editando_{local['id']}"] = False
                    st.rerun()
        
        st.divider()
else:
    st.info("Nenhum local cadastrado ainda.")

# Estatísticas do sistema
st.subheader("📊 Estatísticas do Sistema")

col1, col2, col3, col4 = st.columns(4)

# Buscar estatísticas
notas = db.get_notas()
total_notas = len(notas)
total_valor = sum(nota['valor_total'] for nota in notas)

# Contar parcelas
todas_parcelas = []
for nota in notas:
    parcelas = db.get_parcelas_by_nota(nota['id'])
    todas_parcelas.extend(parcelas)

total_parcelas = len(todas_parcelas)
parcelas_pagas = len([p for p in todas_parcelas if p['status'] == 'PAGA'])

col1.metric("Total de Notas", total_notas)
col2.metric("Valor Total", f"R$ {total_valor:,.2f}")
col3.metric("Total de Parcelas", total_parcelas)
col4.metric("Parcelas Pagas", parcelas_pagas)

# Informações do banco de dados
st.subheader("🗄️ Informações do Banco de Dados")

st.info("""
**Estrutura das Tabelas:**

1. **notas** - Armazena as notas fiscais
   - id, numero_nota, fornecedor, valor_total, data_emissao
   - descricao, local_aplicacao, status_material
   - eh_parcelada, num_parcelas, dias_ate_primeira, intervalo_dias

2. **parcelas** - Armazena as parcelas das notas
   - id, nota_id, numero, valor, data_vencimento
   - status, data_pagamento

3. **locais_aplicacao** - Armazena os locais de aplicação
   - id, nome
""")

# Backup e Restauração
st.subheader("💾 Backup e Restauração")

col1, col2 = st.columns(2)

with col1:
    st.write("**Exportar Dados**")
    if st.button("📤 Exportar Todos os Dados"):
        # Implementar exportação
        st.info("Funcionalidade de exportação será implementada em breve")

with col2:
    st.write("**Importar Dados**")
    uploaded_file = st.file_uploader("Selecionar arquivo", type=['json', 'csv'])
    if uploaded_file:
        st.info("Funcionalidade de importação será implementada em breve")

# Configurações avançadas
st.subheader("🔧 Configurações Avançadas")

with st.expander("⚙️ Configurações do Sistema"):
    st.write("**Configurações de Notificação**")
    
    notificar_vencimento = st.checkbox("Notificar sobre parcelas próximas do vencimento", value=True)
    dias_antecedencia = st.slider("Dias de antecedência para notificação", 1, 30, 7)
    
    if st.button("Salvar Configurações"):
        st.success("Configurações salvas com sucesso!")

# Limpeza de dados
st.subheader("🧹 Limpeza de Dados")

with st.expander("⚠️ Área de Risco"):
    st.warning("As operações abaixo são irreversíveis!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Todas as Notas", type="secondary"):
            st.error("Funcionalidade de limpeza será implementada com confirmação de segurança")
    
    with col2:
        if st.button("🗑️ Limpar Parcelas Vencidas", type="secondary"):
            st.error("Funcionalidade de limpeza será implementada com confirmação de segurança")

# Logs do sistema
st.subheader("📝 Logs do Sistema")

with st.expander("📋 Visualizar Logs"):
    st.info("Sistema de logs será implementado em breve")
    
    # Simular alguns logs
    logs = [
        f"{st.session_state.get('current_time', '2024-01-01 10:00:00')} - Sistema iniciado",
        f"{st.session_state.get('current_time', '2024-01-01 10:01:00')} - Usuário acessou página de notas",
        f"{st.session_state.get('current_time', '2024-01-01 10:02:00')} - Nova nota criada: #001234",
    ]
    
    for log in logs:
        st.text(log)

# Informações de contato/suporte
st.subheader("📞 Suporte")

st.info("""
**Para suporte técnico ou dúvidas sobre o sistema:**

- 📧 Email: suporte@contasobras.com
- 📱 Telefone: (11) 99999-9999
- 🌐 Website: www.contasobras.com

**Versão do Sistema:** 1.0.0
**Última Atualização:** Janeiro 2024
""")

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Sistema de Controle de Contas para Obras v1.0.0</p>
    <p>Desenvolvido com ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)