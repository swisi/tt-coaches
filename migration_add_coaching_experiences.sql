-- Migration: Coaching-Erfahrungen Tabelle hinzufügen
-- Führen Sie dieses Skript in Ihrer MariaDB/MySQL Datenbank aus

CREATE TABLE IF NOT EXISTS coaching_experiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trainer_profile_id INT NOT NULL,
    start_year INT NOT NULL,
    end_year INT NULL,  -- NULL für laufende Erfahrungen
    coaching_role VARCHAR(50) NOT NULL,
    team VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_profile_id) REFERENCES trainer_profiles(id) ON DELETE CASCADE,
    INDEX idx_trainer_profile (trainer_profile_id),
    INDEX idx_years (end_year, start_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

