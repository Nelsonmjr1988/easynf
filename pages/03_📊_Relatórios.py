import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from database import DatabaseManager
from utils import formatar_moeda
from config import MATERIAL_STATUS, PARCELA_STATUS

st.set_page_config(
    page_title="Relatórios",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Relatórios")

# Inicializar banco de dados
db = DatabaseManager()

# Carregar dados
notas = db.get_notas()
locais = db.get_locais_aplicacao()
locais_dict = {local['id']: local['nome'] for local in locais}

if not notas:
    st.info("Nenhuma nota cadastrada ainda.")
    st.stop()

# Filtros de período
st.subheader("📅 Filtros de Período")

col1, col2 = st.columns(2)

with col1:
    ano_atual = date.today().year
    anos = list(range(ano_atual - 2, ano_atual + 1))
    ano_selecionado = st.selectbox("Ano", anos, index=len(anos)-1)

with col2:
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    mes_selecionado = st.selectbox("Mês", meses, index=date.today().month - 1)

# Gerar relatório mensal
relatorio = db.get_relatorio_mensal(meses.index(mes_selecionado) + 1, ano_selecionado)

# Resumo executivo
st.subheader("📈 Resumo Executivo")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Pago",
    formatar_moeda(relatorio['total_pago']),
    delta=f"{relatorio['total_pago']:.2f} R$"
)

col2.metric(
    "Total Pendente",
    formatar_moeda(relatorio['total_pendente']),
    delta=f"{relatorio['total_pendente']:.2f} R$"
)

col3.metric(
    "Total Vencido",
    formatar_moeda(relatorio['total_vencido']),
    delta=f"{relatorio['total_vencido']:.2f} R$"
)

total_geral = relatorio['total_pago'] + relatorio['total_pendente'] + relatorio['total_vencido']
col4.metric(
    "Total Geral",
    formatar_moeda(total_geral),
    delta=f"{total_geral:.2f} R$"
)

# Gráficos
st.subheader("📊 Análise Visual")

col1, col2 = st.columns(2)

# Gráfico de pizza - Status das parcelas
with col1:
    if total_geral > 0:
        status_data = {
            'Status': ['Pagas', 'Pendentes', 'Vencidas'],
            'Valor': [relatorio['total_pago'], relatorio['total_pendente'], relatorio['total_vencido']],
            'Cor': ['#28a745', '#ffc107', '#dc3545']
        }
        
        fig_pizza = px.pie(
            values=status_data['Valor'],
            names=status_data['Status'],
            title=f"Distribuição por Status - {mes_selecionado}/{ano_selecionado}",
            color_discrete_sequence=status_data['Cor']
        )
        
        st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir no gráfico")

# Gráfico de barras - Comparativo mensal
with col2:
    # Buscar dados dos últimos 6 meses para comparação
    dados_comparativo = []
    for i in range(6):
        data_ref = date(ano_selecionado, meses.index(mes_selecionado) + 1, 1) - timedelta(days=30*i)
        rel_mes = db.get_relatorio_mensal(data_ref.month, data_ref.year)
        
        dados_comparativo.append({
            'Mês': f"{data_ref.month:02d}/{data_ref.year}",
            'Pago': rel_mes['total_pago'],
            'Pendente': rel_mes['total_pendente'],
            'Vencido': rel_mes['total_vencido']
        })
    
    if dados_comparativo:
        df_comparativo = pd.DataFrame(dados_comparativo)
        df_comparativo = df_comparativo.sort_values('Mês')
        
        fig_barras = go.Figure()
        
        fig_barras.add_trace(go.Bar(
            name='Pago',
            x=df_comparativo['Mês'],
            y=df_comparativo['Pago'],
            marker_color='#28a745'
        ))
        
        fig_barras.add_trace(go.Bar(
            name='Pendente',
            x=df_comparativo['Mês'],
            y=df_comparativo['Pendente'],
            marker_color='#ffc107'
        ))
        
        fig_barras.add_trace(go.Bar(
            name='Vencido',
            x=df_comparativo['Mês'],
            y=df_comparativo['Vencido'],
            marker_color='#dc3545'
        ))
        
        fig_barras.update_layout(
            title=f"Evolução dos Valores - Últimos 6 Meses",
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            barmode='stack'
        )
        
        st.plotly_chart(fig_barras, use_container_width=True)

# Tabela detalhada de parcelas
st.subheader("📋 Detalhamento das Parcelas")

