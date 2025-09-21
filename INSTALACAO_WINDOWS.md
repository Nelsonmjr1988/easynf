# 🪟 Instalação no Windows - Sistema de Contas para Obras

## 📋 Pré-requisitos

### 1. Instalar Python

1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente do Python (3.8 ou superior)
3. **IMPORTANTE**: Durante a instalação, marque a opção **"Add Python to PATH"**
4. Complete a instalação

### 2. Verificar Instalação

Abra o **Prompt de Comando** (cmd) ou **PowerShell** e digite:

```cmd
python --version
pip --version
```

Se ambos comandos funcionarem, o Python está instalado corretamente.

## 🚀 Instalação do Sistema

### 1. Navegue até a pasta do projeto

```cmd
cd "C:\Users\nelson\Desktop\ProjetoVsCode\contas a pagar"
```

### 2. Instale as dependências

```cmd
python -m pip install -r requirements.txt
```

### 3. Execute o sistema

```cmd
streamlit run app.py
```

## 🔧 Configuração do Supabase

### 1. Acesse o Supabase

Vá para: https://zawlchxaqakrbhbipxvg.supabase.co

### 2. Configure o Banco de Dados

1. Faça login no Supabase
2. Vá para **SQL Editor** no menu lateral
3. Copie todo o conteúdo do arquivo `setup_supabase.sql`
4. Cole no editor SQL
5. Clique em **Run** para executar

### 3. Verifique as Tabelas

Após executar o script, você deve ver 3 tabelas criadas:
- `locais_aplicacao`
- `notas` 
- `parcelas`

## 🎯 Primeiro Uso

1. **Execute o sistema**: `streamlit run app.py`
2. **Acesse**: http://localhost:8501
3. **Configure locais**: Vá em Configurações → Adicione locais de aplicação
4. **Lance uma nota**: Vá em Lançar Nota → Cadastre sua primeira nota
5. **Visualize**: Vá em Visualizar Notas para gerenciar

## ❗ Solução de Problemas

### Erro: "Python não foi encontrado"
- Reinstale o Python marcando "Add Python to PATH"
- Ou use o Python do Microsoft Store

### Erro: "pip não foi encontrado"
- Use: `python -m pip install -r requirements.txt`

### Erro de conexão com Supabase
- Verifique se o script SQL foi executado
- Confirme se as credenciais estão corretas no `config.py`

### Porta 8501 ocupada
- Feche outros programas que usam a porta 8501
- Ou use: `streamlit run app.py --server.port 8502`

## 📞 Suporte

Se ainda tiver problemas:
1. Verifique se o Python está instalado corretamente
2. Confirme se todas as dependências foram instaladas
3. Verifique se o banco de dados foi configurado no Supabase

## ✅ Verificação Final

Para confirmar que tudo está funcionando:

1. ✅ Python instalado e no PATH
2. ✅ Dependências instaladas
3. ✅ Supabase configurado
4. ✅ Sistema executando em http://localhost:8501
5. ✅ Pode acessar todas as páginas do sistema

**🎉 Pronto! Seu sistema está funcionando!**