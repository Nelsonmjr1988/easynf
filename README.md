# 🏗️ Sistema de Controle de Contas para Obras

Sistema completo desenvolvido em Python e Streamlit para controle de contas e parcelas em obras, com integração ao Supabase para persistência de dados.

## ✨ Funcionalidades

### 📝 Lançamento de Notas
- Cadastro completo de notas fiscais
- Campos: número da nota, fornecedor, valor total, data de emissão, descrição
- Gerenciamento de locais de aplicação (estoque/em uso)
- Sistema de notas parceladas com cálculo automático
- Validações de dados e cálculos automáticos

### 📋 Visualização de Notas
- Lista todas as notas com filtros avançados
- Filtros por fornecedor, status e local de aplicação
- Alteração de local de aplicação e status do material
- Detalhamento completo das parcelas
- Marcação de parcelas como pagas
- Atualização automática de status (vencidas/pendentes)

### 📊 Relatórios
- Relatório mensal completo de contas pagas e a pagar
- Filtros por mês/ano
- Gráficos comparativos e totais
- Análise por local de aplicação
- Exportação de dados em CSV e TXT
- Estatísticas detalhadas

### ⚙️ Configurações
- Gerenciamento de locais de aplicação
- Estatísticas do sistema
- Configurações avançadas
- Área de backup e restauração

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Conta no Supabase
- Git (opcional)

### Passos para Instalação

