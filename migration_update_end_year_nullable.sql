-- Migration: Endjahr optional machen für laufende Coaching-Erfahrungen
-- Führen Sie dieses Skript aus, wenn die Tabelle coaching_experiences bereits existiert

ALTER TABLE coaching_experiences 
MODIFY COLUMN end_year INT NULL;

