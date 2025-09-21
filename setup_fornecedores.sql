-- Criar tabela de fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    vendedor VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índice para busca rápida por CNPJ
CREATE INDEX IF NOT EXISTS idx_fornecedores_cnpj ON fornecedores(cnpj);

-- Criar índice para busca rápida por nome
CREATE INDEX IF NOT EXISTS idx_fornecedores_nome ON fornecedores(nome);

-- Comentários na tabela
COMMENT ON TABLE fornecedores IS 'Tabela para armazenar dados dos fornecedores';
COMMENT ON COLUMN fornecedores.id IS 'ID único do fornecedor';
COMMENT ON COLUMN fornecedores.nome IS 'Nome da empresa fornecedora';
COMMENT ON COLUMN fornecedores.cnpj IS 'CNPJ da empresa (único)';
COMMENT ON COLUMN fornecedores.telefone IS 'Telefone de contato';
COMMENT ON COLUMN fornecedores.vendedor IS 'Nome do vendedor responsável (opcional)';
COMMENT ON COLUMN fornecedores.created_at IS 'Data de criação do registro';
COMMENT ON COLUMN fornecedores.updated_at IS 'Data da última atualização';

-- Inserir alguns fornecedores de exemplo
INSERT INTO fornecedores (nome, cnpj, telefone, vendedor) VALUES
('Empresa ABC Ltda', '12.345.678/0001-90', '(11) 99999-9999', 'João Silva'),
('Comércio XYZ S.A.', '98.765.432/0001-10', '(11) 88888-8888', 'Maria Santos'),
('Indústria DEF Ltda', '11.222.333/0001-44', '(11) 77777-7777', 'Pedro Costa')
ON CONFLICT (cnpj) DO NOTHING;