-- migration_remove_role_id.sql
-- Entfernt die role_id Spalte aus der users Tabelle, da Rollen jetzt über Flags verwaltet werden

ALTER TABLE users 
DROP FOREIGN KEY IF EXISTS users_ibfk_1;

ALTER TABLE users 
DROP COLUMN IF EXISTS role_id;

