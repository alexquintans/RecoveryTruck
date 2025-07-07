-- Seed de equipamentos para o sistema
INSERT INTO equipments (id, tenant_id, type, identifier, location, status) VALUES
(gen_random_uuid(), 'e216fbd5-4c40-4058-806d-8fb3355fe334', 'totem', 'Banheira de Gelo 1', 'Sala 1', 'online'),
(gen_random_uuid(), 'e216fbd5-4c40-4058-806d-8fb3355fe334', 'totem', 'Banheira de Gelo 2', 'Sala 1', 'online'),
(gen_random_uuid(), 'e216fbd5-4c40-4058-806d-8fb3355fe334', 'totem', 'Banheira de Gelo 3', 'Sala 1', 'online'),
(gen_random_uuid(), 'e216fbd5-4c40-4058-806d-8fb3355fe334', 'panel', 'Bota de Compressão 1', 'Sala 2', 'online'),
(gen_random_uuid(), 'e216fbd5-4c40-4058-806d-8fb3355fe334', 'panel', 'Bota de Compressão 2', 'Sala 2', 'online'),
(gen_random_uuid(), 'e216fbd5-4c40-4058-806d-8fb3355fe334', 'panel', 'Bota de Compressão 3', 'Sala 2', 'online'); 