1. **Clone o repositório** (ou baixe os arquivos):
```bash
git clone <url-do-repositorio>
cd contas-a-pagar
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure o Supabase**:
   - Crie um projeto no [Supabase](https://supabase.com)
   - Copie a URL e a chave da API
   - Edite o arquivo `config.py` e substitua:
     ```python
     SUPABASE_URL = "sua_url_do_supabase"
     SUPABASE_KEY = "sua_chave_do_supabase"
     ```

4. **Crie as tabelas no Supabase**:
Execute os seguintes comandos SQL no editor SQL do Supabase:

```sql
-- Tabela de locais de aplicação
CREATE TABLE locais_aplicacao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de notas
CREATE TABLE notas (
    id SERIAL PRIMARY KEY,
    numero_nota VARCHAR(100) NOT NULL,
    fornecedor VARCHAR(255) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    data_emissao DATE NOT NULL,
    descricao TEXT,
    local_aplicacao INTEGER REFERENCES locais_aplicacao(id),
    status_material VARCHAR(20) NOT NULL,
    eh_parcelada BOOLEAN DEFAULT FALSE,
    num_parcelas INTEGER DEFAULT 1,
    dias_ate_primeira INTEGER DEFAULT 0,
    intervalo_dias INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de parcelas
CREATE TABLE parcelas (
    id SERIAL PRIMARY KEY,
    nota_id INTEGER REFERENCES notas(id) ON DELETE CASCADE,
    numero INTEGER NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_vencimento DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDENTE',
    data_pagamento DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX idx_parcelas_nota_id ON parcelas(nota_id);
CREATE INDEX idx_parcelas_status ON parcelas(status);
CREATE INDEX idx_parcelas_vencimento ON parcelas(data_vencimento);
CREATE INDEX idx_notas_fornecedor ON notas(fornecedor);
CREATE INDEX idx_notas_local ON notas(local_aplicacao);
```

5. **Execute o sistema**:
```bash
streamlit run app.py
```

6. **Acesse no navegador**:
   - O sistema abrirá automaticamente em `http://localhost:8501`
   - Se não abrir automaticamente, acesse manualmente

## 📁 Estrutura do Projeto

```
contas-a-pagar/
├── app.py                  # Arquivo principal
├── config.py              # Configurações do Supabase
├── database.py            # Gerenciamento do banco de dados
├── utils.py               # Funções utilitárias
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
└── pages/                # Páginas do Streamlit
    ├── 01_📝_Lançar_Nota.py
    ├── 02_📋_Visualizar_Notas.py
    ├── 03_📊_Relatórios.py
    └── 04_⚙️_Configurações.py
```

## 🎯 Como Usar

### 1. Primeiro Acesso
1. Acesse a página **Configurações**
2. Adicione os locais de aplicação (ex: "Obra Centro", "Obra Norte")
3. Volte ao **Dashboard** para começar

### 2. Lançar uma Nota
1. Vá para **Lançar Nota**
2. Preencha todos os campos obrigatórios
3. Configure as parcelas se necessário
4. Clique em **Salvar Nota**

### 3. Visualizar Notas
1. Acesse **Visualizar Notas**
2. Use os filtros para encontrar notas específicas
3. Altere locais e status conforme necessário
4. Marque parcelas como pagas

### 4. Gerar Relatórios
1. Vá para **Relatórios**
2. Selecione o mês/ano desejado
3. Visualize gráficos e estatísticas
4. Exporte os dados se necessário

## 🔧 Configurações Avançadas

### Variáveis de Ambiente
Para maior segurança, você pode usar variáveis de ambiente:

```bash
export SUPABASE_URL="sua_url_do_supabase"
export SUPABASE_KEY="sua_chave_do_supabase"
```

### Personalização
- Edite `config.py` para alterar configurações gerais
- Modifique `utils.py` para ajustar validações e cálculos
- Customize os estilos CSS no `pages/00_🏠_Dashboard.py`

## 📊 Estrutura do Banco de Dados

### Tabela `notas`
- `id`: Chave primária
- `numero_nota`: Número da nota fiscal
- `fornecedor`: Nome do fornecedor
- `valor_total`: Valor total da nota
- `data_emissao`: Data de emissão
- `descricao`: Descrição dos materiais/serviços
- `local_aplicacao`: ID do local de aplicação
- `status_material`: Estoque ou Em Uso
- `eh_parcelada`: Se a nota é parcelada
- `num_parcelas`: Número de parcelas
- `dias_ate_primeira`: Dias até a primeira parcela
- `intervalo_dias`: Intervalo entre parcelas

### Tabela `parcelas`
- `id`: Chave primária
- `nota_id`: ID da nota (chave estrangeira)
- `numero`: Número da parcela
- `valor`: Valor da parcela
- `data_vencimento`: Data de vencimento
- `status`: PENDENTE, PAGA, VENCIDA
- `data_pagamento`: Data do pagamento (se paga)

### Tabela `locais_aplicacao`
- `id`: Chave primária
- `nome`: Nome do local

## 🐛 Solução de Problemas

### Erro de Conexão com Supabase
- Verifique se a URL e chave estão corretas
- Confirme se o projeto Supabase está ativo
- Verifique se as tabelas foram criadas corretamente

### Erro de Dependências
```bash
pip install --upgrade -r requirements.txt
```

### Problemas de Performance
- Verifique se os índices foram criados no Supabase
- Considere limitar o número de registros exibidos

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔐 Sistema de Autenticação

### **Primeiro Acesso:**
1. Acesse a aplicação
2. Vá para a aba "Cadastro"
3. Digite o código: `Easy2025`
4. Preencha seus dados
5. Faça login com seu CPF

### **Usuários:**
- **Login**: CPF como usuário e senha
- **Código de Cadastro**: `Easy2025`
- **Controle de Acesso**: Apenas usuários autenticados
- **Logs**: Todas as ações são registradas

### **Executar Aplicação:**
```bash
streamlit run app.py
```

**⚠️ Importante:** Use `app.py` como arquivo principal; o dashboard está em `pages/00_🏠_Dashboard.py`

## 📞 Suporte

Para suporte técnico ou dúvidas:
- 📧 Email: suporte@contasobras.com
- 📱 Telefone: (11) 99999-9999
- 🌐 Website: www.contasobras.com

## 🎉 Agradecimentos

- [Streamlit](https://streamlit.io) - Framework web
- [Supabase](https://supabase.com) - Backend como serviço
- [Plotly](https://plotly.com) - Gráficos interativos
- [Pandas](https://pandas.pydata.org) - Manipulação de dados

---

**Desenvolvido com ❤️ para facilitar o controle financeiro de obras**