#!/usr/bin/env python3
"""
Script de teste para verificar a conexão com o Supabase
"""

from database import DatabaseManager
from config import supabase

def testar_conexao():
    print("🔍 Testando conexão com Supabase...")
    
    try:
        # Testar conexão básica
        result = supabase.table('locais_aplicacao').select('*').limit(1).execute()
        print("✅ Conexão com Supabase funcionando!")
        print(f"Debug: Resultado do teste: {result}")
        
        # Testar criação de local
        db = DatabaseManager()
        print("\n🔍 Testando criação de local...")
        
        resultado = db.create_local_aplicacao("Teste Local")
        if resultado:
            print("✅ Local de teste criado com sucesso!")
            print(f"Debug: ID do local criado: {resultado['id']}")
        else:
            print("❌ Erro ao criar local de teste")
            
        # Testar criação de parcelas
        print("\n🔍 Testando criação de parcelas...")
        
        parcelas_teste = [
            {
                'nota_id': 1,  # ID fictício para teste
                'numero': 1,
                'valor': 500.00,
                'data_vencimento': '2024-02-01',
                'status': 'PENDENTE'
            },
            {
                'nota_id': 1,
                'numero': 2,
                'valor': 500.00,
                'data_vencimento': '2024-02-15',
                'status': 'PENDENTE'
            }
        ]
        
        parcelas_criadas = db.create_parcelas(parcelas_teste)
        if parcelas_criadas:
            print(f"✅ {len(parcelas_criadas)} parcelas de teste criadas!")
        else:
            print("❌ Erro ao criar parcelas de teste")
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print(f"Debug: Tipo do erro: {type(e)}")

if __name__ == "__main__":
    testar_conexao()