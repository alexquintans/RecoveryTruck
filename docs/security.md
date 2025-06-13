# Segurança do Sistema Totem

Este documento descreve as configurações e práticas de segurança implementadas no sistema Totem.

## Autenticação

### JWT (JSON Web Tokens)

```python
# Configuração
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Geração de token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
```

### Rate Limiting

```python
# Configuração
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 60  # segundos

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client = request.client.host
    if is_rate_limited(client):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    return await call_next(request)
```

## Autorização

### RBAC (Role-Based Access Control)

```python
# Definição de roles
class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"

# Permissões
PERMISSIONS = {
    Role.ADMIN: ["*"],
    Role.OPERATOR: ["read", "write"],
    Role.USER: ["read"]
}

# Decorator de autorização
def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = get_current_user()
            if permission not in PERMISSIONS[user.role]:
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Proteção de Dados

### Criptografia

```python
# Configuração
ENCRYPTION_KEY = "your-encryption-key"
ENCRYPTION_ALGORITHM = "AES-256-GCM"

# Funções de criptografia
def encrypt_data(data: str) -> str:
    key = base64.b64decode(ENCRYPTION_KEY)
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(nonce + tag + ciphertext).decode()

def decrypt_data(encrypted_data: str) -> str:
    key = base64.b64decode(ENCRYPTION_KEY)
    data = base64.b64decode(encrypted_data)
    nonce = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

### Sanitização

```python
# Sanitização de inputs
def sanitize_input(data: str) -> str:
    # Remove caracteres especiais
    data = re.sub(r'[^\w\s-]', '', data)
    # Remove espaços extras
    data = ' '.join(data.split())
    return data

# Validação de dados
def validate_payment_data(data: dict) -> bool:
    required_fields = ['amount', 'currency', 'description']
    return all(field in data for field in required_fields)
```

## Segurança de Rede

### CORS (Cross-Origin Resource Sharing)

```python
# Configuração
CORS_ORIGINS = [
    "https://totem.example.com",
    "https://admin.totem.example.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### TLS/SSL

```nginx
# Configuração Nginx
server {
    listen 443 ssl;
    server_name totem.example.com;

    ssl_certificate /etc/nginx/ssl/totem.crt;
    ssl_certificate_key /etc/nginx/ssl/totem.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

## Logs de Segurança

### Auditoria

```python
# Log de auditoria
async def log_audit(
    user_id: int,
    action: str,
    resource: str,
    details: dict
):
    await db.execute(
        audit_logs.insert().values(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            timestamp=datetime.utcnow()
        )
    )
```

### Monitoramento

```python
# Alertas de segurança
async def check_security_alerts():
    # Verifica tentativas de login
    failed_logins = await db.execute(
        select([login_attempts])
        .where(login_attempts.c.failed_attempts >= 5)
        .where(login_attempts.c.timestamp >= datetime.utcnow() - timedelta(minutes=15))
    )
    
    if failed_logins:
        await send_security_alert(
            "Multiple failed login attempts detected",
            failed_logins
        )
```

## Backup e Recuperação

### Backup

```python
# Backup automático
async def backup_database():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    
    # Backup do banco
    subprocess.run([
        "pg_dump",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-f", backup_file
    ])
    
    # Upload para storage seguro
    await upload_to_secure_storage(backup_file)
```

### Recuperação

```python
# Procedimento de recuperação
async def restore_database(backup_file: str):
    # Download do backup
    await download_from_secure_storage(backup_file)
    
    # Restauração
    subprocess.run([
        "psql",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-f", backup_file
    ])
```

## Incidentes de Segurança

### Procedimento de Resposta

1. **Identificação**
   - Monitoramento de logs
   - Alertas de segurança
   - Relatórios de usuários

2. **Contenção**
   - Isolamento do sistema afetado
   - Bloqueio de acessos suspeitos
   - Backup de evidências

3. **Eradicação**
   - Correção da vulnerabilidade
   - Atualização de sistemas
   - Limpeza de malware

4. **Recuperação**
   - Restauração de sistemas
   - Verificação de integridade
   - Retorno à operação normal

5. **Análise**
   - Root cause analysis
   - Documentação do incidente
   - Atualização de procedimentos

### Contatos de Emergência

- **Segurança**: security@totem.example.com
- **Suporte**: support@totem.example.com
- **Administração**: admin@totem.example.com

## Atualizações de Segurança

### Processo de Patch

1. **Identificação**
   - Monitoramento de vulnerabilidades
   - Análise de dependências
   - Relatórios de segurança

2. **Priorização**
   - Severidade da vulnerabilidade
   - Impacto no sistema
   - Complexidade da correção

3. **Testes**
   - Ambiente de staging
   - Testes de regressão
   - Validação de segurança

4. **Deploy**
   - Janela de manutenção
   - Rollback plan
   - Monitoramento pós-deploy

### Dependências

```python
# Verificação de segurança
async def check_dependencies():
    # Verifica vulnerabilidades
    subprocess.run(["safety", "check"])
    
    # Atualiza dependências
    subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"])
```

## Conformidade

### LGPD

- Consentimento explícito
- Finalidade específica
- Acesso aos dados
- Exclusão de dados
- Relatório de incidentes

### PCI DSS

- Criptografia de dados
- Controle de acesso
- Monitoramento de rede
- Testes de vulnerabilidade
- Política de segurança

## Treinamento

### Desenvolvedores

- Segurança de aplicações
- Boas práticas de código
- Análise de vulnerabilidades
- Resposta a incidentes

### Operadores

- Procedimentos de segurança
- Monitoramento de logs
- Resposta a alertas
- Backup e recuperação

## Checklist de Segurança

### Diário

- [ ] Verificação de logs
- [ ] Monitoramento de alertas
- [ ] Backup de dados
- [ ] Atualização de sistemas

### Semanal

- [ ] Análise de vulnerabilidades
- [ ] Revisão de permissões
- [ ] Teste de backup
- [ ] Atualização de dependências

### Mensal

- [ ] Auditoria de segurança
- [ ] Revisão de políticas
- [ ] Treinamento de equipe
- [ ] Relatório de segurança