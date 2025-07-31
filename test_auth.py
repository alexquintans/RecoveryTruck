#!/usr/bin/env python3
"""
Script para testar autenticação e identificar problemas
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Adiciona o diretório da API ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps', 'api'))

def get_database_url():
    """Obtém a URL do banco de dados"""
    # Para Docker, usar a configuração do container
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Configuração para Docker
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5433")  # Porta do Docker
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        db = os.getenv("POSTGRES_DB", "totem")
        
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    return database_url

def test_authentication():
    """Testa a autenticação do operador"""
    
    try:
        # Conecta ao banco
        database_url = get_database_url()
        print(f"🔗 Conectando ao banco: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 1. Verificar se o operador existe
        print("\n📋 Verificando operador no banco...")
        result = db.execute(text("""
            SELECT id, name, email, password_hash, is_active, tenant_id 
            FROM operators 
            WHERE email = 'operador@recoverytruck.dev'
        """))
        operator = result.fetchone()
        
        if not operator:
            print("❌ Operador não encontrado!")
            return False
        
        print(f"✅ Operador encontrado:")
        print(f"   ID: {operator[0]}")
        print(f"   Nome: {operator[1]}")
        print(f"   Email: {operator[2]}")
        print(f"   Hash: {operator[3][:50]}...")
        print(f"   Ativo: {operator[4]}")
        print(f"   Tenant ID: {operator[5]}")
        
        # 2. Testar verificação de senha
        print("\n🔐 Testando verificação de senha...")
        
        # Configurar bcrypt
        pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=12
        )
        
        # Senha que queremos testar
        test_password = "123456"
        stored_hash = operator[3]
        
        print(f"   Senha de teste: {test_password}")
        print(f"   Hash armazenado: {stored_hash}")
        
        # Testar verificação
        try:
            is_valid = pwd_context.verify(test_password, stored_hash)
            print(f"   ✅ Verificação bem-sucedida: {is_valid}")
            
            if is_valid:
                print("   🎉 Senha está correta!")
            else:
                print("   ❌ Senha está incorreta!")
                
        except Exception as e:
            print(f"   ❌ Erro na verificação: {str(e)}")
            return False
        
        # 3. Testar geração de novo hash
        print("\n🔄 Testando geração de novo hash...")
        try:
            new_hash = pwd_context.hash(test_password)
            print(f"   Novo hash gerado: {new_hash}")
            
            # Verificar se o novo hash funciona
            is_valid_new = pwd_context.verify(test_password, new_hash)
            print(f"   ✅ Novo hash funciona: {is_valid_new}")
            
        except Exception as e:
            print(f"   ❌ Erro ao gerar novo hash: {str(e)}")
        
        # 4. Verificar tenant
        print("\n🏢 Verificando tenant...")
        tenant_result = db.execute(text("""
            SELECT id, name, cnpj, is_active 
            FROM tenants 
            WHERE id = :tenant_id
        """), {"tenant_id": operator[5]})
        tenant = tenant_result.fetchone()
        
        if tenant:
            print(f"   ✅ Tenant encontrado: {tenant[1]} ({tenant[2]})")
        else:
            print(f"   ❌ Tenant não encontrado para ID: {operator[5]}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Teste de Autenticação - Sistema Totem")
    print("=" * 50)
    
    success = test_authentication()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou!")
        sys.exit(1) 