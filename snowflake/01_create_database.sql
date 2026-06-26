-- =================================================================
-- SCRIPT 1: CRÉATION DE LA BASE DE DONNÉES SNOWFLAKE
-- Démonstration Retail Analytics avec Agent IA
-- =================================================================

-- Utilisation du rôle administrateur
USE ROLE ACCOUNTADMIN;

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS RETAIL_DEMO
    COMMENT = 'Base de données pour la démonstration retail avec agents IA';

-- Création du schéma principal
CREATE SCHEMA IF NOT EXISTS RETAIL_DEMO.MAIN
    COMMENT = 'Schéma principal pour les données retail';

-- Création du schéma pour les données agrégées
CREATE SCHEMA IF NOT EXISTS RETAIL_DEMO.ANALYTICS
    COMMENT = 'Schéma pour les vues et données agrégées';

-- Création du warehouse pour les analyses
CREATE WAREHOUSE IF NOT EXISTS RETAIL_WH
    WITH WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    SCALING_POLICY = 'STANDARD'
    COMMENT = 'Warehouse pour les analyses retail';

-- Utilisation du contexte
USE WAREHOUSE RETAIL_WH;
USE DATABASE RETAIL_DEMO;
USE SCHEMA MAIN;

-- Création d'un utilisateur pour les agents IA
CREATE USER IF NOT EXISTS AGENT_USER 
    PASSWORD = 'AgentDemo2024!'
    DEFAULT_ROLE = 'PUBLIC'
    DEFAULT_WAREHOUSE = 'RETAIL_WH'
    DEFAULT_NAMESPACE = 'RETAIL_DEMO.MAIN'
    COMMENT = 'Utilisateur pour les agents IA retail';

-- Création d'un rôle spécifique pour les agents
CREATE ROLE IF NOT EXISTS RETAIL_ANALYST;

-- Attribution des permissions
GRANT USAGE ON WAREHOUSE RETAIL_WH TO ROLE RETAIL_ANALYST;
GRANT USAGE ON DATABASE RETAIL_DEMO TO ROLE RETAIL_ANALYST;
GRANT USAGE ON SCHEMA RETAIL_DEMO.MAIN TO ROLE RETAIL_ANALYST;
GRANT USAGE ON SCHEMA RETAIL_DEMO.ANALYTICS TO ROLE RETAIL_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA RETAIL_DEMO.MAIN TO ROLE RETAIL_ANALYST;
GRANT SELECT ON ALL VIEWS IN SCHEMA RETAIL_DEMO.ANALYTICS TO ROLE RETAIL_ANALYST;
GRANT SELECT ON FUTURE TABLES IN SCHEMA RETAIL_DEMO.MAIN TO ROLE RETAIL_ANALYST;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA RETAIL_DEMO.ANALYTICS TO ROLE RETAIL_ANALYST;

-- Attribution du rôle à l'utilisateur agent
GRANT ROLE RETAIL_ANALYST TO USER AGENT_USER;

-- Configuration des paramètres de session
ALTER SESSION SET TIMESTAMP_OUTPUT_FORMAT = 'YYYY-MM-DD HH24:MI:SS';
ALTER SESSION SET DATE_OUTPUT_FORMAT = 'YYYY-MM-DD';
ALTER SESSION SET TIME_ZONE = 'Europe/Paris';

-- Création des formats de fichier pour l'import
CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    ESCAPE = 'NONE'
    ESCAPE_UNENCLOSED_FIELD = '\134'
    DATE_FORMAT = 'YYYY-MM-DD'
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
    NULL_IF = ('NULL', 'null', '', '\\N');

CREATE FILE FORMAT IF NOT EXISTS JSON_FORMAT
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE
    COMMENT = 'Format JSON pour l\'import de données retail';

-- Création des stages pour l'import de données
CREATE STAGE IF NOT EXISTS RETAIL_STAGE
    FILE_FORMAT = CSV_FORMAT
    COMMENT = 'Stage pour l\'upload des fichiers de données retail';

-- Messages de confirmation
SELECT 'Base de données RETAIL_DEMO créée avec succès' AS STATUS;
SELECT 'Warehouse RETAIL_WH configuré' AS STATUS;
SELECT 'Utilisateur AGENT_USER et rôle RETAIL_ANALYST créés' AS STATUS;
SELECT 'Formats de fichier et stages configurés' AS STATUS;

-- Vérification de la configuration
SHOW DATABASES LIKE 'RETAIL_DEMO';
SHOW SCHEMAS IN DATABASE RETAIL_DEMO;
SHOW WAREHOUSES LIKE 'RETAIL_WH';
SHOW USERS LIKE 'AGENT_USER';
SHOW ROLES LIKE 'RETAIL_ANALYST';