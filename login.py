import streamlit as st
from auth import AuthManager
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Login - EasyNF",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS simples e funcional
st.markdown("""
<style>
    /* Esconder header e sidebar */
    .stApp > header {
        display: none !important;
    }
    
    .css-1d391kg {
        display: none !important;
    }
    
    .main .block-container {
        padding: 16 !important;
        max-width: 100% !important;
    }
    
    /* Layout principal */
    .login-container {
        display: flex;
        width: 100vw;
        height: 100vh;
        margin: 16;
        padding: 16;
    }
    
    .left-panel {
        flex: 0 0 50%;
        background: white;
        padding: 16;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .right-panel {
        flex: 0 0 50%;
        background: url('https://img.freepik.com/fotos-premium/guindastes-pontilham-o-canteiro-de-obras-contribuindo-para-o-processo-de-construcao-vertical-mobile-wallpaper_896558-11337.jpg?w=360') center/cover;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        position: relative;
    }
    
    .right-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 16;
        right: 16;
        bottom: 0;
        background: rgba(0,0,0,0.4);
    }
    
    .right-content {
        position: relative;
        z-index: 1;
    }
    
    .right-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    .right-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        margin-bottom: 2rem;
    }
    
    .right-description {
        font-size: 1rem;
        opacity: 0.8;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        max-width: 400px;
    }
    
    .form-container {
        width: 100%;
        max-width: 400px;
    }
    
    .form-title {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .form-subtitle {
        color: #666;
        margin-bottom: 2rem;
        text-align: center;
        font-size: 1rem;
    }
    
    /* Responsivo */
    @media (max-width: 1000px) {
        .left-panel {
            flex: 1;
            width: 100%;
        }
        
        .right-panel {
            display: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Inicializar gerenciador de autenticação
auth = AuthManager()

# Verificar se já está logado
if auth.is_logged_in():
    st.switch_page("pages/00_🏠_Dashboard.py")

# Título principal (sempre visível)
st.markdown("# 🔐 EasyNF")
st.markdown("**Sistema de Contas para Obras**")
st.markdown("---")

# Layout principal
st.markdown("""
<div class="login-container">
    <div class="left-panel">
        <div class="form-container">
""", unsafe_allow_html=True)

# Tabs para Login e Cadastro
tab1, tab2 = st.tabs(["🔑 Login", "📝 Cadastro"])

with tab1:
    st.markdown("### Faça seu Login")
    
    with st.form("login_form"):
        cpf = st.text_input(
            "CPF",
            placeholder="000.000.000-00",
            help="Digite apenas números"
        )
        
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Sua senha"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_button = st.form_submit_button("🔑 Entrar", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🔄 Limpar", use_container_width=True):
                st.rerun()
        
        if login_button:
            if cpf and senha:
                if auth.login(cpf, senha):
                    st.success("✅ Login realizado com sucesso!")
                    st.balloons()
                    st.switch_page("pages/00_🏠_Dashboard.py")
                else:
                    st.error("❌ CPF ou senha incorretos!")
            else:
                st.warning("⚠️ Preencha todos os campos!")

with tab2:
    st.markdown("### Cadastre-se no Sistema")
    
    # Verificar se já tem código de acesso
    if 'codigo_verificado' not in st.session_state:
        st.session_state.codigo_verificado = False
    
    if not st.session_state.codigo_verificado:
        # Etapa 1: Verificar código de acesso
        st.info("🔐 **Acesso Restrito** - Digite o código de acesso para continuar")
        
        with st.form("codigo_form"):
            codigo = st.text_input(
                "Código de Acesso",
                type="password",
                placeholder="Digite o código de acesso",
                help="Código fornecido pela empresa"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                verificar_button = st.form_submit_button("🔐 Verificar Código", use_container_width=True)
            
            with col2:
                if st.form_submit_button("🔄 Limpar", use_container_width=True):
                    st.rerun()
            
            if verificar_button:
                if codigo == "Easy2025":
                    st.session_state.codigo_verificado = True
                    st.success("✅ Código verificado! Agora você pode se cadastrar.")
                    st.rerun()
                else:
                    st.error("❌ Código incorreto! Tente novamente.")
    
    else:
        # Etapa 2: Formulário de cadastro
        st.success("✅ Código verificado! Preencha seus dados:")
        
        with st.form("register_form"):
            nome = st.text_input(
                "Nome Completo",
                placeholder="Seu nome completo"
            )
            
            cpf = st.text_input(
                "CPF",
                placeholder="000.000.000-00",
                help="Digite apenas números"
            )
            
            funcao = st.selectbox(
                "Função",
                ["Administrador", "Usuário", "Financeiro", "Contador", "Outro"]
            )
            
            empresa = st.text_input(
                "Empresa",
                placeholder="Nome da sua empresa"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                register_button = st.form_submit_button("📝 Cadastrar", use_container_width=True)
            
            with col2:
                if st.form_submit_button("🔄 Limpar", use_container_width=True):
                    st.rerun()
            
            if register_button:
                if all([nome, cpf, funcao, empresa]):
                    if auth.register(nome, cpf, funcao, empresa, "Easy2025"):
                        st.success("✅ Cadastro realizado com sucesso!")
                        st.info("💡 Agora você pode fazer login usando seu CPF como senha")
                        st.balloons()
                        st.session_state.codigo_verificado = False
                    else:
                        st.error("❌ Erro no cadastro! Verifique se o CPF já existe.")
                else:
                    st.warning("⚠️ Preencha todos os campos!")
        
        # Botão para voltar à verificação de código
        if st.button("🔙 Voltar à Verificação de Código"):
            st.session_state.codigo_verificado = False
            st.rerun()

# Fechar container esquerdo e abrir container direito
st.markdown("""
        </div>
    </div>
    <div class="right-panel">
        <div class="right-content">
            <h1 class="right-title">EasyNF</h1>
            <p class="right-subtitle">Sistema de Gestão para Obras</p>
            <p class="right-description">
                Controle completo de contas, parcelas e fornecedores para projetos de construção. 
                Gerencie suas finanças de forma eficiente e profissional.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)