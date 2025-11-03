-- migration_make_role_id_optional.sql
-- Macht role_id optional, da Rollen jetzt über Flags verwaltet werden

ALTER TABLE users 
MODIFY COLUMN role_id INT NULL;

-- Kommentar hinzufügen
ALTER TABLE users 
MODIFY COLUMN role_id INT NULL COMMENT 'Optional: Nur noch für Rückwärtskompatibilität. Rollen werden jetzt über Flags (is_superadmin, is_admin, is_coach) verwaltet.';