if relatorio['parcelas']:
    # Preparar dados da tabela
    parcelas_data = []
    for parcela in relatorio['parcelas']:
        nota = parcela.get('notas', {})
        local_nome = locais_dict.get(nota.get('local_aplicacao'), 'N/A')
        
        parcelas_data.append({
            'Nota': nota.get('numero_nota', 'N/A'),
            'Fornecedor': nota.get('fornecedor', 'N/A'),
            'Parcela': parcela['numero'],
            'Valor': parcela['valor'],
            'Vencimento': datetime.fromisoformat(parcela['data_vencimento']).strftime('%d/%m/%Y'),
            'Status': PARCELA_STATUS.get(parcela['status'], parcela['status']),
            'Local': local_nome,
            'Material': MATERIAL_STATUS.get(nota.get('status_material'), 'N/A')
        })
    
    df_parcelas = pd.DataFrame(parcelas_data)
    df_parcelas['Valor'] = df_parcelas['Valor'].apply(formatar_moeda)
    
    # Filtros para a tabela
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filtro = st.selectbox("Filtrar por Status", ["Todos"] + list(PARCELA_STATUS.values()))
    
    with col2:
        fornecedores = sorted(list(set(df_parcelas['Fornecedor'])))
        fornecedor_filtro = st.selectbox("Filtrar por Fornecedor", ["Todos"] + fornecedores)
    
    with col3:
        locais_filtro = st.selectbox("Filtrar por Local", ["Todos"] + list(set(df_parcelas['Local'])))
    
    # Aplicar filtros
    df_filtrado = df_parcelas.copy()
    
    if status_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Status'] == status_filtro]
    
    if fornecedor_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == fornecedor_filtro]
    
    if locais_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Local'] == locais_filtro]
    
    # Exibir tabela
    st.dataframe(
        df_filtrado,
        column_config={
            'Nota': 'Número da Nota',
            'Fornecedor': 'Fornecedor',
            'Parcela': 'Parcela',
            'Valor': 'Valor',
            'Vencimento': 'Vencimento',
            'Status': 'Status',
            'Local': 'Local de Aplicação',
            'Material': 'Status do Material'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Estatísticas da tabela filtrada
    if not df_filtrado.empty:
        st.subheader("📊 Estatísticas do Filtro")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_filtrado = sum(float(v.replace('R$ ', '').replace('.', '').replace(',', '.')) for v in df_filtrado['Valor'])
        
        col1.metric("Total de Parcelas", len(df_filtrado))
        col2.metric("Valor Total", formatar_moeda(total_filtrado))
        
        status_counts = df_filtrado['Status'].value_counts()
        col3.metric("Mais Comum", status_counts.index[0] if not status_counts.empty else "N/A")
        col4.metric("Quantidade", status_counts.iloc[0] if not status_counts.empty else 0)
else:
    st.info(f"Nenhuma parcela encontrada para {mes_selecionado}/{ano_selecionado}")

# Análise por local de aplicação
st.subheader("🏗️ Análise por Local de Aplicação")

if locais:
    local_stats = []
    
    for local in locais:
        # Buscar parcelas deste local no período
        parcelas_local = []
        for parcela in relatorio['parcelas']:
            nota = parcela.get('notas', {})
            if nota.get('local_aplicacao') == local['id']:
                parcelas_local.append(parcela)
        
        if parcelas_local:
            total_local = sum(p['valor'] for p in parcelas_local)
            pago_local = sum(p['valor'] for p in parcelas_local if p['status'] == 'PAGA')
            pendente_local = sum(p['valor'] for p in parcelas_local if p['status'] == 'PENDENTE')
            vencido_local = sum(p['valor'] for p in parcelas_local if p['status'] == 'VENCIDA')
            
            local_stats.append({
                'Local': local['nome'],
                'Total': total_local,
                'Pago': pago_local,
                'Pendente': pendente_local,
                'Vencido': vencido_local,
                'Parcelas': len(parcelas_local)
            })
    
    if local_stats:
        df_local = pd.DataFrame(local_stats)
        df_local = df_local.sort_values('Total', ascending=False)
        
        # Gráfico de barras por local
        fig_local = px.bar(
            df_local,
            x='Local',
            y=['Pago', 'Pendente', 'Vencido'],
            title=f"Valores por Local - {mes_selecionado}/{ano_selecionado}",
            color_discrete_map={'Pago': '#28a745', 'Pendente': '#ffc107', 'Vencido': '#dc3545'}
        )
        
        fig_local.update_layout(
            xaxis_title="Local de Aplicação",
            yaxis_title="Valor (R$)",
            barmode='stack'
        )
        
        st.plotly_chart(fig_local, use_container_width=True)
        
        # Tabela de locais
        df_local['Total'] = df_local['Total'].apply(formatar_moeda)
        df_local['Pago'] = df_local['Pago'].apply(formatar_moeda)
        df_local['Pendente'] = df_local['Pendente'].apply(formatar_moeda)
        df_local['Vencido'] = df_local['Vencido'].apply(formatar_moeda)
        
        st.dataframe(
            df_local,
            column_config={
                'Local': 'Local de Aplicação',
                'Total': 'Total',
                'Pago': 'Pago',
                'Pendente': 'Pendente',
                'Vencido': 'Vencido',
                'Parcelas': 'Nº Parcelas'
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nenhum dado encontrado para os locais no período selecionado")
else:
    st.info("Nenhum local de aplicação cadastrado")

# Exportar dados
st.subheader("💾 Exportar Dados")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Exportar Relatório CSV"):
        if relatorio['parcelas']:
            df_export = pd.DataFrame(parcelas_data)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"relatorio_{mes_selecionado.lower()}_{ano_selecionado}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhum dado para exportar")

with col2:
    if st.button("📋 Exportar Resumo"):
        resumo = f"""
RELATÓRIO MENSAL - {mes_selecionado.upper()}/{ano_selecionado}

RESUMO EXECUTIVO:
- Total Pago: {formatar_moeda(relatorio['total_pago'])}
- Total Pendente: {formatar_moeda(relatorio['total_pendente'])}
- Total Vencido: {formatar_moeda(relatorio['total_vencido'])}
- Total Geral: {formatar_moeda(total_geral)}

ESTATÍSTICAS:
- Total de Parcelas: {len(relatorio['parcelas'])}
- Parcelas Pagas: {len([p for p in relatorio['parcelas'] if p['status'] == 'PAGA'])}
- Parcelas Pendentes: {len([p for p in relatorio['parcelas'] if p['status'] == 'PENDENTE'])}
- Parcelas Vencidas: {len([p for p in relatorio['parcelas'] if p['status'] == 'VENCIDA'])}

Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        
        st.download_button(
            label="Download Resumo",
            data=resumo,
            file_name=f"resumo_{mes_selecionado.lower()}_{ano_selecionado}.txt",
            mime="text/plain"
        )