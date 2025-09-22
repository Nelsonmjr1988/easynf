import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import DatabaseManager
from utils import formatar_moeda
import re

st.set_page_config(
    page_title="Lançar Fornecedor",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Lançar Novo Fornecedor")

# Demonstração da máscara
with st.expander("💡 Como usar a máscara de CNPJ", expanded=False):
    st.markdown("""
    **Instruções:**
    1. Digite apenas os números do CNPJ
    2. A formatação será aplicada automaticamente
    3. O CNPJ deve ter exatamente 14 dígitos
    
    **Exemplo:**
    - Digite: `12345678000190`
    - Resultado: `12.345.678/0001-90`
    """)
    
    # Exemplo interativo
    exemplo = st.text_input("Teste aqui:", placeholder="12345678000190", key="exemplo_cnpj")
    if exemplo:
        exemplo_formatado = formatar_cnpj(exemplo)
        st.code(f"Entrada: {exemplo}")
        st.code(f"Saída: {exemplo_formatado}")
        if validar_cnpj(exemplo_formatado):
            st.success("✅ CNPJ válido!")
        else:
            st.warning("⚠️ CNPJ incompleto")



# Funções para formatação e validação de CNPJ
def formatar_cnpj(cnpj):
    """Aplica máscara de CNPJ: 00.000.000/0000-00"""
    if not cnpj:
        return ""
    
    # Remove tudo que não é dígito
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    
    # Limita a 14 dígitos
    cnpj_limpo = cnpj_limpo[:14]
    
    # Aplica a máscara progressivamente
    if len(cnpj_limpo) == 0:
        return ""
    elif len(cnpj_limpo) <= 2:
        return cnpj_limpo
    elif len(cnpj_limpo) <= 5:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:]}"
    elif len(cnpj_limpo) <= 8:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:]}"
    elif len(cnpj_limpo) <= 12:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:]}"
    else:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:14]}"

def validar_cnpj(cnpj):
    """Valida se o CNPJ tem 14 dígitos"""
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    return len(cnpj_limpo) == 14

# Inicializar banco de dados
db = DatabaseManager()

# Formulário principal
with st.form("form_lancar_fornecedor"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome_fornecedor = st.text_input("Nome do Fornecedor *", placeholder="Ex: Empresa ABC Ltda")
        
        # Campo CNPJ com máscara em tempo real
        cnpj_input = st.text_input(
            "CNPJ *", 
            placeholder="00.000.000/0000-00", 
            max_chars=14,
            key="cnpj_input"
        )
        
        # JavaScript para máscara em tempo real
        st.markdown("""
        <script>
        function aplicarMascaraCNPJ(input) {
            // Remove tudo que não é dígito
            let valor = input.value.replace(/\D/g, '');
            
            // Limita a 14 dígitos
            valor = valor.substring(0, 14);
            
            // Aplica a máscara progressivamente
            if (valor.length <= 2) {
                input.value = valor;
            } else if (valor.length <= 5) {
                input.value = valor.replace(/(\d{2})(\d+)/, '$1.$2');
            } else if (valor.length <= 8) {
                input.value = valor.replace(/(\d{2})(\d{3})(\d+)/, '$1.$2.$3');
            } else if (valor.length <= 12) {
                input.value = valor.replace(/(\d{2})(\d{3})(\d{3})(\d+)/, '$1.$2.$3/$4');
            } else {
                input.value = valor.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
            }
        }
        
        // Aplicar máscara quando a página carregar
        document.addEventListener('DOMContentLoaded', function() {
            // Aguardar um pouco para o Streamlit carregar
            setTimeout(function() {
                const inputs = document.querySelectorAll('input[data-testid="stTextInput"]');
                inputs.forEach(function(input) {
                    if (input.placeholder.includes('00.000.000/0000-00')) {
                        input.addEventListener('input', function() {
                            aplicarMascaraCNPJ(this);
                        });
                    }
                });
            }, 1000);
        });
        </script>
        """, unsafe_allow_html=True)
        
        # Aplicar máscara e mostrar resultado
        if cnpj_input:
            cnpj = formatar_cnpj(cnpj_input)
            
            # Mostrar CNPJ formatado
            if validar_cnpj(cnpj):
                st.success(f"✅ CNPJ: {cnpj}")
            else:
                st.warning(f"⚠️ CNPJ: {cnpj} (incompleto - precisa de 14 dígitos)")
        else:
            cnpj = ""
        
        telefone = st.text_input("Telefone *", placeholder="Ex: (11) 99999-9999")
    
    with col2:
        vendedor = st.text_input("Vendedor", placeholder="Nome do vendedor (opcional)")
    
    # Botão de envio
    submitted = st.form_submit_button("💾 Salvar Fornecedor", type="primary", width='stretch')
    
    if submitted:
        # Validações
        erros = []
        
        if not nome_fornecedor:
            erros.append("Nome do fornecedor é obrigatório")
        if not cnpj:
            erros.append("CNPJ é obrigatório")
        elif not validar_cnpj(cnpj):
            erros.append("CNPJ deve ter 14 dígitos")
        if not telefone:
            erros.append("Telefone é obrigatório")
        
        # Verificar duplicata por CNPJ
        if cnpj and validar_cnpj(cnpj) and db.verificar_fornecedor_cnpj(cnpj):
            erros.append(f"Já existe um fornecedor cadastrado com o CNPJ: {cnpj}")
        
        if erros:
            for erro in erros:
                st.error(erro)
        else:
            # Dados do fornecedor
            fornecedor_data = {
                'nome': nome_fornecedor,
                'cnpj': cnpj,
                'telefone': telefone,
                'vendedor': vendedor if vendedor else None
            }
            
            # Salvar fornecedor
            fornecedor_criado = db.create_fornecedor(fornecedor_data)
            
            if fornecedor_criado:
                st.success("✅ Fornecedor salvo com sucesso!")
                
                # Mostrar dados salvos
                st.info(f"""
                **📄 Fornecedor #{fornecedor_criado['id']}** salvo com sucesso!
                - **Nome:** {fornecedor_criado['nome']}
                - **CNPJ:** {fornecedor_criado['cnpj']}
                - **Telefone:** {fornecedor_criado['telefone']}
                - **Vendedor:** {fornecedor_criado['vendedor'] or 'Não informado'}
                """)
                
                # Botões de ação
                st.session_state._fornecedor_actions_ready = True
            else:
                st.error("❌ Erro ao criar fornecedor. Tente novamente.")

# Botões de ação fora do form (para evitar erro do Streamlit)
if st.session_state.get('_fornecedor_actions_ready'):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Novo Fornecedor", type="primary", width='stretch'):
            st.session_state._fornecedor_actions_ready = False
            st.rerun()
    with col2:
        if st.button("🏠 Página Inicial", width='stretch'):
            st.switch_page("pages/00_🏠_Dashboard.py")
    with col3:
        if st.button("📋 Ver Fornecedores", width='stretch'):
            st.switch_page("pages/02_📋_Visualizar_Fornecedores.py")

# Informações sobre o sistema
st.sidebar.markdown("### ℹ️ Informações")
st.sidebar.markdown("""
**Campos Obrigatórios:**
- Nome do Fornecedor
- CNPJ
- Telefone

**Campos Opcionais:**
- Vendedor

**Validações:**
- CNPJ único no sistema
- Formato de CNPJ válido
""")

# Estatísticas rápidas
st.sidebar.markdown("### 📊 Estatísticas")
total_fornecedores = len(db.get_fornecedores())
st.sidebar.metric("Total de Fornecedores", total_fornecedores)