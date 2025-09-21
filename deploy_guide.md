# 🚀 Guia de Deploy - Sistema de Contas a Pagar

## 📋 Pré-requisitos

### 1. Banco de Dados (Supabase)
Execute o script SQL no Supabase:
```sql
-- Execute o arquivo setup_usuarios.sql no Supabase
```

### 2. Variáveis de Ambiente
Configure as seguintes variáveis no seu provedor de deploy:

```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

## 🌐 Opções de Deploy

### Opção 1: Streamlit Cloud (RECOMENDADO)

1. **Fork do Repositório**
   - Faça fork do repositório no GitHub
   - Ou crie um novo repositório com o código

2. **Configurar Streamlit Cloud**
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Conecte sua conta GitHub
   - Selecione o repositório
   - Configure as variáveis de ambiente

3. **Deploy**
   - Clique em "Deploy"
   - Aguarde o processo de build
   - Acesse sua aplicação

### Opção 2: Railway

1. **Criar Conta**
   - Acesse [railway.app](https://railway.app)
   - Crie uma conta

2. **Deploy**
   - Conecte com GitHub
   - Selecione o repositório
   - Configure as variáveis de ambiente
   - Deploy automático

### Opção 3: Heroku

1. **Instalar Heroku CLI**
   ```bash
   # Windows
   winget install Heroku.HerokuCLI
   
   # Ou baixe do site oficial
   ```

2. **Configurar Heroku**
   ```bash
   heroku login
   heroku create nome-do-seu-app
   ```

3. **Criar Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy inicial"
   git push heroku main
   ```

### Opção 4: VPS (Seu Domínio Hostinger)

1. **Configurar VPS**
   ```bash
   # Conectar via SSH
   ssh root@seu-ip
   
   # Atualizar sistema
   apt update && apt upgrade -y
   
   # Instalar Python
   apt install python3 python3-pip python3-venv -y
   
   # Instalar Git
   apt install git -y
   ```

2. **Clonar Repositório**
   ```bash
   git clone https://github.com/seu-usuario/contas-a-pagar.git
   cd contas-a-pagar
   ```

3. **Configurar Ambiente**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configurar Nginx**
   ```bash
   apt install nginx -y
   
   # Criar arquivo de configuração
   nano /etc/nginx/sites-available/contas-a-pagar
   ```

   Conteúdo do arquivo:
   ```nginx
   server {
       listen 80;
       server_name seu-dominio.com.br;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Ativar Site**
   ```bash
   ln -s /etc/nginx/sites-available/contas-a-pagar /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

6. **Configurar SSL**
   ```bash
   apt install certbot python3-certbot-nginx -y
   certbot --nginx -d seu-dominio.com.br
   ```

7. **Configurar Serviço**
   ```bash
   nano /etc/systemd/system/contas-a-pagar.service
   ```

   Conteúdo:
   ```ini
   [Unit]
   Description=Contas a Pagar Streamlit App
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/contas-a-pagar
   Environment=PATH=/root/contas-a-pagar/venv/bin
   ExecStart=/root/contas-a-pagar/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

8. **Iniciar Serviço**
   ```bash
   systemctl daemon-reload
   systemctl enable contas-a-pagar
   systemctl start contas-a-pagar
   ```

## 🔧 Configurações Pós-Deploy

### 1. Primeiro Acesso
- Acesse a aplicação
- Use o código "Easy2025" para criar o primeiro usuário
- Faça login com o CPF cadastrado

### 2. Configurar Domínio (VPS)
- Aponte o DNS do seu domínio para o IP do VPS
- Configure os registros A e CNAME

### 3. Backup
- Configure backup automático do banco de dados
- Faça backup regular dos arquivos de configuração

## 📊 Monitoramento

### 1. Logs do Sistema
- Acesse a página "Logs do Sistema" (apenas administradores)
- Monitore atividades dos usuários
- Verifique erros e acessos

### 2. Performance
- Monitore uso de CPU e memória
- Configure alertas de downtime
- Otimize conforme necessário

## 🔒 Segurança

### 1. HTTPS
- Sempre use HTTPS em produção
- Configure certificados SSL válidos

### 2. Backup
- Faça backup regular dos dados
- Teste restauração periodicamente

### 3. Atualizações
- Mantenha dependências atualizadas
- Monitore vulnerabilidades

## 🆘 Suporte

### Problemas Comuns

1. **Erro de Conexão com Banco**
   - Verifique variáveis de ambiente
   - Confirme credenciais do Supabase

2. **Erro de Porta**
   - Verifique se a porta 8501 está liberada
   - Configure firewall se necessário

3. **Erro de Dependências**
   - Verifique requirements.txt
   - Reinstale dependências

### Contato
- Documentação: README.md
- Issues: GitHub Issues
- Suporte: [Seu Email]

---

## ✅ Checklist de Deploy

- [ ] Banco de dados configurado
- [ ] Variáveis de ambiente definidas
- [ ] Código no repositório
- [ ] Deploy realizado
- [ ] Primeiro usuário criado
- [ ] Testes realizados
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Documentação atualizada

**🎉 Deploy Concluído com Sucesso!**
