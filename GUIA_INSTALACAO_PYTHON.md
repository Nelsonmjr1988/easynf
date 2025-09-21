# 🐍 Guia Completo - Instalação do Python no Windows

## 📥 Passo 1: Baixar o Python

1. **Acesse o site oficial**: https://www.python.org/downloads/
2. **Clique em "Download Python 3.x.x"** (versão mais recente)
3. Aguarde o download terminar

## 🔧 Passo 2: Instalar o Python

### ⚠️ ATENÇÃO: Configurações Importantes!

1. **Execute o arquivo baixado** (python-3.x.x-amd64.exe)
2. **IMPORTANTE**: Marque a caixa **"Add Python to PATH"** ✅
3. **Clique em "Install Now"**
4. Aguarde a instalação terminar
5. **Clique em "Close"**

## ✅ Passo 3: Verificar se Funcionou

1. **Abra o Prompt de Comando**:
   - Pressione `Windows + R`
   - Digite `cmd`
   - Pressione Enter

2. **Teste o Python**:
   ```cmd
   python --version
   ```
   Deve aparecer algo como: `Python 3.11.x`

3. **Teste o pip**:
   ```cmd
   pip --version
   ```
   Deve aparecer algo como: `pip 23.x.x`

## 🚀 Passo 4: Instalar o Sistema

Agora que o Python está instalado, execute:

```cmd
cd "C:\Users\nelson\Desktop\ProjetoVsCode\contas a pagar"
python -m pip install -r requirements.txt
streamlit run app.py
```

## ❗ Solução de Problemas

### Se "python" não for reconhecido:
1. Reinicie o computador
2. Ou reinstale o Python marcando "Add Python to PATH"

### Se "pip" não for reconhecido:
1. Use: `python -m pip install -r requirements.txt`
2. Ou reinstale o Python

### Se der erro de permissão:
1. Execute o Prompt de Comando como Administrador
2. Ou use: `python -m pip install --user -r requirements.txt`

## 🎯 Alternativa: Microsoft Store

Se preferir, você pode instalar pelo Microsoft Store:

1. Abra a **Microsoft Store**
2. Pesquise por **"Python"**
3. Instale o **"Python 3.11"** (ou versão mais recente)
4. Após instalar, teste no Prompt de Comando

## ✅ Verificação Final

Para confirmar que tudo está funcionando:

1. ✅ `python --version` funciona
2. ✅ `pip --version` funciona  
3. ✅ Consegue instalar as dependências
4. ✅ Consegue executar o sistema

## 📞 Precisa de Ajuda?

Se tiver algum problema:
1. Tire print da tela do erro
2. Verifique se marcou "Add Python to PATH"
3. Tente reinstalar o Python
4. Reinicie o computador após instalar

**🎉 Depois de instalar o Python, seu sistema estará pronto para usar!**