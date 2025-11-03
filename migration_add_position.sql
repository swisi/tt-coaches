-- Migration: Position-Feld zu coaching_experiences hinzufügen
-- Führen Sie dieses Skript in Ihrer MariaDB/MySQL Datenbank aus

ALTER TABLE coaching_experiences 
ADD COLUMN position VARCHAR(50) NULL 
AFTER team;

-- Index für Position (optional, aber kann die Performance verbessern)
CREATE INDEX idx_position ON coaching_experiences(position);
