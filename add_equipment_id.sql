-- Adicionar coluna equipment_id na tabela tickets
ALTER TABLE tickets ADD COLUMN equipment_id UUID REFERENCES equipments(id);
 
-- Criar índice para melhor performance
CREATE INDEX ix_tickets_equipment_id ON tickets(equipment_id); 