-- Migration: Profilbild-Feld hinzufügen
-- Führen Sie dieses Skript in Ihrer MariaDB/MySQL Datenbank aus

-- Füge Profilbild-Feld hinzu
ALTER TABLE trainer_profiles 
ADD COLUMN profile_image_path VARCHAR(500) NULL 
AFTER last_name;

-- Optional: Wenn Sie möchten, dass die Lizenznummer vor first_name steht (Datenbank-Struktur)
-- Hinweis: Die Reihenfolge in der Datenbank beeinflusst nicht die Reihenfolge im Formular
-- Diese Änderung ist optional und kann Probleme verursachen, wenn bereits Daten vorhanden sind
-- ALTER TABLE trainer_profiles MODIFY COLUMN license_number VARCHAR(50) NULL AFTER user_id;

