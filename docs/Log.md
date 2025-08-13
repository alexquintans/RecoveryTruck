🔍 DEBUG - VITE_WS_URL: wss://recoverytruck-production.up.railway.app/ws
index-b6e70955.js:96 🔍 DEBUG - baseWs inicial: wss://recoverytruck-production.up.railway.app/ws
index-b6e70955.js:96 🔍 DEBUG - baseWs após correção: wss://recoverytruck-production.up.railway.app/ws
index-b6e70955.js:96 🔍 DEBUG - WebSocket URL final construída: wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c
index-b6e70955.js:96 🔍 DEBUG CRÍTICO - myTickets useMemo - VERIFICAÇÃO INICIAL: {myTicketsQueryData: undefined, myTicketsQueryDataLength: 0, myTicketsQueryDataType: 'undefined', isArray: false, firstItem: undefined, …}
index-b6e70955.js:96 🔍 DEBUG - myTickets useMemo - DADOS APÓS FALLBACK: {rawData: Array(0), rawDataLength: 0, rawDataType: 'object', hasValidData: false, firstRawItem: undefined, …}
index-b6e70955.js:96 🔍 DEBUG - myTickets: Nenhum dado para processar
(anonymous) @ index-b6e70955.js:96
useMemo @ index-b6e70955.js:38
At.useMemo @ index-b6e70955.js:9
Am @ index-b6e70955.js:96
eO @ index-b6e70955.js:297
F2 @ index-b6e70955.js:38
c3 @ index-b6e70955.js:40
o3 @ index-b6e70955.js:40
wN @ index-b6e70955.js:40
Cp @ index-b6e70955.js:40
r3 @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this warning
index-b6e70955.js:297 🔍 DEBUG - safeMyTickets useMemo CORRIGIDO: {myTickets: Array(0), myTicketsLength: 0, result: Array(0), resultLength: 0, myTicketsDetails: Array(0), …}
index-b6e70955.js:297 🔍 DEBUG - safePendingPaymentTickets useMemo: {pendingPaymentTickets: Array(0), pendingPaymentTicketsLength: 0, result: Array(0), resultLength: 0}
index-b6e70955.js:303 🔍 DEBUG - Organizando filas por serviço:
index-b6e70955.js:303 🔍 DEBUG -   safeTickets: 0
index-b6e70955.js:303 🔍 DEBUG -   activeServices: 0
index-b6e70955.js:303 🔍 DEBUG - organizeTicketsByService - Início: {totalTickets: 0, totalServices: 0, services: Array(0)}
index-b6e70955.js:303 🔍 DEBUG - Tickets na fila: 0
index-b6e70955.js:303 🔍 DEBUG - organizeTicketsByService - Resultado final: []
index-b6e70955.js:303 🔍 DEBUG - Resultado das filas organizadas:
index-b6e70955.js:96 🔍 DEBUG - myTicketsQuery - Iniciando query...
index-b6e70955.js:96 🔍 DEBUG - myTicketsQuery - enabled: true
index-b6e70955.js:96 🔍 DEBUG - myTicketsQuery - user: {id: 'f4e5df1f-d538-49eb-915e-ec99f0496dc2', name: 'Operador Admin', email: 'admin@exemplo.com', role: 'operator', tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:96 🔍 DEBUG - myTicketsQuery - isAuthenticated: true
index-b6e70955.js:96 🔍 DEBUG - myTicketsQuery - user?.id: f4e5df1f-d538-49eb-915e-ec99f0496dc2
index-b6e70955.js:96 🔍 DEBUG - Chamando getMyTickets...
index-b6e70955.js:80 🔍 DEBUG - ticketService.getMyTickets - Iniciando chamada...
index-b6e70955.js:96 🔍 Buscando tickets cancelados...
index-b6e70955.js:96 🔍 DEBUG - pendingPaymentQuery - Iniciando...
index-b6e70955.js:80 🔌 WebSocket - useEffect - Iniciando conexão
index-b6e70955.js:80 🔌 WebSocket - Conectando: wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c
index-b6e70955.js:297 🔄 Carregando dados para tenant: 7f02a566-2406-436d-b10d-90ecddd3fe2d
index-b6e70955.js:309 🔍 DEBUG - ResumoVisual dados: {services: 0, servicesAtivos: 0, equipments: 0, equipmentsAtivos: 0, extras: 0, …}
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - URL: /tickets/equipment/status
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Params: {tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/queue', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/my-tickets', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/operation', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/operation/equipment', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/status/pending-payment', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/equipment/status', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:291  GET https://recoverytruck-production.up.railway.app/operator/equipments?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
l1 @ index-b6e70955.js:291
(anonymous) @ index-b6e70955.js:297
(anonymous) @ index-b6e70955.js:297
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:291  GET https://recoverytruck-production.up.railway.app/operator/services?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
Fw @ index-b6e70955.js:291
(anonymous) @ index-b6e70955.js:297
(anonymous) @ index-b6e70955.js:297
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:291  GET https://recoverytruck-production.up.railway.app/operator/extras?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
Ow @ index-b6e70955.js:291
(anonymous) @ index-b6e70955.js:297
(anonymous) @ index-b6e70955.js:297
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:297 ✅ Dados carregados: {services: Array(0), equipments: Array(0), extras: Array(0)}
index-b6e70955.js:303 🔍 DEBUG - Organizando filas por serviço:
index-b6e70955.js:303 🔍 DEBUG -   safeTickets: 0
index-b6e70955.js:303 🔍 DEBUG -   activeServices: 0
index-b6e70955.js:303 🔍 DEBUG - organizeTicketsByService - Início: {totalTickets: 0, totalServices: 0, services: Array(0)}
index-b6e70955.js:303 🔍 DEBUG - Tickets na fila: 0
index-b6e70955.js:303 🔍 DEBUG - organizeTicketsByService - Resultado final: []
index-b6e70955.js:303 🔍 DEBUG - Resultado das filas organizadas:
index-b6e70955.js:309 🔍 DEBUG - ResumoVisual dados: {services: 0, servicesAtivos: 0, equipments: 0, equipmentsAtivos: 0, extras: 0, …}
index-b6e70955.js:80 🔍 DEBUG - Axios Response Interceptor: {url: '/tickets/queue', method: 'get', status: 200, statusText: '', data: Array(20)}
index-b6e70955.js:96 🔍 DEBUG - Queue query result: {total: 0, itemsCount: 0, byService: {…}, itemsDetails: undefined}
index-b6e70955.js:303 🔍 DEBUG - Organizando filas por serviço:
index-b6e70955.js:303 🔍 DEBUG -   safeTickets: 0
index-b6e70955.js:303 🔍 DEBUG -   activeServices: 0
index-b6e70955.js:303 🔍 DEBUG - organizeTicketsByService - Início: {totalTickets: 0, totalServices: 0, services: Array(0)}
index-b6e70955.js:303 🔍 DEBUG - Tickets na fila: 0
index-b6e70955.js:303 🔍 DEBUG - organizeTicketsByService - Resultado final: []
index-b6e70955.js:303 🔍 DEBUG - Resultado das filas organizadas:
index-b6e70955.js:80 🔍 DEBUG - Axios Response Interceptor: {url: '/tickets/my-tickets', method: 'get', status: 200, statusText: '', data: Array(148)}
index-b6e70955.js:80 🔍 DEBUG - ticketService.getMyTickets - Response: {status: 200, dataLength: 148, data: Array(148), ticketsStructure: Array(148)}
index-b6e70955.js:96 🔍 DEBUG - getMyTickets result: {total: 148, tickets: Array(148)}
index-b6e70955.js:96 🔍 DEBUG - getMyTickets - RESULTADO DO BACKEND (sem filtro adicional): {total: 148, tickets: Array(148), statuses: Array(148)}
index-b6e70955.js:96 🔍 DEBUG CRÍTICO - myTickets useMemo - VERIFICAÇÃO INICIAL: {myTicketsQueryData: Array(148), myTicketsQueryDataLength: 148, myTicketsQueryDataType: 'object', isArray: true, firstItem: {…}, …}
index-b6e70955.js:96 🔍 DEBUG - myTickets useMemo - DADOS APÓS FALLBACK: {rawData: Array(148), rawDataLength: 148, rawDataType: 'object', hasValidData: true, firstRawItem: {…}, …}
index-b6e70955.js:96 🔍 DEBUG - myTickets - Tickets válidos encontrados: 148
index-b6e70955.js:96 🔍 DEBUG - myTickets useMemo - DADOS PROCESSADOS: {processedTickets: Array(148), processedLength: 148, processedIds: Array(148), hasProcessedData: true, firstProcessedItem: {…}, …}
index-b6e70955.js:96 🔍 DEBUG CRÍTICO - myTickets FINAL: {returnValue: Array(148), returnValueLength: 148, returnValueType: 'object', isArray: true, willBeReturned: 'SIM - Dados serão retornados'}
index-b6e70955.js:297 🔍 DEBUG - safeMyTickets useMemo CORRIGIDO: {myTickets: Array(148), myTicketsLength: 148, result: Array(148), resultLength: 148, myTicketsDetails: Array(148), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:297 🔄 Carregando progresso automático para tickets: (148) ['ca4b4167-01be-4a16-9f1e-1586c25e2290', 'e912526f-faa3-48b6-b770-396b18854da2', 'c932ada0-f69b-45f2-ba13-2da6923a8f56', '78b6354b-be59-440c-b74c-4a0283bac2e9', '019435e3-4c97-402e-a3b0-6436e0c2d6c2', '52aeb6bb-c371-4a53-ab58-63fe525f5087', '09425b89-648a-4529-a9c1-6eae54784a6f', '68da1dbe-9252-4f10-8622-da31eeeb9540', '5cdab3b8-a48a-400d-b1bc-d4adf7d8a3ac', 'a837deb7-a532-4a20-bf00-4e1a707e4ada', 'c5287da0-8fae-4c4f-9891-0ad70179eed8', 'b4fb1704-d969-4e58-8a50-007f0d04c728', '07a8c6fb-341f-4c22-b5f4-896d5a40b33b', 'b0366398-0916-4583-aa1f-4e98b576d949', '780a1c93-cf73-46f3-9cfa-4e51ff53e793', 'f91347d0-d778-491e-9962-3aec6dcb575f', '7d1a79cd-7bae-4241-ae79-ea22a3ecd2e2', '5a3646cb-003f-407b-a0ce-736e48fb7ddd', 'a21c9a4d-74d6-4d66-9975-e00c59563ee5', '3f2c3df7-6879-45c1-a9ae-7d4d4f34d44e', 'c062e0ee-2e6c-47ba-929b-8f92f5dabc28', '43f77986-9952-4229-9187-23b88559694d', 'c8d8d68a-1250-44a2-9078-7c994ab452d5', '97b7f502-0f31-49a8-b3ae-b5ac171362d2', 'aba83b70-0cdd-4285-8a33-848e5602bdb4', 'f79e1b7e-f874-4680-8e14-a40b4deff8a7', 'cea41f86-f98f-4f42-9c49-7d15d0ea1e54', '9d74acd1-06d8-4774-931a-0c0b8f362b24', '25b75f3a-e42f-4e71-b56c-8c6c2d218f49', '369e1777-5d8a-4e9d-a627-196d0adfd6f9', '623ce480-db1e-4e8b-a3c0-5e5e572ccf65', '44bb6cac-4a0a-44b6-967c-255e7931aa7a', '2a16574b-02a2-42d6-9401-7e9fa689d06c', 'c789f2e9-f84c-4d7b-9652-ad89d2f47431', 'da6c5736-d7ff-497c-93c1-2af69378e2dd', 'b3315e1f-5478-435a-8ace-aaba31dcf4e8', 'f480f863-cf86-4d2f-9ec3-6573b63bc6c4', '06dea4aa-64f3-466a-8457-1a439e1e4c12', 'f66160de-eff9-41be-9b9f-95c702dea74d', '3f062845-853d-4426-88ca-5176a67c9907', '1f0d2682-d85f-4bf3-891c-8fd8fb145761', '714c21d0-d70c-4bb5-927c-d9242183e8aa', '762ed09d-2eca-4d93-a316-dbef1ca9fd2f', '70367f95-cc28-4f7b-88b8-92c17dadb682', '06984e1f-9a66-4d87-af9a-298dadbd6502', '3188cd23-98f1-4bc2-bd6a-c8b86566df54', '3cd577db-dd83-47bb-9a41-b115ae2c03e6', 'c8abfe83-8148-4ffe-8221-b019d6e73384', '58aa5fec-9c87-46cf-aa93-6cb2bae2efc6', '4ab32299-3b52-4d4b-b10e-cc6447105d55', '4b9aa20a-dfd1-459d-bb56-af459d84c9c6', '81d23f80-a4c4-4cc9-9a0b-aa3e2b95f195', 'e5e47637-82a8-4919-972d-be39f4f39196', 'cb37565e-9e7f-4e75-ab3b-542382ba8742', 'c1b80aa7-93fc-482a-9336-e5eb24e5a173', '47ee1eb9-43d4-4dcf-bbb2-bef5c9e3438e', '9a42b7ed-195e-446a-a0a2-cbfd11852f41', 'b95437c9-643d-464e-ab49-bb122c612a81', '0c5f4178-53c1-4071-bb53-7019e1645af9', '29a66c99-f712-48b4-8dde-adf0f07d9c0f', '1b77a303-a04c-48a0-a597-aec920a5d3eb', '9e7293d5-1508-4ca7-9deb-0e9c27dd28cc', '182f68b7-c259-48ff-9ed3-62c26a8cc952', 'b761efdd-726c-4cd0-9939-94d722d1e1f5', 'f580b241-c6c8-43ac-97b9-46055d2457e6', 'b92096ef-31fc-44c4-97fe-a9861cb3d74e', '9450b79d-2c8d-46bd-8e3e-2705bcdc085e', '6e7b39f5-3c0a-4876-bb22-b67d6ddaaa83', '3b843175-7dcc-4b69-93c2-d09484c647db', 'd0e5edbe-a86a-4b83-8b81-c83e6b6170f0', '7964e727-448d-468c-bdf3-a82ae2ce8d97', 'eb8dc879-9535-411b-8da7-dfe8c5dfa118', '9972d1b9-5b13-4057-90c1-3626a7d2cf83', 'ef0ac486-8b81-413e-98d2-5aa96c1c298d', 'dc65b2dd-c0cb-4045-b20a-894940f09b7f', 'e92947c8-ed13-4c4d-8448-12792bb26771', '40beeb46-7f6e-41a5-af92-aabda5e12bbc', 'e8bf76c8-d6da-4a63-ba10-2614812b5642', 'f31f7c7e-d28d-4353-8de5-45c80c58b061', '765839e8-7758-472b-a59e-06daf3fd09ef', '94e142e1-9d97-4a0d-9758-ec01eefec9cf', '9f892a43-acd6-4f05-b4ef-9fcdb84681a1', '3eef803a-51a2-4c78-80b6-6dbd85f264e2', '966ee9a1-a434-4f76-b604-ebf4ef6cfac2', '439e7f50-2a0e-44fb-a403-08e715057285', '79cec8e0-3071-4c68-acd6-f939d83291f9', '689a39cd-b78a-4e38-8dc8-9c23b24a4636', '2435dfc6-67ab-414d-b53b-eb8257cef646', '37a909d3-2ef6-409e-84dd-522229f6aab2', 'aa672eb3-7f04-4860-89f0-b024ecef3aec', 'dfee925b-e51e-4066-b285-53af46a0bf1f', 'eed0a93d-02ff-44cd-8390-6b4883862646', '91be302a-f169-4aa2-a251-d803d1718f69', 'afa33ad9-ac20-4898-bb12-f8b2532e1e7f', '56400ffa-270e-43fa-a124-7457de0bd00b', 'e33f0bb8-8253-489f-a843-920cd561851d', 'e85af4c0-e459-4dcf-b157-e55dc6422510', '210a000f-7468-460b-8bcf-ddb51b4695c3', '4180a8cc-d031-448c-ada2-88d6a79744e3', '7ad0bc4a-f5d7-4d97-9b81-be790128ebcc', …]
index-b6e70955.js:297 🔄 Carregando progresso do ticket: ca4b4167-01be-4a16-9f1e-1586c25e2290
index-b6e70955.js:309 🔍 DEBUG - ResumoVisual dados: {services: 0, servicesAtivos: 0, equipments: 0, equipmentsAtivos: 0, extras: 0, …}
index-b6e70955.js:297 ✅ Progresso carregado para ticket: ca4b4167-01be-4a16-9f1e-1586c25e2290
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e912526f-faa3-48b6-b770-396b18854da2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e912526f-faa3-48b6-b770-396b18854da2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c932ada0-f69b-45f2-ba13-2da6923a8f56
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c932ada0-f69b-45f2-ba13-2da6923a8f56
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 78b6354b-be59-440c-b74c-4a0283bac2e9
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 78b6354b-be59-440c-b74c-4a0283bac2e9
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 019435e3-4c97-402e-a3b0-6436e0c2d6c2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 019435e3-4c97-402e-a3b0-6436e0c2d6c2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 52aeb6bb-c371-4a53-ab58-63fe525f5087
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 52aeb6bb-c371-4a53-ab58-63fe525f5087
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 09425b89-648a-4529-a9c1-6eae54784a6f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 09425b89-648a-4529-a9c1-6eae54784a6f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 68da1dbe-9252-4f10-8622-da31eeeb9540
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 68da1dbe-9252-4f10-8622-da31eeeb9540
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 5cdab3b8-a48a-400d-b1bc-d4adf7d8a3ac
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 5cdab3b8-a48a-400d-b1bc-d4adf7d8a3ac
index-b6e70955.js:297 🔄 Carregando progresso do ticket: a837deb7-a532-4a20-bf00-4e1a707e4ada
index-b6e70955.js:297 ✅ Progresso carregado para ticket: a837deb7-a532-4a20-bf00-4e1a707e4ada
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c5287da0-8fae-4c4f-9891-0ad70179eed8
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c5287da0-8fae-4c4f-9891-0ad70179eed8
index-b6e70955.js:297 🔄 Carregando progresso do ticket: b4fb1704-d969-4e58-8a50-007f0d04c728
index-b6e70955.js:297 ✅ Progresso carregado para ticket: b4fb1704-d969-4e58-8a50-007f0d04c728
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 07a8c6fb-341f-4c22-b5f4-896d5a40b33b
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 07a8c6fb-341f-4c22-b5f4-896d5a40b33b
index-b6e70955.js:297 🔄 Carregando progresso do ticket: b0366398-0916-4583-aa1f-4e98b576d949
index-b6e70955.js:297 ✅ Progresso carregado para ticket: b0366398-0916-4583-aa1f-4e98b576d949
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 780a1c93-cf73-46f3-9cfa-4e51ff53e793
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 780a1c93-cf73-46f3-9cfa-4e51ff53e793
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f91347d0-d778-491e-9962-3aec6dcb575f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f91347d0-d778-491e-9962-3aec6dcb575f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 7d1a79cd-7bae-4241-ae79-ea22a3ecd2e2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 7d1a79cd-7bae-4241-ae79-ea22a3ecd2e2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 5a3646cb-003f-407b-a0ce-736e48fb7ddd
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 5a3646cb-003f-407b-a0ce-736e48fb7ddd
index-b6e70955.js:297 🔄 Carregando progresso do ticket: a21c9a4d-74d6-4d66-9975-e00c59563ee5
index-b6e70955.js:297 ✅ Progresso carregado para ticket: a21c9a4d-74d6-4d66-9975-e00c59563ee5
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 3f2c3df7-6879-45c1-a9ae-7d4d4f34d44e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 3f2c3df7-6879-45c1-a9ae-7d4d4f34d44e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c062e0ee-2e6c-47ba-929b-8f92f5dabc28
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c062e0ee-2e6c-47ba-929b-8f92f5dabc28
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 43f77986-9952-4229-9187-23b88559694d
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 43f77986-9952-4229-9187-23b88559694d
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c8d8d68a-1250-44a2-9078-7c994ab452d5
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c8d8d68a-1250-44a2-9078-7c994ab452d5
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 97b7f502-0f31-49a8-b3ae-b5ac171362d2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 97b7f502-0f31-49a8-b3ae-b5ac171362d2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: aba83b70-0cdd-4285-8a33-848e5602bdb4
index-b6e70955.js:297 ✅ Progresso carregado para ticket: aba83b70-0cdd-4285-8a33-848e5602bdb4
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f79e1b7e-f874-4680-8e14-a40b4deff8a7
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f79e1b7e-f874-4680-8e14-a40b4deff8a7
index-b6e70955.js:297 🔄 Carregando progresso do ticket: cea41f86-f98f-4f42-9c49-7d15d0ea1e54
index-b6e70955.js:297 ✅ Progresso carregado para ticket: cea41f86-f98f-4f42-9c49-7d15d0ea1e54
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9d74acd1-06d8-4774-931a-0c0b8f362b24
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9d74acd1-06d8-4774-931a-0c0b8f362b24
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 25b75f3a-e42f-4e71-b56c-8c6c2d218f49
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 25b75f3a-e42f-4e71-b56c-8c6c2d218f49
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 369e1777-5d8a-4e9d-a627-196d0adfd6f9
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 369e1777-5d8a-4e9d-a627-196d0adfd6f9
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 623ce480-db1e-4e8b-a3c0-5e5e572ccf65
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 623ce480-db1e-4e8b-a3c0-5e5e572ccf65
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 44bb6cac-4a0a-44b6-967c-255e7931aa7a
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 44bb6cac-4a0a-44b6-967c-255e7931aa7a
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 2a16574b-02a2-42d6-9401-7e9fa689d06c
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 2a16574b-02a2-42d6-9401-7e9fa689d06c
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c789f2e9-f84c-4d7b-9652-ad89d2f47431
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c789f2e9-f84c-4d7b-9652-ad89d2f47431
index-b6e70955.js:297 🔄 Carregando progresso do ticket: da6c5736-d7ff-497c-93c1-2af69378e2dd
index-b6e70955.js:297 ✅ Progresso carregado para ticket: da6c5736-d7ff-497c-93c1-2af69378e2dd
index-b6e70955.js:297 🔄 Carregando progresso do ticket: b3315e1f-5478-435a-8ace-aaba31dcf4e8
index-b6e70955.js:297 ✅ Progresso carregado para ticket: b3315e1f-5478-435a-8ace-aaba31dcf4e8
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f480f863-cf86-4d2f-9ec3-6573b63bc6c4
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f480f863-cf86-4d2f-9ec3-6573b63bc6c4
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 06dea4aa-64f3-466a-8457-1a439e1e4c12
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 06dea4aa-64f3-466a-8457-1a439e1e4c12
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f66160de-eff9-41be-9b9f-95c702dea74d
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f66160de-eff9-41be-9b9f-95c702dea74d
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 3f062845-853d-4426-88ca-5176a67c9907
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 3f062845-853d-4426-88ca-5176a67c9907
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 1f0d2682-d85f-4bf3-891c-8fd8fb145761
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 1f0d2682-d85f-4bf3-891c-8fd8fb145761
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 714c21d0-d70c-4bb5-927c-d9242183e8aa
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 714c21d0-d70c-4bb5-927c-d9242183e8aa
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 762ed09d-2eca-4d93-a316-dbef1ca9fd2f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 762ed09d-2eca-4d93-a316-dbef1ca9fd2f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 70367f95-cc28-4f7b-88b8-92c17dadb682
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 70367f95-cc28-4f7b-88b8-92c17dadb682
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 06984e1f-9a66-4d87-af9a-298dadbd6502
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 06984e1f-9a66-4d87-af9a-298dadbd6502
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 3188cd23-98f1-4bc2-bd6a-c8b86566df54
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 3188cd23-98f1-4bc2-bd6a-c8b86566df54
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 3cd577db-dd83-47bb-9a41-b115ae2c03e6
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 3cd577db-dd83-47bb-9a41-b115ae2c03e6
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c8abfe83-8148-4ffe-8221-b019d6e73384
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c8abfe83-8148-4ffe-8221-b019d6e73384
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 58aa5fec-9c87-46cf-aa93-6cb2bae2efc6
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 58aa5fec-9c87-46cf-aa93-6cb2bae2efc6
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 4ab32299-3b52-4d4b-b10e-cc6447105d55
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 4ab32299-3b52-4d4b-b10e-cc6447105d55
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 4b9aa20a-dfd1-459d-bb56-af459d84c9c6
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 4b9aa20a-dfd1-459d-bb56-af459d84c9c6
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 81d23f80-a4c4-4cc9-9a0b-aa3e2b95f195
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 81d23f80-a4c4-4cc9-9a0b-aa3e2b95f195
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e5e47637-82a8-4919-972d-be39f4f39196
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e5e47637-82a8-4919-972d-be39f4f39196
index-b6e70955.js:297 🔄 Carregando progresso do ticket: cb37565e-9e7f-4e75-ab3b-542382ba8742
index-b6e70955.js:297 ✅ Progresso carregado para ticket: cb37565e-9e7f-4e75-ab3b-542382ba8742
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c1b80aa7-93fc-482a-9336-e5eb24e5a173
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c1b80aa7-93fc-482a-9336-e5eb24e5a173
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 47ee1eb9-43d4-4dcf-bbb2-bef5c9e3438e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 47ee1eb9-43d4-4dcf-bbb2-bef5c9e3438e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9a42b7ed-195e-446a-a0a2-cbfd11852f41
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9a42b7ed-195e-446a-a0a2-cbfd11852f41
index-b6e70955.js:297 🔄 Carregando progresso do ticket: b95437c9-643d-464e-ab49-bb122c612a81
index-b6e70955.js:297 ✅ Progresso carregado para ticket: b95437c9-643d-464e-ab49-bb122c612a81
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 0c5f4178-53c1-4071-bb53-7019e1645af9
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 0c5f4178-53c1-4071-bb53-7019e1645af9
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 29a66c99-f712-48b4-8dde-adf0f07d9c0f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 29a66c99-f712-48b4-8dde-adf0f07d9c0f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 1b77a303-a04c-48a0-a597-aec920a5d3eb
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 1b77a303-a04c-48a0-a597-aec920a5d3eb
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9e7293d5-1508-4ca7-9deb-0e9c27dd28cc
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9e7293d5-1508-4ca7-9deb-0e9c27dd28cc
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 182f68b7-c259-48ff-9ed3-62c26a8cc952
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 182f68b7-c259-48ff-9ed3-62c26a8cc952
index-b6e70955.js:297 🔄 Carregando progresso do ticket: b761efdd-726c-4cd0-9939-94d722d1e1f5
index-b6e70955.js:297 ✅ Progresso carregado para ticket: b761efdd-726c-4cd0-9939-94d722d1e1f5
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f580b241-c6c8-43ac-97b9-46055d2457e6
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f580b241-c6c8-43ac-97b9-46055d2457e6
index-b6e70955.js:297 🔄 Carregando progresso do ticket: b92096ef-31fc-44c4-97fe-a9861cb3d74e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: b92096ef-31fc-44c4-97fe-a9861cb3d74e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9450b79d-2c8d-46bd-8e3e-2705bcdc085e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9450b79d-2c8d-46bd-8e3e-2705bcdc085e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 6e7b39f5-3c0a-4876-bb22-b67d6ddaaa83
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 6e7b39f5-3c0a-4876-bb22-b67d6ddaaa83
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 3b843175-7dcc-4b69-93c2-d09484c647db
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 3b843175-7dcc-4b69-93c2-d09484c647db
index-b6e70955.js:297 🔄 Carregando progresso do ticket: d0e5edbe-a86a-4b83-8b81-c83e6b6170f0
index-b6e70955.js:297 ✅ Progresso carregado para ticket: d0e5edbe-a86a-4b83-8b81-c83e6b6170f0
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 7964e727-448d-468c-bdf3-a82ae2ce8d97
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 7964e727-448d-468c-bdf3-a82ae2ce8d97
index-b6e70955.js:297 🔄 Carregando progresso do ticket: eb8dc879-9535-411b-8da7-dfe8c5dfa118
index-b6e70955.js:297 ✅ Progresso carregado para ticket: eb8dc879-9535-411b-8da7-dfe8c5dfa118
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9972d1b9-5b13-4057-90c1-3626a7d2cf83
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9972d1b9-5b13-4057-90c1-3626a7d2cf83
index-b6e70955.js:297 🔄 Carregando progresso do ticket: ef0ac486-8b81-413e-98d2-5aa96c1c298d
index-b6e70955.js:297 ✅ Progresso carregado para ticket: ef0ac486-8b81-413e-98d2-5aa96c1c298d
index-b6e70955.js:297 🔄 Carregando progresso do ticket: dc65b2dd-c0cb-4045-b20a-894940f09b7f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: dc65b2dd-c0cb-4045-b20a-894940f09b7f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e92947c8-ed13-4c4d-8448-12792bb26771
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e92947c8-ed13-4c4d-8448-12792bb26771
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 40beeb46-7f6e-41a5-af92-aabda5e12bbc
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 40beeb46-7f6e-41a5-af92-aabda5e12bbc
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e8bf76c8-d6da-4a63-ba10-2614812b5642
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e8bf76c8-d6da-4a63-ba10-2614812b5642
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f31f7c7e-d28d-4353-8de5-45c80c58b061
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f31f7c7e-d28d-4353-8de5-45c80c58b061
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 765839e8-7758-472b-a59e-06daf3fd09ef
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 765839e8-7758-472b-a59e-06daf3fd09ef
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 94e142e1-9d97-4a0d-9758-ec01eefec9cf
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 94e142e1-9d97-4a0d-9758-ec01eefec9cf
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9f892a43-acd6-4f05-b4ef-9fcdb84681a1
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9f892a43-acd6-4f05-b4ef-9fcdb84681a1
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 3eef803a-51a2-4c78-80b6-6dbd85f264e2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 3eef803a-51a2-4c78-80b6-6dbd85f264e2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 966ee9a1-a434-4f76-b604-ebf4ef6cfac2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 966ee9a1-a434-4f76-b604-ebf4ef6cfac2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 439e7f50-2a0e-44fb-a403-08e715057285
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 439e7f50-2a0e-44fb-a403-08e715057285
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 79cec8e0-3071-4c68-acd6-f939d83291f9
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 79cec8e0-3071-4c68-acd6-f939d83291f9
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 689a39cd-b78a-4e38-8dc8-9c23b24a4636
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 689a39cd-b78a-4e38-8dc8-9c23b24a4636
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 2435dfc6-67ab-414d-b53b-eb8257cef646
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 2435dfc6-67ab-414d-b53b-eb8257cef646
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 37a909d3-2ef6-409e-84dd-522229f6aab2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 37a909d3-2ef6-409e-84dd-522229f6aab2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: aa672eb3-7f04-4860-89f0-b024ecef3aec
index-b6e70955.js:297 ✅ Progresso carregado para ticket: aa672eb3-7f04-4860-89f0-b024ecef3aec
index-b6e70955.js:297 🔄 Carregando progresso do ticket: dfee925b-e51e-4066-b285-53af46a0bf1f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: dfee925b-e51e-4066-b285-53af46a0bf1f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: eed0a93d-02ff-44cd-8390-6b4883862646
index-b6e70955.js:297 ✅ Progresso carregado para ticket: eed0a93d-02ff-44cd-8390-6b4883862646
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 91be302a-f169-4aa2-a251-d803d1718f69
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 91be302a-f169-4aa2-a251-d803d1718f69
index-b6e70955.js:297 🔄 Carregando progresso do ticket: afa33ad9-ac20-4898-bb12-f8b2532e1e7f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: afa33ad9-ac20-4898-bb12-f8b2532e1e7f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 56400ffa-270e-43fa-a124-7457de0bd00b
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 56400ffa-270e-43fa-a124-7457de0bd00b
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e33f0bb8-8253-489f-a843-920cd561851d
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e33f0bb8-8253-489f-a843-920cd561851d
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e85af4c0-e459-4dcf-b157-e55dc6422510
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e85af4c0-e459-4dcf-b157-e55dc6422510
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 210a000f-7468-460b-8bcf-ddb51b4695c3
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 210a000f-7468-460b-8bcf-ddb51b4695c3
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 4180a8cc-d031-448c-ada2-88d6a79744e3
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 4180a8cc-d031-448c-ada2-88d6a79744e3
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 7ad0bc4a-f5d7-4d97-9b81-be790128ebcc
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 7ad0bc4a-f5d7-4d97-9b81-be790128ebcc
index-b6e70955.js:297 🔄 Carregando progresso do ticket: d778dc13-1109-4c5c-914d-22beb3b350be
index-b6e70955.js:297 ✅ Progresso carregado para ticket: d778dc13-1109-4c5c-914d-22beb3b350be
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 2074b3ad-1bd4-4b1f-b896-63022bbecb01
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 2074b3ad-1bd4-4b1f-b896-63022bbecb01
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 30803890-914a-4729-b082-9ada60f05366
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 30803890-914a-4729-b082-9ada60f05366
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 87f782e4-ec81-4ccc-8840-1b5c6280aa41
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 87f782e4-ec81-4ccc-8840-1b5c6280aa41
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c17c79c6-f7d2-4dcb-a594-a35aa10d27d4
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c17c79c6-f7d2-4dcb-a594-a35aa10d27d4
index-b6e70955.js:297 🔄 Carregando progresso do ticket: a697b04d-6b67-4bb2-b2fa-58bfa84ba779
index-b6e70955.js:297 ✅ Progresso carregado para ticket: a697b04d-6b67-4bb2-b2fa-58bfa84ba779
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e1ac0a49-7b4a-4d12-a116-b076c73b183e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e1ac0a49-7b4a-4d12-a116-b076c73b183e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 6412edc9-4629-4b13-af00-7e120433b9e7
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 6412edc9-4629-4b13-af00-7e120433b9e7
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c4bc7e63-6cd9-40e7-8d50-92d4ad38970c
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c4bc7e63-6cd9-40e7-8d50-92d4ad38970c
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 7fb5fff4-3a29-4781-b2ed-0720134ff3ed
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 7fb5fff4-3a29-4781-b2ed-0720134ff3ed
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 1c6a0f5e-86ef-4b14-a682-6450fc614737
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 1c6a0f5e-86ef-4b14-a682-6450fc614737
index-b6e70955.js:297 🔄 Carregando progresso do ticket: ed4a66fc-0da6-4419-bc5d-36bd6d9fe36b
index-b6e70955.js:297 ✅ Progresso carregado para ticket: ed4a66fc-0da6-4419-bc5d-36bd6d9fe36b
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 8195dd51-f305-4b00-ac08-c650e59af721
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 8195dd51-f305-4b00-ac08-c650e59af721
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 4a3cb0b2-690e-4f3f-9235-4519b9dcc5c2
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 4a3cb0b2-690e-4f3f-9235-4519b9dcc5c2
index-b6e70955.js:297 🔄 Carregando progresso do ticket: aa1e9450-0d25-4095-b562-1bc5d85e698f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: aa1e9450-0d25-4095-b562-1bc5d85e698f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 7e5cb733-8164-4412-b887-09762880c366
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 7e5cb733-8164-4412-b887-09762880c366
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 91a7321e-70b6-424e-8d30-d554a81da4bc
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 91a7321e-70b6-424e-8d30-d554a81da4bc
index-b6e70955.js:297 🔄 Carregando progresso do ticket: d5cad3d2-863c-4f45-969b-5c4d4ed6de88
index-b6e70955.js:297 ✅ Progresso carregado para ticket: d5cad3d2-863c-4f45-969b-5c4d4ed6de88
index-b6e70955.js:297 🔄 Carregando progresso do ticket: d94a7888-ab56-45fc-9f09-571173e49e5a
index-b6e70955.js:297 ✅ Progresso carregado para ticket: d94a7888-ab56-45fc-9f09-571173e49e5a
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 4256cea7-b0ec-4019-bd07-e0820b6f1730
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 4256cea7-b0ec-4019-bd07-e0820b6f1730
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 55aea123-1e30-42f6-80de-17d482aa21aa
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 55aea123-1e30-42f6-80de-17d482aa21aa
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c3844238-9ead-4b64-af3e-364eedf46fef
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c3844238-9ead-4b64-af3e-364eedf46fef
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 908d7d74-4bae-44f4-9464-635637f098ca
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 908d7d74-4bae-44f4-9464-635637f098ca
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c9e288c3-1443-474b-90c4-e0b95c08208d
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c9e288c3-1443-474b-90c4-e0b95c08208d
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 27d3fda2-7a6f-4563-81b3-2887c4c1d956
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 27d3fda2-7a6f-4563-81b3-2887c4c1d956
index-b6e70955.js:297 🔄 Carregando progresso do ticket: ad48997c-4e06-4060-8348-264b3146153d
index-b6e70955.js:297 ✅ Progresso carregado para ticket: ad48997c-4e06-4060-8348-264b3146153d
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 344d9cc1-af13-4745-ba87-43f59464e7fb
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 344d9cc1-af13-4745-ba87-43f59464e7fb
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 633d3742-9fe9-4251-b009-4ebf0296c3d7
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 633d3742-9fe9-4251-b009-4ebf0296c3d7
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 0fe62e50-35d0-4e13-8a7b-afe16a283026
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 0fe62e50-35d0-4e13-8a7b-afe16a283026
index-b6e70955.js:297 🔄 Carregando progresso do ticket: e0aa0ca8-5178-4373-ac7e-819cdb55f094
index-b6e70955.js:297 ✅ Progresso carregado para ticket: e0aa0ca8-5178-4373-ac7e-819cdb55f094
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 67c4bf4c-cd0e-48a6-b88a-0855bd418c72
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 67c4bf4c-cd0e-48a6-b88a-0855bd418c72
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f2f9aca4-b402-47c8-9fb0-fa6c734e9c4f
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f2f9aca4-b402-47c8-9fb0-fa6c734e9c4f
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 255500ee-1088-432a-889e-6af744caf5e5
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 255500ee-1088-432a-889e-6af744caf5e5
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 94ed0dd9-612c-48ae-81fc-f5c8cf913dc5
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 94ed0dd9-612c-48ae-81fc-f5c8cf913dc5
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 5747b72b-8d2c-4520-aa83-5c915b5f32e3
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 5747b72b-8d2c-4520-aa83-5c915b5f32e3
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 584e4c10-687c-4216-9809-4d1d5d96d502
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 584e4c10-687c-4216-9809-4d1d5d96d502
index-b6e70955.js:297 🔄 Carregando progresso do ticket: c20318fb-fe78-402f-a4e7-867ac2c10fb9
index-b6e70955.js:297 ✅ Progresso carregado para ticket: c20318fb-fe78-402f-a4e7-867ac2c10fb9
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 44c3c3c2-0f13-4b4a-a218-3d621eccb42b
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 44c3c3c2-0f13-4b4a-a218-3d621eccb42b
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 4a3f8702-48e8-4424-aef8-beda6346da34
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 4a3f8702-48e8-4424-aef8-beda6346da34
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f002a8a4-d898-42f0-97bc-08b7ed2057ed
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f002a8a4-d898-42f0-97bc-08b7ed2057ed
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 9b407829-f75c-4ec7-9024-0c228f10029c
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 9b407829-f75c-4ec7-9024-0c228f10029c
index-b6e70955.js:297 🔄 Carregando progresso do ticket: f2d52321-4645-4b4d-9de1-8d3e69932021
index-b6e70955.js:297 ✅ Progresso carregado para ticket: f2d52321-4645-4b4d-9de1-8d3e69932021
index-b6e70955.js:297 🔄 Carregando progresso do ticket: a6639d4d-5a65-4429-872c-7ce3bf1cae0e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: a6639d4d-5a65-4429-872c-7ce3bf1cae0e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 64868750-27c7-47cf-91fa-ca690f7316ea
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 64868750-27c7-47cf-91fa-ca690f7316ea
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 665bedd0-af1f-47a8-97d1-cb2a7e150774
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 665bedd0-af1f-47a8-97d1-cb2a7e150774
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 8a62fdc6-f930-4ad5-a576-e388f8f51f2e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 8a62fdc6-f930-4ad5-a576-e388f8f51f2e
index-b6e70955.js:297 🔄 Carregando progresso do ticket: 11f0b093-9979-491c-bef7-d4f05c53a763
index-b6e70955.js:297 ✅ Progresso carregado para ticket: 11f0b093-9979-491c-bef7-d4f05c53a763
index-b6e70955.js:297 🔄 Carregando progresso do ticket: a67f02f0-b596-4a7a-8e64-d0c9f53a5a5e
index-b6e70955.js:297 ✅ Progresso carregado para ticket: a67f02f0-b596-4a7a-8e64-d0c9f53a5a5e
index-b6e70955.js:80 🔍 DEBUG - Axios Response Interceptor: {url: '/tickets', method: 'get', status: 200, statusText: '', data: Array(11)}
index-b6e70955.js:96 🔍 Resultado tickets cancelados: (11) [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
index-b6e70955.js:80 🔍 DEBUG - Axios Response Interceptor: {url: '/tickets/status/pending-payment', method: 'get', status: 200, statusText: '', data: Array(0)}
index-b6e70955.js:96 🔍 DEBUG - pendingPaymentQuery - Resultado: {total: 0, tickets: Array(0)}
index-b6e70955.js:80 🔍 DEBUG - Axios Response Interceptor: {url: '/tickets', method: 'get', status: 200, statusText: '', data: Array(17)}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/tickets/equipment/status?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/tickets/equipment/status', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:96 ❌ ERRO - equipmentService.getEquipmentStatus: Nt {message: 'Request failed with status code 404', name: 'AxiosError', code: 'ERR_BAD_REQUEST', config: {…}, request: XMLHttpRequest, …}
getEquipmentStatus @ index-b6e70955.js:96
await in getEquipmentStatus
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:297 🔍 DEBUG - safePendingPaymentTickets useMemo: {pendingPaymentTickets: Array(0), pendingPaymentTicketsLength: 0, result: Array(0), resultLength: 0}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/operation/equipment?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
list @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/operation/equipment', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
list @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/operation?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getOperation @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/operation', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getOperation @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 WebSocket connection to 'wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c' failed: 
(anonymous) @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:80
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ WebSocket - Erro na conexão: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 ❌ WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
(anonymous) @ index-b6e70955.js:80
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:96 🔌 WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
onError @ index-b6e70955.js:96
(anonymous) @ index-b6e70955.js:80
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 🔌 WebSocket - Conexão fechada 1006 
index-b6e70955.js:80 🔌 WebSocket fechado
index-b6e70955.js:96 🔌 WebSocket fechado
index-b6e70955.js:80 🔌 WebSocket - Tentativa de reconexão 1/5
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - URL: /tickets/equipment/status
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Params: {tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/equipment/status', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/operation/equipment', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/operation', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/operation?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getOperation @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/tickets/equipment/status?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/operation/equipment?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
list @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/operation/equipment', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
list @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/operation', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getOperation @ index-b6e70955.js:96
queryFn @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/tickets/equipment/status', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:96 ❌ ERRO - equipmentService.getEquipmentStatus: Nt {message: 'Request failed with status code 404', name: 'AxiosError', code: 'ERR_BAD_REQUEST', config: {…}, request: XMLHttpRequest, …}
getEquipmentStatus @ index-b6e70955.js:96
await in getEquipmentStatus
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:80 🔌 WebSocket - Conectando: wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:80 WebSocket connection to 'wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c' failed: 
(anonymous) @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 ❌ WebSocket - Erro na conexão: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 ❌ WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
(anonymous) @ index-b6e70955.js:80
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:96 🔌 WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
onError @ index-b6e70955.js:96
(anonymous) @ index-b6e70955.js:80
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 🔌 WebSocket - Conexão fechada 1006 
index-b6e70955.js:80 🔌 WebSocket fechado
index-b6e70955.js:96 🔌 WebSocket fechado
index-b6e70955.js:80 🔌 WebSocket - Tentativa de reconexão 2/5
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - URL: /tickets/equipment/status
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Params: {tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/equipment/status', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/tickets/equipment/status?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/tickets/equipment/status', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:96 ❌ ERRO - equipmentService.getEquipmentStatus: Nt {message: 'Request failed with status code 404', name: 'AxiosError', code: 'ERR_BAD_REQUEST', config: {…}, request: XMLHttpRequest, …}
getEquipmentStatus @ index-b6e70955.js:96
await in getEquipmentStatus
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - URL: /tickets/equipment/status
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Params: {tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/equipment/status', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/tickets/equipment/status?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/tickets/equipment/status', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:96 ❌ ERRO - equipmentService.getEquipmentStatus: Nt {message: 'Request failed with status code 404', name: 'AxiosError', code: 'ERR_BAD_REQUEST', config: {…}, request: XMLHttpRequest, …}
getEquipmentStatus @ index-b6e70955.js:96
await in getEquipmentStatus
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - URL: /tickets/equipment/status
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Params: {tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/equipment/status', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:80 🔌 WebSocket - Conectando: wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/tickets/equipment/status?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/tickets/equipment/status', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:96 ❌ ERRO - equipmentService.getEquipmentStatus: Nt {message: 'Request failed with status code 404', name: 'AxiosError', code: 'ERR_BAD_REQUEST', config: {…}, request: XMLHttpRequest, …}
getEquipmentStatus @ index-b6e70955.js:96
await in getEquipmentStatus
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:80 WebSocket connection to 'wss://recoverytruck-production.up.railway.app/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTUxMjIzMjd9.1xcXC-Qy8cqlRj4_vGbAA_eK2hSIZLoqyceqWIGx14c' failed: 
(anonymous) @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 ❌ WebSocket - Erro na conexão: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 ❌ WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
(anonymous) @ index-b6e70955.js:80
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:96 🔌 WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket, currentTarget: WebSocket, eventPhase: 2, …}
onError @ index-b6e70955.js:96
(anonymous) @ index-b6e70955.js:80
G.onerror @ index-b6e70955.js:80Understand this error
index-b6e70955.js:80 🔌 WebSocket - Conexão fechada 1006 
index-b6e70955.js:80 🔌 WebSocket fechado
index-b6e70955.js:96 🔌 WebSocket fechado
index-b6e70955.js:80 🔌 WebSocket - Tentativa de reconexão 3/5
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Iniciando requisição...
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - URL: /tickets/equipment/status
index-b6e70955.js:96 🔍 DEBUG - equipmentService.getEquipmentStatus - Params: {tenant_id: '7f02a566-2406-436d-b10d-90ecddd3fe2d'}
index-b6e70955.js:80 🔍 DEBUG - Axios Request Interceptor: {url: '/tickets/equipment/status', method: 'get', headers: _m, params: {…}, data: undefined}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:77  GET https://recoverytruck-production.up.railway.app/tickets/equipment/status?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d 404 (Not Found)
(anonymous) @ index-b6e70955.js:77
xhr @ index-b6e70955.js:77
tw @ index-b6e70955.js:79
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:80 ❌ ERRO - Axios Response Interceptor Error: {url: '/tickets/equipment/status', method: 'get', status: 404, statusText: '', data: {…}, …}
(anonymous) @ index-b6e70955.js:80
Promise.then
_request @ index-b6e70955.js:80
request @ index-b6e70955.js:79
Up.<computed> @ index-b6e70955.js:80
(anonymous) @ index-b6e70955.js:75
getEquipmentStatus @ index-b6e70955.js:96
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:96 ❌ ERRO - equipmentService.getEquipmentStatus: Nt {message: 'Request failed with status code 404', name: 'AxiosError', code: 'ERR_BAD_REQUEST', config: {…}, request: XMLHttpRequest, …}
getEquipmentStatus @ index-b6e70955.js:96
await in getEquipmentStatus
s @ index-b6e70955.js:67
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
setInterval
mg @ index-b6e70955.js:67
gg @ index-b6e70955.js:67
onQueryUpdate @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
batch @ index-b6e70955.js:67
$s @ index-b6e70955.js:67
l @ index-b6e70955.js:67
m @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
Promise.then
(anonymous) @ index-b6e70955.js:67
Promise.catch
b @ index-b6e70955.js:67
start @ index-b6e70955.js:67
fetch @ index-b6e70955.js:67
fd @ index-b6e70955.js:67
onSubscribe @ index-b6e70955.js:67
subscribe @ index-b6e70955.js:67
(anonymous) @ index-b6e70955.js:67
N4 @ index-b6e70955.js:38
rm @ index-b6e70955.js:40
Rc @ index-b6e70955.js:40
(anonymous) @ index-b6e70955.js:40
U @ index-b6e70955.js:25
F @ index-b6e70955.js:25Understand this error
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}
index-b6e70955.js:303 🔍 DEBUG - Tickets agrupados por cliente: {Gustavo Fugulin Soares da Silva: Array(9), Alec: Array(1), "Alex Quintans ": Array(131), Teste PWA: Array(1), EverGreen MKT: Array(3), …}