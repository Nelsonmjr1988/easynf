-- Tabela de usuários
CREATE TABLE IF NOT EXISTS public.usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    funcao VARCHAR(100) NOT NULL,
    empresa VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Tabela de logs do sistema
CREATE TABLE IF NOT EXISTS public.logs_sistema (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    acao VARCHAR(100) NOT NULL,
    tabela_afetada VARCHAR(50),
    registro_id INTEGER,
    dados_anteriores JSONB,
    dados_novos JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_usuarios_cpf ON public.usuarios(cpf);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON public.usuarios(ativo);
CREATE INDEX IF NOT EXISTS idx_logs_usuario ON public.logs_sistema(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_acao ON public.logs_sistema(acao);
CREATE INDEX IF NOT EXISTS idx_logs_data ON public.logs_sistema(created_at);

-- Inserir usuário administrador padrão
INSERT INTO public.usuarios (nome, cpf, funcao, empresa) 
VALUES ('Administrador', '000.000.000-00', 'Administrador', 'Sistema')
ON CONFLICT (cpf) DO NOTHING;
