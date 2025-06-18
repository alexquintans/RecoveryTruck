# POC - Sistema de Autoatendimento

Esta é uma prova de conceito (POC) do sistema de autoatendimento para totens com pagamento integrado.

## Estrutura do Projeto

```
.
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   └── painel.html
└── requirements.txt
```

## Requisitos

- Python 3.8+
- Navegador web moderno

## Instalação

1. Crie um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando a POC

1. Inicie o backend:
```bash
cd backend
python main.py
```

2. Abra o frontend:
- Abra `frontend/index.html` em uma aba do navegador (este será o totem)
- Abra `frontend/painel.html` em outra aba (este será o painel de chamada)

## Funcionalidades Demonstradas

- Seleção de serviços
- Geração de tickets
- Simulação de pagamento
- Painel de chamada em tempo real
- WebSocket para atualizações instantâneas

## Observações

- Esta é uma POC simplificada para demonstração
- Os dados são armazenados em memória (não persistem após reiniciar)
- O pagamento é simulado (não há integração real com POS)
- O sistema está configurado para rodar localmente

## Próximos Passos

1. Integração com banco de dados real
2. Implementação da integração com POS
3. Adição de autenticação e segurança
4. Implementação de impressão de tickets
5. Adição de mais serviços e configurações 