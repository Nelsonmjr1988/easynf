import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database import DatabaseManager
from utils import (
    formatar_moeda, formatar_valor_entrada, validar_formato_valor,
    validar_data_emissao, validar_valor_positivo, validar_numero_parcelas,
    calcular_parcelas, validar_campos_obrigatorios
)
from config import MATERIAL_STATUS
from auth import AuthManager

st.set_page_config(
    page_title="Lançar Nota Fiscal",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Lançar Nota Fiscal")

# Verificar autenticação
auth = AuthManager()
if not auth.is_logged_in():
    st.switch_page("pages/00_🔐_Login.py")

# Inicializar banco de dados
db = DatabaseManager()

# Carregar dados necessários
fornecedores = db.get_fornecedores()
locais = db.get_locais_aplicacao()

if not fornecedores:
    st.error("❌ Nenhum fornecedor cadastrado. Cadastre um fornecedor primeiro.")
    if st.button("➕ Cadastrar Fornecedor"):
        st.switch_page("pages/01_📝_Lançar_Fornecedor.py")
    st.stop()

if not locais:
    st.error("❌ Nenhum local de aplicação cadastrado. Configure os locais primeiro.")
    if st.button("⚙️ Configurar Locais"):
        st.switch_page("pages/04_⚙️_Configurações.py")
    st.stop()

# Inicializar estado da sessão
if 'nota_data' not in st.session_state:
    st.session_state.nota_data = {}
if 'parcelas_preview' not in st.session_state:
    st.session_state.parcelas_preview = []
if 'show_parcelas_preview' not in st.session_state:
    st.session_state.show_parcelas_preview = False
if 'parcelas_banco' not in st.session_state:
    st.session_state.parcelas_banco = []  # Parcelas salvas no banco

def reset_form():
    """Reseta o formulário"""
    st.session_state.nota_data = {}
    st.session_state.parcelas_preview = []
    st.session_state.show_parcelas_preview = False
    st.session_state.show_confirm_dialog = False
    st.session_state.parcelas_banco = []

def carregar_parcelas_do_banco(nota_id: int):
    """Carrega parcelas existentes do banco de dados"""
    try:
        parcelas = db.get_parcelas_by_nota(nota_id)
        st.session_state.parcelas_banco = parcelas
        return parcelas
    except Exception as e:
        st.error(f"Erro ao carregar parcelas: {e}")
        return []

def calcular_preview_parcelas():
    """Calcula preview das parcelas"""
    if st.session_state.nota_data.get('eh_parcelada') and st.session_state.nota_data.get('valor_total'):
        try:
            valor_total = st.session_state.nota_data['valor_total']
            num_parcelas = st.session_state.nota_data.get('num_parcelas', 1)
            dias_ate_primeira = st.session_state.nota_data.get('dias_ate_primeira', 30)
            intervalo_dias = st.session_state.nota_data.get('intervalo_dias', 30)
            
            # Obter data de emissão
            data_emissao_str = st.session_state.nota_data.get('data_emissao')
            data_emissao = None
            if data_emissao_str:
                data_emissao = datetime.fromisoformat(data_emissao_str).date()
            
            parcelas = calcular_parcelas(valor_total, num_parcelas, dias_ate_primeira, intervalo_dias, data_emissao)
            # Adicionar status_material para cada parcela
            for parcela in parcelas:
                parcela['status_material'] = 'ESTOQUE'  # Valor padrão
            st.session_state.parcelas_preview = parcelas
            st.session_state.show_parcelas_preview = True
        except Exception as e:
            st.error(f"Erro ao calcular parcelas: {e}")

def recalcular_parcelas_apos_edicao(parcela_editada_idx, novo_valor, nova_data, novo_status_material=None):
    """Recalcula as outras parcelas após edição de uma parcela"""
    try:
        valor_total_nota = st.session_state.nota_data.get('valor_total', 0)
        num_parcelas = len(st.session_state.parcelas_preview)
        
        if num_parcelas > 1:
            # Calcular valor médio das parcelas restantes
            valor_restante = valor_total_nota - novo_valor
            num_parcelas_restantes = num_parcelas - 1
            valor_medio_restante = valor_restante / num_parcelas_restantes
            
            # Atualizar as outras parcelas
            for i, parcela in enumerate(st.session_state.parcelas_preview):
                if i != parcela_editada_idx:
                    # Manter a data original ou calcular baseado na nova data
                    if i < parcela_editada_idx:
                        # Parcelas anteriores: manter data original
                        pass
                    else:
                        # Parcelas posteriores: recalcular data baseada na nova data
                        dias_diferenca = (i - parcela_editada_idx) * st.session_state.nota_data.get('intervalo_dias', 30)
                        nova_data_calculada = nova_data + timedelta(days=dias_diferenca)
                        parcela['data_vencimento'] = nova_data_calculada.isoformat()
                    
                    # Atualizar valor
                    parcela['valor'] = round(valor_medio_restante, 2)
            
            # Ajustar a última parcela para manter o valor total exato
            valor_atual_soma = sum(p['valor'] for p in st.session_state.parcelas_preview)
            diferenca = valor_total_nota - valor_atual_soma
            
            if abs(diferenca) > 0.01:
                # Encontrar a última parcela (não editada) e ajustar
                ultima_parcela_idx = -1
                for i in range(num_parcelas - 1, -1, -1):
                    if i != parcela_editada_idx:
                        ultima_parcela_idx = i
                        break
                
                if ultima_parcela_idx >= 0:
                    st.session_state.parcelas_preview[ultima_parcela_idx]['valor'] += diferenca
                    st.session_state.parcelas_preview[ultima_parcela_idx]['valor'] = round(st.session_state.parcelas_preview[ultima_parcela_idx]['valor'], 2)
        
        # Atualizar status_material se fornecido
        if novo_status_material:
            st.session_state.parcelas_preview[parcela_editada_idx]['status_material'] = novo_status_material
        
        # Forçar atualização do preview
        st.session_state.show_parcelas_preview = True
        
    except Exception as e:
        st.error(f"Erro ao recalcular parcelas: {e}")

def recalcular_parcelas_manualmente():
    """Recalcula todas as parcelas manualmente baseado no valor total atual"""
    try:
        valor_total_nota = st.session_state.nota_data.get('valor_total', 0)
        num_parcelas = len(st.session_state.parcelas_preview)
        
        if num_parcelas > 0:
            # Obter data de emissão para recalcular datas
            data_emissao_str = st.session_state.nota_data.get('data_emissao')
            data_emissao = None
            if data_emissao_str:
                data_emissao = datetime.fromisoformat(data_emissao_str).date()
            else:
                data_emissao = date.today()
            
            # Obter parâmetros de parcelamento
            dias_ate_primeira = st.session_state.nota_data.get('dias_ate_primeira', 30)
            intervalo_dias = st.session_state.nota_data.get('intervalo_dias', 30)
            
            # Calcular valor médio baseado no valor total da nota
            valor_medio = valor_total_nota / num_parcelas
            
            # Data da primeira parcela baseada na data de emissão
            data_primeira = data_emissao + timedelta(days=dias_ate_primeira)
            
            # Aplicar valor médio e recalcular datas
            for i, parcela in enumerate(st.session_state.parcelas_preview):
                if i == num_parcelas - 1:
                    # Última parcela: ajustar para manter o valor total exato
                    valor_restante = valor_total_nota - sum(round(valor_medio, 2) for _ in range(num_parcelas - 1))
                    parcela['valor'] = round(valor_restante, 2)
                else:
                    parcela['valor'] = round(valor_medio, 2)
                
                # Recalcular data de vencimento baseada na data de emissão
                data_vencimento = data_primeira + timedelta(days=i * intervalo_dias)
                parcela['data_vencimento'] = data_vencimento.isoformat()
            
            # Forçar atualização do preview
            st.session_state.show_parcelas_preview = True
            
    except Exception as e:
        st.error(f"Erro ao recalcular parcelas: {e}")

def salvar_nota_com_parcelas():
    """Salva a nota e suas parcelas no banco de dados"""
    try:
        # Salvar nota principal
        nota_salva = db.create_nota(st.session_state.nota_data)
        
        if nota_salva:
            # Salvar parcelas se for parcelada
            if st.session_state.nota_data.get('eh_parcelada') and st.session_state.parcelas_preview:
                parcelas_data = []
                for parcela in st.session_state.parcelas_preview:
                    parcelas_data.append({
                        'nota_id': nota_salva['id'],
                        'numero': parcela['numero'],
                        'valor': parcela['valor'],
                        'data_vencimento': parcela['data_vencimento'],
                        'status': 'PENDENTE',
                        'status_material': parcela.get('status_material', 'ESTOQUE')
                    })
                
                parcelas_salvas = db.create_parcelas(parcelas_data)
                
                if parcelas_salvas:
                    return True, f"Nota e {len(parcelas_salvas)} parcelas salvas com sucesso!"
                else:
                    return False, "Nota salva, mas houve erro ao salvar as parcelas"
            else:
                # Para pagamento à vista, criar 1 parcela com status_material da nota
                parcela_data = {
                    'nota_id': nota_salva['id'],
                    'numero': 1,
                    'valor': nota_salva['valor_total'],
                    'data_vencimento': nota_salva['data_emissao'],
                    'status': 'PENDENTE',
                    'status_material': nota_salva.get('status_material', 'ESTOQUE')
                }
                
                parcela_criada = db.create_parcela(parcela_data)
                if parcela_criada:
                    return True, "Nota e parcela salvas com sucesso!"
                else:
                    return False, "Nota salva, mas houve erro ao salvar a parcela"
        else:
            return False, "Erro ao salvar nota. Tente novamente."
            
    except Exception as e:
        return False, f"Erro inesperado: {e}"

# Formulário principal
with st.form("form_nota", clear_on_submit=False):
    st.subheader("📋 Dados da Nota Fiscal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Seleção de Fornecedor
        fornecedor_options = {f"{f['nome']} - {f['cnpj']}": f for f in fornecedores}
        fornecedor_selecionado = st.selectbox(
            "🏢 Fornecedor *",
            options=["Selecione um fornecedor..."] + list(fornecedor_options.keys()),
            help="Selecione o fornecedor da nota fiscal"
        )
        
        if fornecedor_selecionado != "Selecione um fornecedor...":
            fornecedor_obj = fornecedor_options[fornecedor_selecionado]
            st.session_state.nota_data['fornecedor'] = fornecedor_obj['nome']
            # Remover CNPJ dos dados da nota (não existe na tabela)
            
            # Mostrar CNPJ automaticamente
            st.info(f"📄 CNPJ: {fornecedor_obj['cnpj']}")
        
        # Link para adicionar fornecedor
        st.markdown("💡 [➕ Adicionar Fornecedor](pages/01_📝_Lançar_Fornecedor.py)")
    
    with col2:
        # Número da Nota
        numero_nota = st.text_input(
            "🔢 Número da Nota *",
            placeholder="Ex: 000123456",
            help="Número da nota fiscal"
        )
        if numero_nota:
            st.session_state.nota_data['numero_nota'] = numero_nota
            
            # Verificar duplicata
            if st.session_state.nota_data.get('fornecedor'):
                if db.verificar_duplicata_nota(numero_nota, st.session_state.nota_data['fornecedor']):
                    st.error("⚠️ Já existe uma nota com este número para este fornecedor!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Data de Emissão
        data_emissao = st.date_input(
            "📅 Data de Emissão *",
            value=date.today(),
            max_value=date.today(),
            help="Data de emissão da nota fiscal",
            format="DD/MM/YYYY"
        )
        if data_emissao:
            st.session_state.nota_data['data_emissao'] = data_emissao.isoformat()
            # Mostrar data formatada
            st.info(f"📅 Data selecionada: {data_emissao.strftime('%d/%m/%Y')}")
    
    with col2:
        # Valor Total
        valor_input = st.text_input(
            "💰 Valor Total *",
            placeholder="Ex: 1.500,00",
            help="Valor total da nota fiscal"
        )
        if valor_input:
            if validar_formato_valor(valor_input):
                valor_total = formatar_valor_entrada(valor_input)
                if validar_valor_positivo(valor_total):
                    st.session_state.nota_data['valor_total'] = valor_total
                    st.success(f"✅ Valor: {formatar_moeda(valor_total)}")
                else:
                    st.error("❌ Valor deve ser maior que zero")
            else:
                st.error("❌ Formato inválido. Use: 1.500,00")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Local de Aplicação
        local_options = {local['nome']: local['id'] for local in locais}
        local_selecionado = st.selectbox(
            "🏗️ Local de Aplicação *",
            options=["Selecione um local..."] + list(local_options.keys()),
            help="Local onde o material será aplicado"
        )
        if local_selecionado != "Selecione um local...":
            st.session_state.nota_data['local_aplicacao'] = local_options[local_selecionado]
        
        # Link para gerenciar locais
        st.markdown("💡 [⚙️ Gerenciar Locais](pages/04_⚙️_Configurações.py)")
    
    with col2:
        # Status do Material - só aparece para pagamento à vista
        if not st.session_state.nota_data.get('eh_parcelada', False):
            status_options = {v: k for k, v in MATERIAL_STATUS.items()}
            status_selecionado = st.selectbox(
                "📦 Status do Material *",
                options=list(MATERIAL_STATUS.values()),
                help="Status atual do material"
            )
            if status_selecionado:
                st.session_state.nota_data['status_material'] = status_options[status_selecionado]
        else:
            # Para pagamento parcelado, usar valor padrão (não será usado)
            st.session_state.nota_data['status_material'] = 'ESTOQUE'
    
    # Descrição (opcional)
    descricao = st.text_area(
        "📝 Descrição",
        placeholder="Descrição adicional da nota fiscal (opcional)",
        help="Informações adicionais sobre a nota"
    )
    if descricao:
        st.session_state.nota_data['descricao'] = descricao
    
    st.divider()
    
    # Tipo de Pagamento
    st.subheader("💳 Tipo de Pagamento")
    
    tipo_pagamento = st.radio(
        "Selecione o tipo de pagamento:",
        ["À Vista", "Parcelado"],
        horizontal=True
    )
    
    if tipo_pagamento == "Parcelado":
        st.session_state.nota_data['eh_parcelada'] = True
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            num_parcelas = st.number_input(
                "🔢 Número de Parcelas",
                min_value=1,
                max_value=24,
                value=3,
                help="Quantidade de parcelas (1 a 24)"
            )
            if validar_numero_parcelas(num_parcelas):
                st.session_state.nota_data['num_parcelas'] = num_parcelas
            else:
                st.error("❌ Número de parcelas inválido")
        
        with col2:
            dias_ate_primeira = st.number_input(
                "📅 Dias até a Primeira Parcela",
                min_value=1,
                max_value=365,
                value=30,
                help="Quantos dias até a primeira parcela"
            )
            st.session_state.nota_data['dias_ate_primeira'] = dias_ate_primeira
        
        with col3:
            intervalo_dias = st.number_input(
                "⏰ Intervalo entre Parcelas (dias)",
                min_value=1,
                max_value=365,
                value=30,
                help="Intervalo em dias entre as parcelas"
            )
            st.session_state.nota_data['intervalo_dias'] = intervalo_dias
        
        # Calcular preview automaticamente quando os dados mudarem
        if (st.session_state.nota_data.get('valor_total') and 
            st.session_state.nota_data.get('num_parcelas') and
            st.session_state.nota_data.get('dias_ate_primeira') and
            st.session_state.nota_data.get('intervalo_dias')):
            calcular_preview_parcelas()
            
            # Recalcular automaticamente se necessário
            if st.session_state.parcelas_preview:
                valor_total_parcelas = sum(p['valor'] for p in st.session_state.parcelas_preview)
                valor_total_nota = st.session_state.nota_data.get('valor_total', 0)
                
                if abs(valor_total_parcelas - valor_total_nota) > 0.01:
                    # Ajustar automaticamente a última parcela
                    ultima_parcela_idx = len(st.session_state.parcelas_preview) - 1
                    diferenca = valor_total_nota - valor_total_parcelas
                    st.session_state.parcelas_preview[ultima_parcela_idx]['valor'] += diferenca
                    st.session_state.parcelas_preview[ultima_parcela_idx]['valor'] = round(st.session_state.parcelas_preview[ultima_parcela_idx]['valor'], 2)
    
    else:
        st.session_state.nota_data['eh_parcelada'] = False
        st.session_state.show_parcelas_preview = False
    
    # Preview das Parcelas
    if st.session_state.show_parcelas_preview and st.session_state.parcelas_preview:
        st.subheader("👀 Preview das Parcelas")
        st.info("💡 Você pode editar as datas e valores das parcelas antes de salvar")
        
        # Criar DataFrame editável
        df_parcelas = pd.DataFrame(st.session_state.parcelas_preview)
        df_parcelas['Valor Formatado'] = df_parcelas['valor'].apply(formatar_moeda)
        df_parcelas['Data Vencimento'] = pd.to_datetime(df_parcelas['data_vencimento']).dt.strftime('%d/%m/%Y')
        
        # Mostrar informações sobre a data de emissão
        if st.session_state.nota_data.get('data_emissao'):
            data_emissao = datetime.fromisoformat(st.session_state.nota_data['data_emissao']).date()
            st.info(f"📅 **Data de Emissão:** {data_emissao.strftime('%d/%m/%Y')} - Parcelas calculadas a partir desta data")
        
        # Exibir tabela
        st.dataframe(
            df_parcelas[['numero', 'Valor Formatado', 'Data Vencimento', 'status_material']],
            column_config={
                'numero': 'Parcela',
                'Valor Formatado': 'Valor',
                'Data Vencimento': 'Vencimento',
                'status_material': 'Status Material'
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Mostrar valor total das parcelas
        valor_total_parcelas = sum(p['valor'] for p in st.session_state.parcelas_preview)
        st.metric("💰 Valor Total das Parcelas", formatar_moeda(valor_total_parcelas))
        
        # Verificar se estamos editando uma nota existente
        if st.session_state.parcelas_banco:
            st.info("📝 **Modo de Edição**: As parcelas estão sendo carregadas do banco de dados. As alterações serão salvas automaticamente.")
    
    st.divider()
    
    # Botão principal de submit - só aparece quando apropriado
    pode_salvar = True
    
    # Se for parcelado, só pode salvar se tiver preview das parcelas
    if st.session_state.nota_data.get('eh_parcelada'):
        if not st.session_state.show_parcelas_preview or not st.session_state.parcelas_preview:
            pode_salvar = False
            st.warning("⚠️ Configure o parcelamento para continuar")
    
    if pode_salvar:
        salvar_nota = st.form_submit_button("💾 Salvar Nota", type="primary", width='stretch')
    else:
        salvar_nota = False

# Seção de edição de parcelas (fora do formulário)
if st.session_state.show_parcelas_preview and st.session_state.parcelas_preview:
    st.divider()
    st.subheader("✏️ Editar Parcelas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        parcela_editar = st.selectbox(
            "Selecionar Parcela para Editar",
            options=[f"Parcela {p['numero']}" for p in st.session_state.parcelas_preview]
        )
        
        if parcela_editar:
            parcela_idx = int(parcela_editar.split(' ')[1]) - 1
            parcela_atual = st.session_state.parcelas_preview[parcela_idx]
            
            novo_valor = st.number_input(
                "Novo Valor",
                value=float(parcela_atual['valor']),
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
            
            nova_data = st.date_input(
                "Nova Data de Vencimento",
                value=datetime.fromisoformat(parcela_atual['data_vencimento']).date()
            )
            
            # Campo para status_material
            status_options = {v: k for k, v in MATERIAL_STATUS.items()}
            novo_status_material = st.selectbox(
                "Status do Material",
                options=list(MATERIAL_STATUS.values()),
                index=0 if parcela_atual.get('status_material', 'ESTOQUE') == 'ESTOQUE' else 1,
                key=f"status_material_{parcela_idx}"
            )
            
            if st.button("💾 Atualizar Parcela", type="primary", width='stretch'):
                try:
                    # Verificar se temos parcelas do banco para atualizar
                    if st.session_state.parcelas_banco and parcela_idx < len(st.session_state.parcelas_banco):
                        parcela_banco = st.session_state.parcelas_banco[parcela_idx]
                        parcela_id = parcela_banco['id']
                        
                        # Atualizar no banco de dados
                        resultado = db.update_parcela(parcela_id, round(novo_valor, 2), nova_data.isoformat())
                        
                        if resultado:
                            # Atualizar na memória
                            st.session_state.parcelas_preview[parcela_idx]['valor'] = round(novo_valor, 2)
                            st.session_state.parcelas_preview[parcela_idx]['data_vencimento'] = nova_data.isoformat()
                            
                            # Recalcular as outras parcelas para manter consistência
                            recalcular_parcelas_apos_edicao(parcela_idx, novo_valor, nova_data, status_options[novo_status_material])
                            
                            # Atualizar o valor total da nota
                            valor_total_atualizado = sum(p['valor'] for p in st.session_state.parcelas_preview)
                            st.session_state.nota_data['valor_total'] = valor_total_atualizado
                            
                            # Recarregar parcelas do banco para sincronizar
                            carregar_parcelas_do_banco(st.session_state.parcelas_banco[0]['nota_id'])
                            
                            st.success("✅ Parcela atualizada no banco de dados! Preview atualizado.")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar parcela no banco de dados")
                    else:
                        # Se não há parcelas no banco, apenas atualizar na memória
                        st.session_state.parcelas_preview[parcela_idx]['valor'] = round(novo_valor, 2)
                        st.session_state.parcelas_preview[parcela_idx]['data_vencimento'] = nova_data.isoformat()
                        
                        # Recalcular as outras parcelas para manter consistência
                        recalcular_parcelas_apos_edicao(parcela_idx, novo_valor, nova_data, status_options[novo_status_material])
                        
                        # Atualizar o valor total da nota
                        valor_total_atualizado = sum(p['valor'] for p in st.session_state.parcelas_preview)
                        st.session_state.nota_data['valor_total'] = valor_total_atualizado
                        
                        st.success("✅ Parcela atualizada! Preview atualizado.")
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar parcela: {e}")
    
    with col2:
        # Recalcular valor total baseado nas parcelas editadas
        valor_total_parcelas = sum(p['valor'] for p in st.session_state.parcelas_preview)
        st.metric("Valor Total das Parcelas", formatar_moeda(valor_total_parcelas))
        
        # Ajustar automaticamente a última parcela para manter o valor total correto
        valor_total_nota = st.session_state.nota_data.get('valor_total', 0)
        diferenca = valor_total_nota - valor_total_parcelas
        
        if abs(diferenca) > 0.01 and st.session_state.parcelas_preview:
            # Ajustar a última parcela com a diferença
            ultima_parcela_idx = len(st.session_state.parcelas_preview) - 1
            st.session_state.parcelas_preview[ultima_parcela_idx]['valor'] += diferenca
            st.session_state.parcelas_preview[ultima_parcela_idx]['valor'] = round(st.session_state.parcelas_preview[ultima_parcela_idx]['valor'], 2)
            
            # Atualizar o valor total da nota
            st.session_state.nota_data['valor_total'] = sum(p['valor'] for p in st.session_state.parcelas_preview)
        
        # Ações para as parcelas
        st.write("**Ações:**")
        
        if st.button("🔄 Recalcular Todas as Parcelas", type="secondary", width='stretch'):
            recalcular_parcelas_manualmente()
            st.success("✅ Parcelas recalculadas! Preview atualizado.")
            st.rerun()
        
        # Mostrar informações sobre as parcelas
        st.write("**Informações:**")
        st.write(f"• Total de parcelas: {len(st.session_state.parcelas_preview)}")
        st.write(f"• Valor médio: {formatar_moeda(valor_total_parcelas / len(st.session_state.parcelas_preview))}")
        
        # Verificar se há diferenças
        valor_total_nota = st.session_state.nota_data.get('valor_total', 0)
        if abs(valor_total_parcelas - valor_total_nota) > 0.01:
            st.info("💡 As parcelas foram ajustadas automaticamente para manter o valor total correto.")

# Botões de ação fora do formulário
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🔄 Limpar Formulário", type="secondary", width='stretch'):
        reset_form()
        st.rerun()

with col2:
    if st.button("👀 Visualizar Notas", type="secondary", width='stretch'):
        st.switch_page("pages/02_📋_Visualizar_Notas.py")

with col3:
    if st.button("🏠 Página Inicial", type="secondary", width='stretch'):
        st.switch_page("pages/00_🏠_Dashboard.py")

# Processar salvamento
if salvar_nota:
    # Validar campos obrigatórios
    erros = validar_campos_obrigatorios(st.session_state.nota_data)
    
    if erros:
        for erro in erros:
            st.error(f"❌ {erro}")
    else:
        # Verificar duplicata novamente
        if db.verificar_duplicata_nota(
            st.session_state.nota_data['numero_nota'],
            st.session_state.nota_data['fornecedor']
        ):
            st.error("❌ Já existe uma nota com este número para este fornecedor!")
        else:
            # Mostrar popup de confirmação
            st.session_state.show_confirm_dialog = True

# Popup de confirmação usando st.expander() como modal
if st.session_state.get('show_confirm_dialog', False):
    # Criar um popup visual usando st.expander
    with st.expander("🤔 Confirmação de Salvamento", expanded=True):
        st.write("**Dados da Nota:**")
        st.write(f"• Fornecedor: {st.session_state.nota_data['fornecedor']}")
        st.write(f"• Número: {st.session_state.nota_data['numero_nota']}")
        st.write(f"• Valor: {formatar_moeda(st.session_state.nota_data['valor_total'])}")
        st.write(f"• Data de Emissão: {datetime.fromisoformat(st.session_state.nota_data['data_emissao']).strftime('%d/%m/%Y')}")
        
        if st.session_state.nota_data.get('eh_parcelada'):
            st.write(f"• Parcelas: {st.session_state.nota_data.get('num_parcelas', 1)}x")
        
        st.write("---")
        st.write("**Deseja continuar lançando novas notas?**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Sim, continuar", type="primary", width='stretch'):
                # Salvar nota e parcelas no banco de dados
                sucesso, mensagem = salvar_nota_com_parcelas()
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    # Resetar formulário e continuar
                    reset_form()
                    st.session_state.show_confirm_dialog = False
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")
        
        with col2:
            if st.button("🏠 Não, voltar ao início", type="secondary", width='stretch'):
                # Salvar nota e parcelas no banco de dados
                sucesso, mensagem = salvar_nota_com_parcelas()
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    # Voltar à página inicial
                    st.session_state.show_confirm_dialog = False
                    st.switch_page("pages/00_🏠_Dashboard.py")
                else:
                    st.error(f"❌ {mensagem}")
        
        with col3:
            if st.button("❌ Cancelar", type="secondary", width='stretch'):
                st.session_state.show_confirm_dialog = False
                st.rerun()

# Informações da página
st.sidebar.markdown("### ℹ️ Informações")
st.sidebar.markdown("""
**Campos Obrigatórios:**
- Fornecedor
- Número da Nota
- Data de Emissão
- Valor Total
- Local de Aplicação
- Status do Material

**Validações:**
- Número da nota não pode repetir para o mesmo fornecedor
- Data de emissão não pode ser futura
- Valor deve ser positivo
- Parcelas: 2 a 24 parcelas

**Funcionalidades:**
- Preview editável das parcelas
- Validação de duplicatas
- Integração com fornecedores e locais
- Confirmação antes de salvar
""")

# Estatísticas rápidas
st.sidebar.markdown("### 📊 Estatísticas")
total_notas = len(db.get_notas())
total_fornecedores = len(fornecedores)
total_locais = len(locais)

st.sidebar.metric("Total de Notas", total_notas)
st.sidebar.metric("Fornecedores", total_fornecedores)
st.sidebar.metric("Locais", total_locais)