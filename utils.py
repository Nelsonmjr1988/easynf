from datetime import datetime, date, timedelta
from typing import List, Dict
import streamlit as st

def calcular_parcelas(valor_total: float, num_parcelas: int, dias_ate_primeira: int, intervalo_dias: int, data_emissao: date = None) -> List[Dict]:
    """Calcula as parcelas baseado nos parâmetros fornecidos"""
    parcelas = []
    valor_parcela = valor_total / num_parcelas
    
    # Usar data de emissão se fornecida, senão usar data atual
    data_base = data_emissao if data_emissao else date.today()
    
    # Data da primeira parcela baseada na data de emissão
    data_primeira = data_base + timedelta(days=dias_ate_primeira)
    
    for i in range(num_parcelas):
        data_vencimento = data_primeira + timedelta(days=i * intervalo_dias)
        parcelas.append({
            'numero': i + 1,
            'valor': round(valor_parcela, 2),
            'data_vencimento': data_vencimento.isoformat(),
            'status': 'PENDENTE'
        })
    
    return parcelas

def formatar_moeda(valor: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def formatar_valor_entrada(valor_str: str) -> float:
    """Converte string de valor brasileiro para float"""
    try:
        # Remove R$ e espaços
        valor_limpo = valor_str.replace('R$', '').replace(' ', '').strip()
        
        # Se tem vírgula, é formato brasileiro (1.500,02)
        if ',' in valor_limpo:
            # Remove pontos de milhares e troca vírgula por ponto
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        
        return float(valor_limpo)
    except (ValueError, AttributeError):
        return 0.0

def validar_formato_valor(valor_str: str) -> bool:
    """Valida se o formato do valor está correto"""
    try:
        formatar_valor_entrada(valor_str)
        return True
    except:
        return False

def validar_data_emissao(data_emissao: date) -> bool:
    """Valida se a data de emissão não é futura"""
    return data_emissao <= date.today()

def validar_valor_positivo(valor: float) -> bool:
    """Valida se o valor é positivo"""
    return valor > 0

def validar_numero_parcelas(num_parcelas: int) -> bool:
    """Valida se o número de parcelas é válido"""
    return 1 <= num_parcelas <= 24

def obter_status_parcela(data_vencimento: str, status_atual: str) -> str:
    """Determina o status da parcela baseado na data de vencimento"""
    if status_atual == 'PAGA':
        return 'PAGA'
    
    data_venc = datetime.fromisoformat(data_vencimento).date()
    if data_venc < date.today():
        return 'VENCIDA'
    else:
        return 'PENDENTE'

def calcular_dias_vencimento(data_vencimento: str) -> int:
    """Calcula quantos dias faltam para o vencimento"""
    data_venc = datetime.fromisoformat(data_vencimento).date()
    return (data_venc - date.today()).days

def obter_cor_status(status: str) -> str:
    """Retorna cor para o status"""
    cores = {
        'PAGA': '#28a745',
        'PENDENTE': '#ffc107',
        'VENCIDA': '#dc3545'
    }
    return cores.get(status, '#6c757d')

def obter_icone_status(status: str) -> str:
    """Retorna ícone para o status"""
    icones = {
        'PAGA': '✅',
        'PENDENTE': '⏳',
        'VENCIDA': '⚠️'
    }
    return icones.get(status, '❓')

@st.cache_data
def carregar_locais_aplicacao():
    """Carrega locais de aplicação do cache"""
    from database import DatabaseManager
    db = DatabaseManager()
    return db.get_locais_aplicacao()

def validar_campos_obrigatorios(nota_data: Dict) -> List[str]:
    """Valida campos obrigatórios e retorna lista de erros"""
    erros = []
    
    if not nota_data.get('numero_nota'):
        erros.append("Número da nota é obrigatório")
    
    if not nota_data.get('fornecedor'):
        erros.append("Fornecedor é obrigatório")
    
    if not nota_data.get('valor_total') or nota_data['valor_total'] <= 0:
        erros.append("Valor total deve ser maior que zero")
    
    if not nota_data.get('data_emissao'):
        erros.append("Data de emissão é obrigatória")
    
    if not nota_data.get('local_aplicacao'):
        erros.append("Local de aplicação é obrigatório")
    
    return erros