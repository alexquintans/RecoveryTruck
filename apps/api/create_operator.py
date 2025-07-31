#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from database import SessionLocal
from models import Operator, Tenant
from security import get_password_hash
import uuid
from datetime import datetime
import argparse

def main():
    db = SessionLocal()
    try:
        # Buscar o tenant
        tenant = db.query(Tenant).filter(Tenant.name == 'Empresa Exemplo').first()
        if not tenant:
            print("❌ Tenant 'Empresa Exemplo' não encontrado")
            return
        
        # Verificar se operador já existe
        existing = db.query(Operator).filter(Operator.email == 'admin@exemplo.com').first()
        if existing:
            print("🗑️ Removendo operador existente...")
            db.delete(existing)
            db.commit()
        
        # Gerar hash da senha
        password_hash = get_password_hash('123456')
        print(f"🔐 Hash gerado: {password_hash}")
        
        # Criar novo operador
        operator = Operator(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            name='Admin Sistema',
            email='admin@exemplo.com',
            password_hash=password_hash,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(operator)
        db.commit()
        db.refresh(operator)
        
        print(f"✅ Operador criado com sucesso!")
        print(f"   📧 Email: {operator.email}")
        print(f"   👤 Nome: {operator.name}")
        print(f"   🔑 Senha: 123456")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerencia operadores no sistema.")
    parser.add_argument(
        '--generate-hash', 
        nargs='?', 
        const='123456', 
        default=None,
        help="Gera um hash para a senha fornecida (padrão: '123456') e sai."
    )
    
    args = parser.parse_args()

    if args.generate_hash:
        password_to_hash = args.generate_hash
        password_hash = get_password_hash(password_to_hash)
        print(f"🔐 Hash gerado para '{password_to_hash}': {password_hash}")
    else:
    main() 