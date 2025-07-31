#!/usr/bin/env python3
"""
Script para inserir dados de teste na tabela tenant
Execute este script quando o banco de dados estiver disponível
"""

import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório da API ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps', 'api'))

def get_database_url():
    """Obtém a URL do banco de dados das variáveis de ambiente"""
    # Tenta diferentes configurações
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Configuração padrão para desenvolvimento
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        db = os.getenv("POSTGRES_DB", "totem")
        
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    return database_url

def insert_tenant_data():
    """Insere dados de teste na tabela tenant"""
    
    try:
        # Conecta ao banco
        database_url = get_database_url()
        print(f"🔗 Conectando ao banco: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        engine = create_engine(database_url)
        
        # Testa a conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print(f"✅ Conexão estabelecida com PostgreSQL: {result.fetchone()[0]}")
        
        # Cria sessão
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Dados dos tenants para inserir
        tenants_data = [
            {
                "name": "RecoveryTruck Premium",
                "cnpj": "12345678000199",
                "is_active": True
            },
            {
                "name": "RecoveryTruck Basic", 
                "cnpj": "98765432000188",
                "is_active": True
            },
            {
                "name": "RecoveryTruck Dev",
                "cnpj": "11111111000111", 
                "is_active": True
            }
        ]
        
        print("\n📝 Inserindo dados na tabela tenant...")
        
        for tenant_data in tenants_data:
            # Verifica se já existe
            existing = db.execute(
                text("SELECT id FROM tenants WHERE cnpj = :cnpj"),
                {"cnpj": tenant_data["cnpj"]}
            ).fetchone()
            
            if existing:
                print(f"⚠️  Tenant {tenant_data['name']} já existe (CNPJ: {tenant_data['cnpj']})")
                continue
            
            # Insere novo tenant
            tenant_id = str(uuid.uuid4())
            now = datetime.now()
            
            db.execute(
                text("""
                    INSERT INTO tenants (id, name, cnpj, is_active, created_at, updated_at)
                    VALUES (:id, :name, :cnpj, :is_active, :created_at, :updated_at)
                """),
                {
                    "id": tenant_id,
                    "name": tenant_data["name"],
                    "cnpj": tenant_data["cnpj"],
                    "is_active": tenant_data["is_active"],
                    "created_at": now,
                    "updated_at": now
                }
            )
            
            print(f"✅ Tenant inserido: {tenant_data['name']} (ID: {tenant_id})")
        
        # Commit das alterações
        db.commit()
        
        # Verifica os dados inseridos
        print("\n📊 Verificando dados inseridos:")
        result = db.execute(text("SELECT id, name, cnpj, is_active FROM tenants ORDER BY created_at"))
        tenants = result.fetchall()
        
        for tenant in tenants:
            print(f"  - {tenant[1]} (CNPJ: {tenant[2]}, Ativo: {tenant[3]})")
        
        print(f"\n🎉 Total de tenants: {len(tenants)}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {str(e)}")
        print("\n💡 Verifique se:")
        print("  1. O banco de dados PostgreSQL está rodando")
        print("  2. As variáveis de ambiente estão configuradas")
        print("  3. A tabela 'tenants' existe (execute as migrações primeiro)")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Script de inserção de dados de teste - Tabela Tenant")
    print("=" * 60)
    
    success = insert_tenant_data()
    
    if success:
        print("\n✅ Script executado com sucesso!")
        print("\n📋 Próximos passos:")
        print("  1. Execute as migrações se ainda não fez: alembic upgrade head")
        print("  2. Inicie a API: uvicorn apps.api.app:app --reload")
        print("  3. Teste a aplicação com os tenants criados")
    else:
        print("\n❌ Script falhou. Verifique os erros acima.")
        sys.exit(1) 