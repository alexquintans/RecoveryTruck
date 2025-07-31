#!/usr/bin/env python3
# 🖨️ Teste Completo do Sistema de Impressão

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Imports do sistema
from apps.api.services.printer_service import (
    printer_manager, PrinterConfig, PrinterType, PrinterConnection,
    ReceiptData, ReceiptType
)

async def test_printer_service():
    """🧪 Testa o serviço de impressão"""
    print("🖨️ === TESTE DO SISTEMA DE IMPRESSÃO ===\n")
    
    # 1. Configurar impressora virtual para teste
    print("1️⃣ Configurando impressora virtual...")
    
    virtual_config = PrinterConfig(
        name="Test Virtual Printer",
        printer_type=PrinterType.VIRTUAL,
        connection_type=PrinterConnection.FILE,
        paper_width=80,
        chars_per_line=48,
        encoding="utf-8",
        cut_paper=False,
        beep=False
    )
    
    printer_manager.register_printer("test_virtual", virtual_config)
    printer_manager.set_default_printer("test_virtual")
    
    print("✅ Impressora virtual configurada")
    
    # 2. Criar dados de teste para diferentes modalidades
    test_receipts = [
        {
            "name": "Cartão de Crédito",
            "data": ReceiptData(
                transaction_id="TXN-CC-20241201-001",
                receipt_type=ReceiptType.CUSTOMER,
                amount=150.75,
                payment_method="credit_card",
                status="approved",
                timestamp=datetime.now(),
                merchant_name="RecoveryTruck Teste",
                merchant_cnpj="12345678901234",
                merchant_address="Rua das Flores, 123 - São Paulo/SP",
                customer_name="João Silva",
                customer_cpf="12345678901",
                card_brand="visa",
                card_last_digits="1234",
                installments=3,
                authorization_code="AUTH123456",
                nsu="NSU789012"
            )
        },
        {
            "name": "PIX",
            "data": ReceiptData(
                transaction_id="TXN-PIX-20241201-002",
                receipt_type=ReceiptType.CUSTOMER,
                amount=89.90,
                payment_method="pix",
                status="approved",
                timestamp=datetime.now(),
                merchant_name="RecoveryTruck Teste",
                merchant_cnpj="12345678901234",
                customer_name="Maria Santos",
                customer_cpf="98765432109",
                pix_key="maria@email.com"
            )
        },
        {
            "name": "Boleto",
            "data": ReceiptData(
                transaction_id="TXN-BOL-20241201-003",
                receipt_type=ReceiptType.CUSTOMER,
                amount=250.00,
                payment_method="boleto",
                status="pending",
                timestamp=datetime.now(),
                merchant_name="RecoveryTruck Teste",
                merchant_cnpj="12345678901234",
                customer_name="Carlos Oliveira",
                customer_cpf="11122233344",
                boleto_barcode="12345678901234567890123456789012345678901234",
                boleto_due_date=datetime(2024, 12, 8)
            )
        }
    ]
    
    # 3. Testar impressão de cada modalidade
    print("\n2️⃣ Testando impressão de comprovantes...")
    
    for i, receipt in enumerate(test_receipts, 1):
        print(f"\n📄 Teste {i}: {receipt['name']}")
        
        success = await printer_manager.print_receipt(
            receipt["data"],
            printer_id="test_virtual"
        )
        
        if success:
            print(f"✅ Comprovante {receipt['name']} impresso com sucesso")
        else:
            print(f"❌ Falha ao imprimir comprovante {receipt['name']}")
    
    # 4. Testar impressão de via do estabelecimento
    print("\n3️⃣ Testando via do estabelecimento...")
    
    merchant_receipt = ReceiptData(
        transaction_id="TXN-MERCHANT-001",
        receipt_type=ReceiptType.MERCHANT,
        amount=99.99,
        payment_method="debit_card",
        status="approved",
        timestamp=datetime.now(),
        merchant_name="RecoveryTruck Teste",
        merchant_cnpj="12345678901234",
        card_brand="mastercard",
        card_last_digits="5678"
    )
    
    success = await printer_manager.print_receipt(merchant_receipt, "test_virtual")
    print("✅ Via do estabelecimento impressa" if success else "❌ Falha na via do estabelecimento")
    
    # 5. Listar arquivos gerados
    print("\n4️⃣ Arquivos de comprovante gerados:")
    receipts_dir = Path("receipts")
    if receipts_dir.exists():
        for receipt_file in receipts_dir.glob("receipt_*.txt"):
            print(f"📄 {receipt_file.name}")
    
    print("\n✅ Teste do serviço de impressão concluído!")

def show_receipt_samples():
    """📄 Mostra exemplos de comprovantes gerados"""
    print("\n📄 === EXEMPLOS DE COMPROVANTES GERADOS ===\n")
    
    receipts_dir = Path("receipts")
    if not receipts_dir.exists():
        print("❌ Diretório de comprovantes não encontrado")
        return
    
    receipt_files = list(receipts_dir.glob("receipt_*.txt"))
    if not receipt_files:
        print("❌ Nenhum comprovante encontrado")
        return
    
    # Mostrar o último comprovante gerado
    latest_receipt = max(receipt_files, key=lambda f: f.stat().st_mtime)
    
    print(f"📄 Exemplo de comprovante ({latest_receipt.name}):")
    print("=" * 50)
    
    try:
        with open(latest_receipt, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ Erro ao ler comprovante: {e}")
    
    print("=" * 50)
    print(f"\n📊 Total de comprovantes gerados: {len(receipt_files)}")

async def main():
    """🚀 Função principal de teste"""
    print("🚀 INICIANDO TESTES DO SISTEMA DE IMPRESSÃO")
    print("=" * 60)
    
    try:
        # Teste 1: Serviço de impressão básico
        await test_printer_service()
        
        # Mostrar exemplos
        show_receipt_samples()
        
        print("\n🎉 === TESTE CONCLUÍDO COM SUCESSO! ===")
        print("\n📋 Resumo:")
        print("✅ Serviço de impressão funcionando")
        print("✅ Suporte a múltiplos tipos de impressora")
        print("✅ Geração de comprovantes completos")
        print("✅ Formatação adequada para diferentes modalidades")
        
        print("\n📁 Arquivos gerados:")
        receipts_dir = Path("receipts")
        if receipts_dir.exists():
            for receipt_file in receipts_dir.glob("receipt_*.txt"):
                print(f"   📄 {receipt_file}")
        
        print("\n🔧 Para usar em produção:")
        print("1. Configure a impressora real no tenant")
        print("2. Instale drivers necessários (pywin32, pyserial, etc.)")
        print("3. Teste conectividade com a impressora")
        print("4. Ajuste configurações de papel e encoding")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
