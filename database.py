from supabase import Client
import streamlit as st
from config import supabase
from datetime import datetime, date
from typing import List, Dict, Optional
import json

class DatabaseManager:
    def __init__(self):
        self.supabase = supabase
    
    def create_tables(self):
        """Cria as tabelas necessárias no Supabase"""
        # Esta função seria executada uma vez para criar as tabelas
        # Como estamos usando Supabase, as tabelas devem ser criadas via interface web
        pass
    
    # Operações para Notas
    def create_nota(self, nota_data: Dict) -> Dict:
        """Cria uma nova nota"""
        try:
            result = self.supabase.table('notas').insert(nota_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar nota: {e}")
            return None
    
    def get_notas(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Busca todas as notas com filtros opcionais"""
        try:
            query = self.supabase.table('notas').select('*')
            
            if filters:
                if filters.get('fornecedor'):
                    query = query.eq('fornecedor', filters['fornecedor'])
                if filters.get('local_aplicacao'):
                    query = query.eq('local_aplicacao', filters['local_aplicacao'])
                if filters.get('status_material'):
                    query = query.eq('status_material', filters['status_material'])
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar notas: {e}")
            return []
    
    def verificar_duplicata_nota(self, numero_nota: str, fornecedor: str) -> bool:
        """Verifica se já existe uma nota com o mesmo número e fornecedor"""
        try:
            result = self.supabase.table('notas').select('id, numero_nota, fornecedor').eq('numero_nota', numero_nota).eq('fornecedor', fornecedor).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Erro ao verificar duplicata: {e}")
            return False
    
    def update_nota(self, nota_id: int, update_data: Dict) -> Dict:
        """Atualiza uma nota"""
        try:
            # Buscar estado anterior para log
            prev_q = self.supabase.table('notas').select('*').eq('id', nota_id).execute()
            dados_anteriores = prev_q.data[0] if prev_q.data else None

            result = self.supabase.table('notas').update(update_data).eq('id', nota_id).execute()
            updated = result.data[0] if result.data else None

            # Log de atualização
            try:
                if updated:
                    self.create_log({
                        'usuario_id': st.session_state.get('user_id'),
                        'acao': 'UPDATE',
                        'tabela_afetada': 'notas',
                        'registro_id': nota_id,
                        'dados_anteriores': dados_anteriores,
                        'dados_novos': update_data
                    })
            except Exception as _:
                pass

            return updated
        except Exception as e:
            print(f"Erro ao atualizar nota: {e}")
            return None
    
    def delete_nota(self, nota_id: int) -> bool:
        """Deleta uma nota e suas parcelas"""
        try:
            # Buscar dados anteriores
            prev_nota_q = self.supabase.table('notas').select('*').eq('id', nota_id).execute()
            prev_nota = prev_nota_q.data[0] if prev_nota_q.data else None
            prev_parcelas_q = self.supabase.table('parcelas').select('*').eq('nota_id', nota_id).execute()
            prev_parcelas = prev_parcelas_q.data if prev_parcelas_q.data else []
            # Primeiro deleta as parcelas
            self.supabase.table('parcelas').delete().eq('nota_id', nota_id).execute()
            # Depois deleta a nota
            self.supabase.table('notas').delete().eq('id', nota_id).execute()
            # Log
            try:
                self.create_log({
                    'usuario_id': st.session_state.get('user_id'),
                    'acao': 'DELETE',
                    'tabela_afetada': 'notas',
                    'registro_id': nota_id,
                    'dados_anteriores': {'nota': prev_nota, 'parcelas': prev_parcelas},
                    'dados_novos': None
                })
            except Exception as _:
                pass
            return True
        except Exception as e:
            print(f"Erro ao deletar nota: {e}")
            return False
    
    # Operações para Parcelas
    def create_parcela(self, parcela_data: Dict) -> Dict:
        """Cria uma nova parcela"""
        try:
            # Garantir que status_material seja incluído
            if 'status_material' not in parcela_data:
                parcela_data['status_material'] = 'ESTOQUE'  # Valor padrão
                
            result = self.supabase.table('parcelas').insert(parcela_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar parcela: {e}")
            return None
    
    def create_parcelas(self, parcelas_data: List[Dict]) -> List[Dict]:
        """Cria múltiplas parcelas"""
        try:
            print(f"Debug: Tentando criar {len(parcelas_data)} parcelas")
            print(f"Debug: Dados das parcelas: {parcelas_data}")
            
            result = self.supabase.table('parcelas').insert(parcelas_data).execute()
            
            print(f"Debug: Resultado da inserção: {result}")
            
            if result.data:
                print(f"Debug: {len(result.data)} parcelas criadas com sucesso")
                return result.data
            else:
                print("Debug: Nenhuma parcela foi criada")
                return []
        except Exception as e:
            print(f"Erro ao criar parcelas: {e}")
            print(f"Debug: Tipo do erro: {type(e)}")
            return []
    
    def get_parcelas_by_nota(self, nota_id: int) -> List[Dict]:
        """Busca parcelas de uma nota específica"""
        try:
            result = self.supabase.table('parcelas').select('*').eq('nota_id', nota_id).order('data_vencimento').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar parcelas: {e}")
            return []
    
    def update_parcela_status(self, parcela_id: int, status: str, data_pagamento: Optional[date] = None) -> Dict:
        """Atualiza status de uma parcela"""
        try:
            prev_q = self.supabase.table('parcelas').select('*').eq('id', parcela_id).execute()
            dados_anteriores = prev_q.data[0] if prev_q.data else None
            update_data = {'status': status}
            if data_pagamento:
                update_data['data_pagamento'] = data_pagamento.isoformat()
            
            result = self.supabase.table('parcelas').update(update_data).eq('id', parcela_id).execute()
            updated = result.data[0] if result.data else None
            # Log
            try:
                if updated:
                    self.create_log({
                        'usuario_id': st.session_state.get('user_id'),
                        'acao': 'UPDATE',
                        'tabela_afetada': 'parcelas',
                        'registro_id': parcela_id,
                        'dados_anteriores': dados_anteriores,
                        'dados_novos': update_data
                    })
            except Exception as _:
                pass
            return updated
        except Exception as e:
            print(f"Erro ao atualizar parcela: {e}")
            return None
    
    def update_parcela(self, parcela_id: int, valor: float, data_vencimento: str) -> Dict:
        """Atualiza valor e data de vencimento de uma parcela"""
        try:
            prev_q = self.supabase.table('parcelas').select('*').eq('id', parcela_id).execute()
            dados_anteriores = prev_q.data[0] if prev_q.data else None
            update_data = {
                'valor': valor,
                'data_vencimento': data_vencimento
            }
            
            result = self.supabase.table('parcelas').update(update_data).eq('id', parcela_id).execute()
            updated = result.data[0] if result.data else None
            # Log
            try:
                if updated:
                    self.create_log({
                        'usuario_id': st.session_state.get('user_id'),
                        'acao': 'UPDATE',
                        'tabela_afetada': 'parcelas',
                        'registro_id': parcela_id,
                        'dados_anteriores': dados_anteriores,
                        'dados_novos': update_data
                    })
            except Exception as _:
                pass
            return updated
        except Exception as e:
            print(f"Erro ao atualizar parcela: {e}")
            return None
    
    def update_parcela_status_material(self, parcela_id: int, status_material: str) -> Dict:
        """Atualiza status_material de uma parcela"""
        try:
            prev_q = self.supabase.table('parcelas').select('*').eq('id', parcela_id).execute()
            dados_anteriores = prev_q.data[0] if prev_q.data else None
            update_data = {
                'status_material': status_material
            }
            
            result = self.supabase.table('parcelas').update(update_data).eq('id', parcela_id).execute()
            updated = result.data[0] if result.data else None
            # Log
            try:
                if updated:
                    self.create_log({
                        'usuario_id': st.session_state.get('user_id'),
                        'acao': 'UPDATE',
                        'tabela_afetada': 'parcelas',
                        'registro_id': parcela_id,
                        'dados_anteriores': dados_anteriores,
                        'dados_novos': update_data
                    })
            except Exception as _:
                pass
            return updated
        except Exception as e:
            print(f"Erro ao atualizar status_material da parcela: {e}")
            return None
    
    def update_parcelas_batch(self, parcelas_data: List[Dict]) -> List[Dict]:
        """Atualiza múltiplas parcelas em lote"""
        try:
            updated_parcelas = []
            for parcela in parcelas_data:
                result = self.supabase.table('parcelas').update({
                    'valor': parcela['valor'],
                    'data_vencimento': parcela['data_vencimento']
                }).eq('id', parcela['id']).execute()
                
                if result.data:
                    updated_parcelas.append(result.data[0])
            
            return updated_parcelas
        except Exception as e:
            print(f"Erro ao atualizar parcelas em lote: {e}")
            return []
    
    # Operações para Usuários
    def create_usuario(self, usuario_data: Dict) -> Dict:
        """Cria um novo usuário"""
        try:
            result = self.supabase.table('usuarios').insert(usuario_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return None
    
    def get_usuario_by_id(self, usuario_id: int) -> Dict:
        """Busca usuário por ID"""
        try:
            result = self.supabase.table('usuarios').select('*').eq('id', usuario_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar usuário por ID: {e}")
            return None
    
    def get_usuario_by_cpf(self, cpf: str) -> Dict:
        """Busca usuário por CPF"""
        try:
            result = self.supabase.table('usuarios').select('*').eq('cpf', cpf).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar usuário por CPF: {e}")
            return None

    def get_usuario_by_email(self, email: str) -> Dict:
        """Busca usuário por email"""
        try:
            result = self.supabase.table('usuarios').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar usuário por email: {e}")
            return None
    
    def get_usuarios(self) -> List[Dict]:
        """Busca todos os usuários"""
        try:
            result = self.supabase.table('usuarios').select('*').order('nome').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return []
    
    def update_usuario(self, usuario_id: int, update_data: Dict) -> Dict:
        """Atualiza dados do usuário"""
        try:
            result = self.supabase.table('usuarios').update(update_data).eq('id', usuario_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao atualizar usuário: {e}")
            return None
    
    def delete_usuario(self, usuario_id: int) -> bool:
        """Desativa usuário (soft delete)"""
        try:
            result = self.supabase.table('usuarios').update({'ativo': False}).eq('id', usuario_id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Erro ao desativar usuário: {e}")
            return False
    
    # Operações para Logs
    def create_log(self, log_data: Dict) -> Dict:
        """Cria um novo log"""
        try:
            result = self.supabase.table('logs_sistema').insert(log_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar log: {e}")
            return None
    
    def get_logs(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Busca logs do sistema"""
        try:
            result = self.supabase.table('logs_sistema').select('''
                *,
                usuarios!logs_sistema_usuario_id_fkey(nome, funcao, empresa)
            ''').order('created_at', desc=True).limit(limit).offset(offset).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar logs: {e}")
            return []
    
    def get_logs_by_usuario(self, usuario_id: int, limit: int = 50) -> List[Dict]:
        """Busca logs de um usuário específico"""
        try:
            result = self.supabase.table('logs_sistema').select('''
                *,
                usuarios!logs_sistema_usuario_id_fkey(nome, funcao, empresa)
            ''').eq('usuario_id', usuario_id).order('created_at', desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar logs do usuário: {e}")
            return []
    
    def get_logs_by_acao(self, acao: str, limit: int = 50) -> List[Dict]:
        """Busca logs por tipo de ação"""
        try:
            result = self.supabase.table('logs_sistema').select('''
                *,
                usuarios!logs_sistema_usuario_id_fkey(nome, funcao, empresa)
            ''').eq('acao', acao).order('created_at', desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar logs por ação: {e}")
            return []
    
    # Operações para Locais de Aplicação
    def create_local_aplicacao(self, nome: str) -> Dict:
        """Cria um novo local de aplicação"""
        try:
            result = self.supabase.table('locais_aplicacao').insert({'nome': nome}).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar local: {e}")
            return None
    
    def get_locais_aplicacao(self) -> List[Dict]:
        """Busca todos os locais de aplicação"""
        try:
            result = self.supabase.table('locais_aplicacao').select('*').order('nome').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar locais: {e}")
            return []
    
    def delete_local_aplicacao(self, local_id: int) -> bool:
        """Deleta um local de aplicação"""
        try:
            self.supabase.table('locais_aplicacao').delete().eq('id', local_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar local: {e}")
            return False
    
    # Relatórios
    def get_relatorio_mensal(self, mes: int, ano: int) -> Dict:
        """Gera relatório mensal de contas"""
        try:
            # Busca parcelas do mês
            start_date = f"{ano}-{mes:02d}-01"
            if mes == 12:
                end_date = f"{ano+1}-01-01"
            else:
                end_date = f"{ano}-{mes+1:02d}-01"
            
            parcelas = self.supabase.table('parcelas').select('*, notas(*)').gte('data_vencimento', start_date).lt('data_vencimento', end_date).execute()
            
            if not parcelas.data:
                return {'parcelas': [], 'total_pago': 0, 'total_pendente': 0, 'total_vencido': 0}
            
            total_pago = sum(p['valor'] for p in parcelas.data if p['status'] == 'PAGA')
            total_pendente = sum(p['valor'] for p in parcelas.data if p['status'] == 'PENDENTE')
            total_vencido = sum(p['valor'] for p in parcelas.data if p['status'] == 'VENCIDA')
            
            return {
                'parcelas': parcelas.data,
                'total_pago': total_pago,
                'total_pendente': total_pendente,
                'total_vencido': total_vencido
            }
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return {'parcelas': [], 'total_pago': 0, 'total_pendente': 0, 'total_vencido': 0}

    # Views de resumo
    def get_resumo_notas_parcelas(self) -> Dict:
        """Lê a view vw_resumo_notas_parcelas e retorna um único registro com totais."""
        try:
            result = self.supabase.table('vw_resumo_notas_parcelas').select('*').execute()
            if result.data:
                # algumas instalações retornam lista com 1 item
                return result.data[0]
            return {
                'total_em_estoque': 0,
                'total_em_uso': 0,
                'total_de_notas': 0,
                'total_a_pagar': 0,
            }
        except Exception as e:
            print(f"Erro ao ler vw_resumo_notas_parcelas: {e}")
            return {
                'total_em_estoque': 0,
                'total_em_uso': 0,
                'total_de_notas': 0,
                'total_a_pagar': 0,
            }

    def get_total_de_notas_view(self) -> Dict:
        """Lê a view vw_total_de_notas e retorna um único registro com o total."""
        try:
            result = self.supabase.table('vw_total_de_notas').select('*').execute()
            if result.data:
                return result.data[0]
            return {'total_de_notas': 0}
        except Exception as e:
            print(f"Erro ao ler vw_total_de_notas: {e}")
            return {'total_de_notas': 0}
    
    # Operações para Fornecedores
    def create_fornecedor(self, fornecedor_data: Dict) -> Dict:
        """Cria um novo fornecedor"""
        try:
            result = self.supabase.table('fornecedores').insert(fornecedor_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar fornecedor: {e}")
            return None
    
    def get_fornecedores(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Busca todos os fornecedores com filtros opcionais"""
        try:
            query = self.supabase.table('fornecedores').select('*')
            
            if filters:
                if filters.get('nome'):
                    query = query.ilike('nome', f"%{filters['nome']}%")
                if filters.get('cnpj'):
                    query = query.eq('cnpj', filters['cnpj'])
                if filters.get('vendedor'):
                    query = query.ilike('vendedor', f"%{filters['vendedor']}%")
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar fornecedores: {e}")
            return []
    
    def verificar_fornecedor_cnpj(self, cnpj: str) -> bool:
        """Verifica se já existe um fornecedor com o mesmo CNPJ"""
        try:
            result = self.supabase.table('fornecedores').select('id, cnpj').eq('cnpj', cnpj).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Erro ao verificar CNPJ: {e}")
            return False
    
    def get_fornecedor_by_id(self, fornecedor_id: int) -> Dict:
        """Busca um fornecedor pelo ID"""
        try:
            result = self.supabase.table('fornecedores').select('*').eq('id', fornecedor_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar fornecedor: {e}")
            return None
    
    def update_fornecedor(self, fornecedor_id: int, fornecedor_data: Dict) -> Dict:
        """Atualiza um fornecedor"""
        try:
            result = self.supabase.table('fornecedores').update(fornecedor_data).eq('id', fornecedor_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao atualizar fornecedor: {e}")
            return None
    
    def delete_fornecedor(self, fornecedor_id: int) -> bool:
        """Exclui um fornecedor"""
        try:
            result = self.supabase.table('fornecedores').delete().eq('id', fornecedor_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao excluir fornecedor: {e}")
            return False