# Guia de Desenvolvimento do Totem

Este documento descreve as diretrizes e configurações para desenvolvimento do sistema Totem.

## Ambiente de Desenvolvimento

### Requisitos

- Python 3.9+
- Node.js 16+
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

### Setup

1. **Clone do Repositório**
   ```bash
   git clone https://github.com/totem/totem.git
   cd totem
   ```

2. **Ambiente Virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Dependências**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Estrutura do Projeto

```
totem/
├── apps/
│   ├── api/
│   │   ├── config/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   └── tests/
│   └── web/
│       ├── src/
│       ├── public/
│       └── tests/
├── docs/
├── scripts/
└── docker/
```

## Convenções

### Código

1. **Python**
   - PEP 8
   - Type hints
   - Docstrings
   - Black formatter
   - isort
   - flake8

2. **JavaScript/TypeScript**
   - ESLint
   - Prettier
   - TypeScript strict
   - Jest

3. **SQL**
   - snake_case
   - Uppercase keywords
   - Indentação consistente

### Git

1. **Branches**
   - `main`: Produção
   - `develop`: Desenvolvimento
   - `feature/*`: Novas features
   - `bugfix/*`: Correções
   - `hotfix/*`: Correções urgentes

2. **Commits**
   - Conventional Commits
   - Mensagens claras
   - Referências a issues

3. **Pull Requests**
   - Descrição clara
   - Testes incluídos
   - Code review

## Desenvolvimento

### API

1. **Novo Endpoint**
   ```python
   @router.post("/resource")
   async def create_resource(
       resource: ResourceCreate,
       db: Session = Depends(get_db)
   ):
       """
       Create a new resource.
       
       Args:
           resource: Resource data
           db: Database session
           
       Returns:
           Created resource
       """
       return await resource_service.create(db, resource)
   ```

2. **Novo Modelo**
   ```python
   class Resource(Base):
       __tablename__ = "resources"
       
       id = Column(Integer, primary_key=True)
       name = Column(String, nullable=False)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

3. **Novo Serviço**
   ```python
   class ResourceService:
       async def create(self, db: Session, data: ResourceCreate) -> Resource:
           resource = Resource(**data.dict())
           db.add(resource)
           await db.commit()
           return resource
   ```

### Frontend

1. **Novo Componente**
   ```typescript
   interface Props {
     title: string;
     onAction: () => void;
   }
   
   export const Component: React.FC<Props> = ({ title, onAction }) => {
     return (
       <div>
         <h1>{title}</h1>
         <button onClick={onAction}>Action</button>
       </div>
     );
   };
   ```

2. **Novo Hook**
   ```typescript
   export const useResource = (id: string) => {
     const [data, setData] = useState<Resource | null>(null);
     const [loading, setLoading] = useState(true);
     
     useEffect(() => {
       const fetchData = async () => {
         const result = await api.get(`/resources/${id}`);
         setData(result);
         setLoading(false);
       };
       
       fetchData();
     }, [id]);
     
     return { data, loading };
   };
   ```

## Testes

### Backend

1. **Unit Tests**
   ```python
   def test_create_resource():
       resource = ResourceService().create(
           db=Mock(),
           data=ResourceCreate(name="Test")
       )
       assert resource.name == "Test"
   ```

2. **Integration Tests**
   ```python
   async def test_create_resource_endpoint():
       response = await client.post(
           "/resources",
           json={"name": "Test"}
       )
       assert response.status_code == 201
       assert response.json()["name"] == "Test"
   ```

### Frontend

1. **Unit Tests**
   ```typescript
   test("Component renders correctly", () => {
     render(<Component title="Test" onAction={jest.fn()} />);
     expect(screen.getByText("Test")).toBeInTheDocument();
   });
   ```

2. **Integration Tests**
   ```typescript
   test("Resource creation flow", async () => {
     render(<ResourceForm />);
     fireEvent.change(screen.getByLabelText("Name"), {
       target: { value: "Test" }
     });
     fireEvent.click(screen.getByText("Create"));
     await waitFor(() => {
       expect(screen.getByText("Success")).toBeInTheDocument();
     });
   });
   ```

## Debugging

### Backend

1. **Logging**
   ```python
   logger.debug("Processing request", request_id=request.id)
   logger.info("Request completed", duration=1.5)
   logger.error("Request failed", error=str(e))
   ```

2. **Debugger**
   ```python
   import pdb; pdb.set_trace()
   ```

### Frontend

1. **Console**
   ```typescript
   console.log("State:", state);
   console.error("Error:", error);
   ```

2. **Debugger**
   ```typescript
   debugger;
   ```

## Performance

### Backend

1. **Caching**
   ```python
   @cache(ttl=300)
   async def get_resource(id: str):
       return await db.query(Resource).get(id)
   ```

2. **Async**
   ```python
   async def process_items(items: List[Item]):
       return await asyncio.gather(
           *[process_item(item) for item in items]
       )
   ```

### Frontend

1. **Memoization**
   ```typescript
   const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
   ```

2. **Lazy Loading**
   ```typescript
   const Component = lazy(() => import("./Component"));
   ```

## Documentação

### Código

1. **Python**
   ```python
   def function(param: str) -> bool:
       """
       Function description.
       
       Args:
           param: Parameter description
           
       Returns:
           Return value description
           
       Raises:
           Exception: When something goes wrong
       """
       pass
   ```

2. **TypeScript**
   ```typescript
   /**
    * Function description
    * @param param - Parameter description
    * @returns Return value description
    * @throws When something goes wrong
    */
   function function(param: string): boolean {
     return true;
   }
   ```

### API

1. **OpenAPI**
   ```python
   @router.get("/resource/{id}")
   async def get_resource(
       id: str = Path(..., description="Resource ID")
   ):
       """
       Get resource by ID.
       
       Parameters:
           id: Resource ID
           
       Returns:
           Resource data
       """
       pass
   ```

## Manutenção

### Dependências

1. **Atualização**
   ```bash
   pip install --upgrade -r requirements.txt
   npm update
   ```

2. **Auditoria**
   ```bash
   pip-audit
   npm audit
   ```

### Código

1. **Linting**
   ```bash
   flake8
   eslint
   ```

2. **Formatação**
   ```bash
   black .
   prettier --write .
   ```

3. **Testes**
   ```bash
   pytest
   npm test
   ``` 