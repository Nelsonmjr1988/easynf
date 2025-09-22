import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import DatabaseManager
from utils import (
    formatar_moeda, obter_status_parcela, calcular_dias_vencimento,
    obter_cor_status, obter_icone_status
)
from config import MATERIAL_STATUS, PARCELA_STATUS
from auth import AuthManager

st.set_page_config(
    page_title="Visualizar Notas",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Visualizar Notas")

# Verificar autenticação
auth = AuthManager()
if not auth.is_logged_in():
    st.switch_page("pages/00_🔐_Login.py")

# Inicializar banco de dados
db = DatabaseManager()

# Carregar dados
notas = db.get_notas()
# Ordenar por sequência de lançamento (ID crescente)
notas = sorted(notas, key=lambda n: n.get('id', 0))
locais = db.get_locais_aplicacao()
locais_dict = {local['id']: local['nome'] for local in locais}

if not notas:
    st.info("Nenhuma nota cadastrada ainda.")
    st.stop()

# Filtros
st.subheader("🔍 Filtros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    fornecedores = sorted(list(set(nota['fornecedor'] for nota in notas)))
    fornecedor_filtro = st.selectbox("Fornecedor", ["Todos"] + fornecedores)

with col2:
    locais_filtro = ["Todos"] + [local['nome'] for local in locais]
    local_filtro = st.selectbox("Local de Aplicação", locais_filtro)

with col3:
    status_filtro = st.selectbox("Status do Material", ["Todos"] + list(MATERIAL_STATUS.values()))

with col4:
    status_parcela_filtro = st.selectbox("Status da Parcela", ["Todos"] + list(PARCELA_STATUS.values()))

# Aplicar filtros
notas_filtradas = notas.copy()

if fornecedor_filtro != "Todos":
    notas_filtradas = [n for n in notas_filtradas if n['fornecedor'] == fornecedor_filtro]

if local_filtro != "Todos":
    local_id = next((l['id'] for l in locais if l['nome'] == local_filtro), None)
    if local_id:
        notas_filtradas = [n for n in notas_filtradas if n['local_aplicacao'] == local_id]

if status_filtro != "Todos":
    status_key = next((k for k, v in MATERIAL_STATUS.items() if v == status_filtro), None)
    if status_key:
        # Para notas parceladas, verificar se alguma parcela tem o status desejado
        notas_com_status = []
        for nota in notas_filtradas:
            if nota.get('eh_parcelada', False):
                # Para notas parceladas, verificar parcelas
                parcelas = db.get_parcelas_by_nota(nota['id'])
                if any(p.get('status_material') == status_key for p in parcelas):
                    notas_com_status.append(nota)
            else:
                # Para notas à vista, verificar status da nota
                if nota['status_material'] == status_key:
                    notas_com_status.append(nota)
        notas_filtradas = notas_com_status

# Exibir notas filtradas
if not notas_filtradas:
    st.warning("Nenhuma nota encontrada com os filtros aplicados.")
    st.stop()

st.subheader(f"📊 {len(notas_filtradas)} Nota(s) Encontrada(s)")

# Tabela de notas
for i, nota in enumerate(notas_filtradas):
    # Criar container para cada nota
    with st.container():
        # Header com informações resumidas e ações
        col_header1, col_header2, col_header3, col_header4 = st.columns([4, 1, 1, 1])
        
        with col_header1:
            # Informações principais da nota
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #333;">📄 Nota {nota['numero_nota']} - {nota['fornecedor']}</h4>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    💰 {formatar_moeda(nota['valor_total'])} | 
                    📅 {datetime.fromisoformat(nota['data_emissao']).strftime('%d/%m/%Y')} | 
                    📦 {MATERIAL_STATUS.get(nota['status_material'], 'N/A')} | 
                    🏗️ {locais_dict.get(nota['local_aplicacao'], 'N/A')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_header2:
            if st.button("✏️ Editar", key=f"edit_{nota['id']}", width='stretch'):
                st.session_state.edit_nota_id = nota['id']
                st.switch_page("pages/01_📝_Lançar_Nota.py")
        
        with col_header3:
            if st.button("🗑️ Deletar", key=f"delete_{nota['id']}", width='stretch'):
                st.session_state.delete_nota_id = nota['id']
                st.session_state.show_delete_confirm = True
        
        with col_header4:
            if st.button("📊 Detalhes", key=f"details_{nota['id']}", width='stretch'):
                # Toggle para mostrar/ocultar detalhes
                if f"show_details_{nota['id']}" not in st.session_state:
                    st.session_state[f"show_details_{nota['id']}"] = False
                st.session_state[f"show_details_{nota['id']}"] = not st.session_state[f"show_details_{nota['id']}"]
                st.rerun()
        
        # Popup de confirmação para deletar
        if st.session_state.get('show_delete_confirm', False) and st.session_state.get('delete_nota_id') == nota['id']:
            st.warning("⚠️ **Confirmação de Exclusão**")
            st.write(f"Tem certeza que deseja deletar a nota {nota['numero_nota']} - {nota['fornecedor']}?")
            st.write("**Esta ação não pode ser desfeita!**")
            
            col_confirm1, col_confirm2, col_confirm3 = st.columns(3)
            
            with col_confirm1:
                if st.button("✅ Sim, Deletar", key=f"confirm_delete_{nota['id']}", width='stretch'):
                    # Deletar nota (isso também deletará as parcelas por cascade)
                    resultado = db.delete_nota(nota['id'])
                    if resultado:
                        st.success("Nota deletada com sucesso!")
                        st.session_state.show_delete_confirm = False
                        st.session_state.delete_nota_id = None
                        st.rerun()
                    else:
                        st.error("Erro ao deletar nota")
            
            with col_confirm2:
                if st.button("❌ Cancelar", key=f"cancel_delete_{nota['id']}", width='stretch'):
                    st.session_state.show_delete_confirm = False
                    st.session_state.delete_nota_id = None
                    st.rerun()
        
        # Detalhes da nota (expandível)
        if st.session_state.get(f'show_details_{nota["id"]}', False):
            with st.expander(f"📋 Detalhes da Nota {nota['numero_nota']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Fornecedor:** {nota['fornecedor']}")
                    st.write(f"**Valor Total:** {formatar_moeda(nota['valor_total'])}")
                    st.write(f"**Data de Emissão:** {datetime.fromisoformat(nota['data_emissao']).strftime('%d/%m/%Y')}")
                    st.write(f"**Local de Aplicação:** {locais_dict.get(nota['local_aplicacao'], 'N/A')}")
                    st.write(f"**Status do Material:** {MATERIAL_STATUS.get(nota['status_material'], 'N/A')}")
                    
                    if nota['descricao']:
                        st.write(f"**Descrição:** {nota['descricao']}")
                
                with col2:
                    # Ações da nota
                    st.write("**Ações:**")
                    
                    # Alterar local de aplicação
                    novo_local = st.selectbox(
                        f"Alterar Local",
                        options=[locais_dict.get(nota['local_aplicacao'], 'N/A')] + [l['nome'] for l in locais if l['id'] != nota['local_aplicacao']],
                        key=f"local_{nota['id']}"
                    )
                    
                    if st.button(f"Atualizar Local", key=f"btn_local_{nota['id']}", width='stretch'):
                        local_id = next((l['id'] for l in locais if l['nome'] == novo_local), None)
                        if local_id and local_id != nota['local_aplicacao']:
                            resultado = db.update_nota(nota['id'], {'local_aplicacao': local_id})
                            if resultado:
                                st.success("Local atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao atualizar local")
                    
                    # Alterar status do material da nota (apenas para pagamento à vista)
                    if not nota.get('eh_parcelada', False):
                        novo_status = st.selectbox(
                            f"Alterar Status do Material",
                            options=[MATERIAL_STATUS.get(nota['status_material'], 'N/A')] + [v for k, v in MATERIAL_STATUS.items() if k != nota['status_material']],
                            key=f"status_{nota['id']}"
                        )
                        
                        if st.button(f"Atualizar Status", key=f"btn_status_{nota['id']}", width='stretch'):
                            status_key = next((k for k, v in MATERIAL_STATUS.items() if v == novo_status), None)
                            if status_key and status_key != nota['status_material']:
                                resultado = db.update_nota(nota['id'], {'status_material': status_key})
                                if resultado:
                                    st.success("Status atualizado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar status")
                    else:
                        st.info("💡 Para notas parceladas, altere o status individual de cada parcela abaixo.")
                
                # Parcelas da nota (dentro do expander)
                st.subheader("💳 Parcelas")
                parcelas = db.get_parcelas_by_nota(nota['id'])
                
                if parcelas:
                    # Atualizar status das parcelas baseado na data
                    for parcela in parcelas:
                        novo_status = obter_status_parcela(parcela['data_vencimento'], parcela['status'])
                        if novo_status != parcela['status']:
                            db.update_parcela_status(parcela['id'], novo_status)
                    
                    # Recarregar parcelas com status atualizado
                    parcelas = db.get_parcelas_by_nota(nota['id'])
                    
                    # Criar DataFrame das parcelas (robusto a campos ausentes)
                    df_parcelas = pd.DataFrame(parcelas)
                    # Garantir colunas esperadas
                    for col, default in [('valor', 0.0), ('data_vencimento', None), ('status', 'PENDENTE'), ('numero', None)]:
                        if col not in df_parcelas.columns:
                            df_parcelas[col] = default
                    # Formatações
                    df_parcelas['Valor'] = df_parcelas['valor'].apply(lambda v: formatar_moeda(float(v) if v is not None else 0.0))
                    df_parcelas['Vencimento'] = pd.to_datetime(df_parcelas['data_vencimento'], errors='coerce').dt.strftime('%d/%m/%Y')
                    df_parcelas['Dias para Vencimento'] = df_parcelas['data_vencimento'].apply(lambda d: calcular_dias_vencimento(d) if d else '')
                    df_parcelas['Status'] = df_parcelas['status'].apply(lambda x: f"{obter_icone_status(x)} {PARCELA_STATUS.get(x, x)}")
                    
                    # Aplicar filtro de status da parcela se selecionado
                    if status_parcela_filtro != "Todos":
                        status_key = next((k for k, v in PARCELA_STATUS.items() if v == status_parcela_filtro), None)
                        if status_key:
                            df_parcelas = df_parcelas[df_parcelas['status'] == status_key]
                    
                    # Adicionar coluna de status do material se existir
                    if 'status_material' in df_parcelas.columns:
                        df_parcelas['Status Material'] = df_parcelas['status_material'].apply(lambda x: f"📦 {MATERIAL_STATUS.get(x, x)}")
                        colunas_exibir = ['numero', 'Valor', 'Vencimento', 'Dias para Vencimento', 'Status', 'Status Material']
                        config_colunas = {
                            'numero': 'Parcela',
                            'Valor': 'Valor',
                            'Vencimento': 'Vencimento',
                            'Dias para Vencimento': 'Dias para Vencimento',
                            'Status': 'Status',
                            'Status Material': 'Status Material'
                        }
                    else:
                        colunas_exibir = ['numero', 'Valor', 'Vencimento', 'Dias para Vencimento', 'Status']
                        config_colunas = {
                            'numero': 'Parcela',
                            'Valor': 'Valor',
                            'Vencimento': 'Vencimento',
                            'Dias para Vencimento': 'Dias para Vencimento',
                            'Status': 'Status'
                        }
                    
                    # Exibir tabela de parcelas
                    st.dataframe(
                        df_parcelas[colunas_exibir],
                        column_config=config_colunas,
                        hide_index=True
                    )
                    
                    # Ações para cada parcela
                    st.subheader("⚡ Ações Rápidas")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Marcar parcela como paga
                        parcelas_pendentes = [p for p in parcelas if p['status'] in ['PENDENTE', 'VENCIDA']]
                        if parcelas_pendentes:
                            parcela_pagar = st.selectbox(
                                "Marcar como Paga",
                                options=[f"Parcela {p['numero']} - {formatar_moeda(p['valor'])} - {datetime.fromisoformat(p['data_vencimento']).strftime('%d/%m/%Y')}" for p in parcelas_pendentes],
                                key=f"pagar_{nota['id']}"
                            )
                            
                            if st.button("✅ Marcar como Paga", key=f"btn_pagar_{nota['id']}", width='stretch'):
                                # Encontrar a parcela selecionada na lista de parcelas pendentes
                                parcela_numero = int(parcela_pagar.split(' - ')[0].split(' ')[1])
                                parcela_selecionada = next((p for p in parcelas_pendentes if p['numero'] == parcela_numero), None)
                                
                                if parcela_selecionada:
                                    parcela_id = parcela_selecionada['id']
                                    resultado = db.update_parcela_status(parcela_id, 'PAGA', date.today())
                                    if resultado:
                                        st.success("Parcela marcada como paga!")
                                        st.rerun()
                                    else:
                                        st.error("Erro ao marcar parcela como paga")
                                else:
                                    st.error("Parcela não encontrada")
                    
                    with col2:
                        # Alterar status do material da parcela
                        tem_status_material = any(('status_material' in p and p.get('status_material') is not None) for p in parcelas) if parcelas else False
                        if tem_status_material:
                            parcela_status_material = st.selectbox(
                                "Alterar Status do Material",
                                options=[f"Parcela {p['numero']} - {formatar_moeda(p['valor'])} - {MATERIAL_STATUS.get(p.get('status_material', 'ESTOQUE'), 'N/A')}" for p in parcelas],
                                key=f"status_material_{nota['id']}"
                            )
                            
                            if st.button("📦 Alterar Status Material", key=f"btn_status_material_{nota['id']}", width='stretch'):
                                # Encontrar a parcela selecionada
                                parcela_numero = int(parcela_status_material.split(' - ')[0].split(' ')[1])
                                parcela_selecionada = next((p for p in parcelas if p['numero'] == parcela_numero), None)
                                
                                if parcela_selecionada:
                                    parcela_id = parcela_selecionada['id']
                                    # Alternar entre ESTOQUE e EM_USO
                                    novo_status = 'EM_USO' if parcela_selecionada.get('status_material', 'ESTOQUE') == 'ESTOQUE' else 'ESTOQUE'
                                    
                                    # Atualizar status_material no banco de dados
                                    resultado = db.update_parcela_status_material(parcela_id, novo_status)
                                    if resultado:
                                        st.success(f"Status do material alterado para {MATERIAL_STATUS.get(novo_status, novo_status)}!")
                                        st.rerun()
                                    else:
                                        st.error("Erro ao alterar status do material")
                                else:
                                    st.error("Parcela não encontrada")
                        else:
                            st.info("💡 Status do material não disponível para esta nota.")
                    
                    with col3:
                        # Estatísticas das parcelas
                        total_parcelas = len(parcelas)
                        parcelas_pagas = len([p for p in parcelas if p['status'] == 'PAGA'])
                        parcelas_pendentes = len([p for p in parcelas if p['status'] == 'PENDENTE'])
                        parcelas_vencidas = len([p for p in parcelas if p['status'] == 'VENCIDA'])
                        
                        st.metric("Total de Parcelas", total_parcelas)
                        st.metric("Pagas", parcelas_pagas)
                        st.metric("Pendentes", parcelas_pendentes)
                        st.metric("Vencidas", parcelas_vencidas)
                else:
                    st.info("Nenhuma parcela encontrada para esta nota.")

# Resumo geral
st.subheader("📊 Resumo Geral")

# Informação sobre o filtro aplicado
if status_filtro != "Todos":
    st.info(f"💡 **Filtro Ativo:** {status_filtro} - Mostrando apenas parcelas com este status do material")

col1, col2, col3, col4 = st.columns(4)

# Calcular valor total baseado no filtro de status do material
total_valor_filtrado = 0
total_parcelas_filtradas = 0

for nota in notas_filtradas:
    parcelas = db.get_parcelas_by_nota(nota['id'])
    
    if status_filtro != "Todos":
        status_key = next((k for k, v in MATERIAL_STATUS.items() if v == status_filtro), None)
        if status_key:
            # Somar apenas parcelas com o status filtrado
            parcelas_filtradas = [p for p in parcelas if p.get('status_material') == status_key]
            total_valor_filtrado += sum(p['valor'] for p in parcelas_filtradas)
            total_parcelas_filtradas += len(parcelas_filtradas)
        else:
            # Se não há filtro de status, somar todas as parcelas
            total_valor_filtrado += sum(p['valor'] for p in parcelas)
            total_parcelas_filtradas += len(parcelas)
    else:
        # Se não há filtro de status, somar todas as parcelas
        total_valor_filtrado += sum(p['valor'] for p in parcelas)
        total_parcelas_filtradas += len(parcelas)

col1.metric("Total de Notas", len(notas_filtradas))

# Mostrar valor baseado no filtro
so_status_todos = (status_filtro == "Todos")
sem_filtros_globais = (fornecedor_filtro == "Todos" and local_filtro == "Todos" and so_status_todos)
if not so_status_todos:
    col2.metric(f"Valor ({status_filtro})", formatar_moeda(total_valor_filtrado))
    col3.metric(f"Parcelas ({status_filtro})", total_parcelas_filtradas)
else:
    # Quando não há filtros (fornecedor/local/status), usar a view para garantir exatidão
    if sem_filtros_globais:
        try:
            total_view = db.get_total_de_notas_view()
            valor_total_geral = total_view.get('total_de_notas', 0) or 0
            col2.metric("Valor Total", formatar_moeda(valor_total_geral))
        except Exception:
            col2.metric("Valor Total", formatar_moeda(total_valor_filtrado))
    else:
        # Com outros filtros ativos, manter a soma do conjunto filtrado
        col2.metric("Valor Total", formatar_moeda(total_valor_filtrado))
    col3.metric("Total de Parcelas", total_parcelas_filtradas)

# Contar parcelas por status (apenas as filtradas)
todas_parcelas = []
for nota in notas_filtradas:
    parcelas = db.get_parcelas_by_nota(nota['id'])
    
    if status_filtro != "Todos":
        status_key = next((k for k, v in MATERIAL_STATUS.items() if v == status_filtro), None)
        if status_key:
            # Incluir apenas parcelas com o status filtrado
            parcelas_filtradas = [p for p in parcelas if p.get('status_material') == status_key]
            todas_parcelas.extend(parcelas_filtradas)
        else:
            todas_parcelas.extend(parcelas)
    else:
        todas_parcelas.extend(parcelas)

parcelas_pagas = len([p for p in todas_parcelas if p['status'] == 'PAGA'])
parcelas_pendentes = len([p for p in todas_parcelas if p['status'] == 'PENDENTE'])
parcelas_vencidas = len([p for p in todas_parcelas if p['status'] == 'VENCIDA'])

col4.metric("Parcelas Pagas", parcelas_pagas)

# Gráfico de status das parcelas
if todas_parcelas:
    st.subheader("📈 Distribuição de Status das Parcelas")
    
    import plotly.express as px
    
    status_data = {
        'Status': ['Pagas', 'Pendentes', 'Vencidas'],
        'Quantidade': [parcelas_pagas, parcelas_pendentes, parcelas_vencidas],
        'Cor': ['#28a745', '#ffc107', '#dc3545']
    }
    
    fig = px.pie(
        values=status_data['Quantidade'],
        names=status_data['Status'],
        title="Status das Parcelas",
        color_discrete_sequence=status_data['Cor']
    )
    
    st.plotly_chart(fig, use_container_width=True)