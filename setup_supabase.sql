-- Script SQL para configurar o banco de dados no Supabase
-- Execute este script no editor SQL do Supabase

-- Tabela de locais de aplicação
CREATE TABLE IF NOT EXISTS locais_aplicacao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de notas
CREATE TABLE IF NOT EXISTS notas (
    id SERIAL PRIMARY KEY,
    numero_nota VARCHAR(100) NOT NULL,
    fornecedor VARCHAR(255) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    data_emissao DATE NOT NULL,
    descricao TEXT,
    local_aplicacao INTEGER REFERENCES locais_aplicacao(id),
    status_material VARCHAR(20) NOT NULL CHECK (status_material IN ('ESTOQUE', 'EM_USO')),
    eh_parcelada BOOLEAN DEFAULT FALSE,
    num_parcelas INTEGER DEFAULT 1 CHECK (num_parcelas > 0 AND num_parcelas <= 24),
    dias_ate_primeira INTEGER DEFAULT 0 CHECK (dias_ate_primeira >= 0),
    intervalo_dias INTEGER DEFAULT 30 CHECK (intervalo_dias > 0),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de parcelas
CREATE TABLE IF NOT EXISTS parcelas (
    id SERIAL PRIMARY KEY,
    nota_id INTEGER REFERENCES notas(id) ON DELETE CASCADE,
    numero INTEGER NOT NULL CHECK (numero > 0),
    valor DECIMAL(10,2) NOT NULL CHECK (valor > 0),
    data_vencimento DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'PAGA', 'VENCIDA')),
    data_pagamento DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_parcelas_nota_id ON parcelas(nota_id);
CREATE INDEX IF NOT EXISTS idx_parcelas_status ON parcelas(status);
CREATE INDEX IF NOT EXISTS idx_parcelas_vencimento ON parcelas(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_notas_fornecedor ON notas(fornecedor);
CREATE INDEX IF NOT EXISTS idx_notas_local ON notas(local_aplicacao);
CREATE INDEX IF NOT EXISTS idx_notas_data_emissao ON notas(data_emissao);

-- Inserir alguns locais de exemplo
INSERT INTO locais_aplicacao (nome) VALUES 
    ('Obra Centro'),
    ('Obra Norte'),
    ('Obra Sul'),
    ('Estoque Central'),
    ('Depósito Principal')
ON CONFLICT (nome) DO NOTHING;

-- Função para atualizar status de parcelas vencidas
CREATE OR REPLACE FUNCTION atualizar_status_parcelas_vencidas()
RETURNS void AS $$
BEGIN
    UPDATE parcelas 
    SET status = 'VENCIDA' 
    WHERE status = 'PENDENTE' 
    AND data_vencimento < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar status automaticamente (opcional)
-- CREATE OR REPLACE FUNCTION trigger_atualizar_status()
-- RETURNS trigger AS $$
-- BEGIN
--     PERFORM atualizar_status_parcelas_vencidas();
--     RETURN NULL;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER trigger_atualizar_status_parcelas
--     AFTER INSERT OR UPDATE ON parcelas
--     FOR EACH STATEMENT
--     EXECUTE FUNCTION trigger_atualizar_status();

-- Comentários nas tabelas
COMMENT ON TABLE locais_aplicacao IS 'Locais onde os materiais são aplicados ou armazenados';
COMMENT ON TABLE notas IS 'Notas fiscais das obras';
COMMENT ON TABLE parcelas IS 'Parcelas das notas fiscais';

COMMENT ON COLUMN notas.status_material IS 'Situação do material: ESTOQUE ou EM_USO';
COMMENT ON COLUMN parcelas.status IS 'Status da parcela: PENDENTE, PAGA ou VENCIDA';

-- Políticas de segurança (RLS) - descomente se necessário
-- ALTER TABLE locais_aplicacao ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE notas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE parcelas ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Permitir todas as operações para usuários autenticados" ON locais_aplicacao
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Permitir todas as operações para usuários autenticados" ON notas
--     FOR ALL USING (auth.role() = 'authenticated');

-- CREATE POLICY "Permitir todas as operações para usuários autenticados" ON parcelas
--     FOR ALL USING (auth.role() = 'authenticated');