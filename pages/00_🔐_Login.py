import streamlit as st
from auth import AuthManager

# Config da página
st.set_page_config(
    page_title="EasyNF - Login",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado
st.markdown("""
<style>
    /* Esconde header/menubar e sidebar (forma segura) */
    header, [data-testid="stToolbar"], #MainMenu, footer {visibility: hidden;}
    [data-testid="stSidebar"] { display: none !important; }
    .block-container {padding: 0; margin: 0;}
    
    /* Reset geral */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: white;
    }

    .logo {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 30px;
        color: #2d3748;
    }

    .stTextInput input {
        border-radius: 8px;
        padding: 10px 14px;
        border: 1px solid #ddd;
    }

    .stTextInput input:focus {
        border: 1px solid #4a3aff;
        box-shadow: 0 0 0 2px rgba(74,58,255,0.1);
    }

    .stButton>button {
        width: 100%;
        background: #4a3aff;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 12px;
    }

    .stButton>button:hover {
        background: #3a2fe0;
    }

    .forgot {
        text-align: center;
        margin-top: 10px;
        font-size: 14px;
        color: #999;
        cursor: pointer;
    }
    
    /* Responsividade */
    @media (max-width: 1000px) {
        .stImage {
            display: none;
        }
    }

</style>
""", unsafe_allow_html=True)

# Auth
auth = AuthManager()

# Estado da aplicação
if 'login_tab' not in st.session_state:
    st.session_state.login_tab = 'login'

# Layout 2 colunas
col1, col2 = st.columns([2,3])

with col1:
    st.markdown("<div class='logo'>EasyNF</div>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
        st.markdown("**Let's get started by filling out the form below.**")
        
        with st.form("login_form"):
            email_login = st.text_input("Email", placeholder="email@exemplo.com")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit_login = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit_login:
                if auth.login(email_login, password):
                    st.success("Login realizado com sucesso!")
                    st.switch_page("pages/00_🏠_Dashboard.py")
                else:
                    st.error("Email ou senha incorretos!")
        
        st.markdown("<div class='forgot'>Esqueceu a senha?</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("**Crie sua conta para acessar o sistema.**")
        
        # Campo para código de acesso
        codigo_acesso = st.text_input("Código de Acesso", placeholder="Digite o código de acesso", type="password")
        
        if codigo_acesso == "Easy2025":
            with st.form("register_form"):
                nome = st.text_input("Nome Completo", placeholder="Digite seu nome completo")
                email_cadastro = st.text_input("Email", placeholder="email@exemplo.com")
                cpf = st.text_input("CPF", placeholder="000.000.000-00")
                funcao = st.text_input("Função", placeholder="Digite sua função")
                empresa = st.text_input("Empresa", placeholder="Digite o nome da empresa")
                senha = st.text_input("Senha", type="password", placeholder="Digite uma senha")
                confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Confirme sua senha")
                submit_register = st.form_submit_button("Cadastrar", use_container_width=True)
                
                if submit_register:
                    if senha == confirmar_senha:
                        if auth.register(nome, cpf, email_cadastro, funcao, empresa, codigo_acesso, senha):
                            st.success("Cadastro realizado com sucesso! Redirecionando...")
                            st.switch_page("pages/00_🏠_Dashboard.py")
                        else:
                            st.error("Erro ao cadastrar. Verifique os dados e tente novamente.")
                    else:
                        st.error("As senhas não coincidem!")
        else:
            st.warning("Digite o código de acesso correto para continuar com o cadastro.")
            if codigo_acesso:
                st.error("Código de acesso incorreto!")

with col2:
    st.image("https://img.freepik.com/fotos-premium/guindastes-pontilham-o-canteiro-de-obras-contribuindo-para-o-processo-de-construcao-vertical-mobile-wallpaper_896558-11337.jpg?w=360", use_container_width=True)
