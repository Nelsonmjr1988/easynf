import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from database import DatabaseManager
from config import supabase
from typing import Optional, Dict

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        try:
            import streamlit as st
            self.codigo_cadastro = st.secrets.get('ACCESS_CODE') or os.getenv('ACCESS_CODE') or "Easy2025"
        except Exception:
            import os
            self.codigo_cadastro = os.getenv('ACCESS_CODE') or "Easy2025"
    
    def hash_password(self, password: str) -> str:
        """Cria hash da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """Gera token de sessão"""
        return secrets.token_urlsafe(32)
    
    def is_logged_in(self) -> bool:
        """Verifica se usuário está logado"""
        return 'user_id' in st.session_state and 'session_token' in st.session_state
    
    def get_current_user(self) -> Optional[Dict]:
        """Retorna dados do usuário atual"""
        if not self.is_logged_in():
            return None
        
        try:
            user_id = st.session_state.user_id
            usuario = self.db.get_usuario_by_id(user_id)
            return usuario
        except:
            return None
    
    def login(self, email: str, senha: str) -> bool:
        """Realiza login via Supabase Auth usando email/senha e sincroniza com tabela usuarios"""
        try:
            # Autenticar no Supabase Auth
            auth_res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha,
            })

            # Se falhar, retorna False
            if not getattr(auth_res, "user", None):
                return False

            # Buscar/crear usuário app na tabela usuarios
            usuario = self.db.get_usuario_by_email(email)
            if not usuario:
                meta = getattr(auth_res.user, "user_metadata", {}) or {}
                usuario = self.db.create_usuario({
                    'nome': meta.get('nome') or email.split('@')[0],
                    'cpf': meta.get('cpf') or '',
                    'email': email,
                    'funcao': meta.get('funcao') or 'Usuário',
                    'empresa': meta.get('empresa') or '',
                    'ativo': True,
                })

            if not usuario:
                return False

            # Criar sessão
            st.session_state.user_id = usuario['id']
            st.session_state.session_token = self.generate_session_token()
            st.session_state.user_name = usuario['nome']
            st.session_state.user_role = usuario['funcao']

            # Log da ação
            self.log_action('LOGIN', 'usuarios', usuario['id'], 
                           {'email': email}, {'login_time': datetime.now().isoformat()})

            return True
            
        except Exception as e:
            print(f"Erro no login: {e}")
            return False
    
    def register(self, nome: str, cpf: str, email: str, funcao: str, empresa: str, codigo: str, senha: str) -> bool:
        """Registra usuário no Supabase Auth; faz login e sincroniza perfil em `usuarios`."""
        try:
            # Verificar código de acesso
            if codigo != self.codigo_cadastro:
                return False
            
            # Verificar se CPF já existe
            if self.db.get_usuario_by_cpf(cpf):
                return False
            # Verificar se email já existe
            if self.db.get_usuario_by_email(email):
                return False
            
            # Criar usuário no Supabase Auth
            auth_res = supabase.auth.sign_up({
                "email": email,
                "password": senha,
                "options": {
                    "data": {
                        "nome": nome,
                        "cpf": cpf,
                        "funcao": funcao,
                        "empresa": empresa,
                    }
                }
            })

            if not getattr(auth_res, "user", None):
                return False

            # Garantir que o perfil exista na tabela `usuarios` (gravar já, independente do login)
            usuario = self.db.get_usuario_by_email(email)
            if not usuario:
                usuario = self.db.create_usuario({
                    'nome': nome,
                    'cpf': cpf,
                    'email': email,
                    'funcao': funcao,
                    'empresa': empresa,
                    'ativo': True,
                })
                if usuario:
                    self.log_action('REGISTER', 'usuarios', usuario['id'], {}, {
                        'nome': nome,
                        'cpf': cpf,
                        'email': email,
                        'funcao': funcao,
                        'empresa': empresa,
                        'ativo': True,
                    })

            # Login automático pós-registro (pode falhar se exigir confirmação de email)
            return self.login(email, senha)
            
        except Exception as e:
            print(f"Erro no registro: {e}")
            return False
    
    def logout(self):
        """Realiza logout do usuário"""
        if self.is_logged_in():
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            # Log da ação
            self.log_action('LOGOUT', 'usuarios', st.session_state.user_id, 
                          {'user_name': st.session_state.get('user_name')}, {})
            
            # Limpar sessão
            for key in ['user_id', 'session_token', 'user_name', 'user_role']:
                if key in st.session_state:
                    del st.session_state[key]
    
    def log_action(self, acao: str, tabela_afetada: str = None, registro_id: int = None, 
                   dados_anteriores: Dict = None, dados_novos: Dict = None):
        """Registra ação no log do sistema"""
        try:
            log_data = {
                'usuario_id': st.session_state.get('user_id'),
                'acao': acao,
                'tabela_afetada': tabela_afetada,
                'registro_id': registro_id,
                'dados_anteriores': dados_anteriores,
                'dados_novos': dados_novos,
                'ip_address': '127.0.0.1',  # Em produção, pegar IP real
                'user_agent': 'Streamlit App'
            }
            
            self.db.create_log(log_data)
            
        except Exception as e:
            print(f"Erro ao criar log: {e}")
    
    def require_auth(self):
        """Decorator para proteger páginas"""
        if not self.is_logged_in():
            st.error("🔒 Acesso negado. Faça login para continuar.")
            st.stop()
    
    def is_admin(self) -> bool:
        """Verifica se usuário é administrador"""
        if not self.is_logged_in():
            return False
        return st.session_state.get('user_role') == 'Administrador'
