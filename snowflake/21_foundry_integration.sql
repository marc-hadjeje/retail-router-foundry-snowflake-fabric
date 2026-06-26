-- ===============================================
-- 🤖 SERVEUR MCP SNOWFLAKE - VERSION MANAGED
-- Exposition des agents Snowflake comme outils MCP
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE RETAIL_DEMO;
USE SCHEMA PUBLIC;
USE WAREHOUSE COMPUTE_WH;

-- ===============================================
-- 🤖 SERVEUR MCP GÉRÉ POUR AGENTS RETAIL
-- ===============================================

-- Créer serveur MCP managed avec vos informations
CREATE OR REPLACE MCP SERVER retail_mcp_server
FROM SPECIFICATION $$
tools:
  - name: "snowflake-retail-agent"
    type: "CORTEX_AGENT_RUN"
    identifier: "RETAIL_DEMO.PUBLIC.RETAIL_CLIENT_ADVISOR"
    description: "Agent IA retail francais pour analyse clients, ventes et recommandations business"
    title: "Agent Retail Snowflake Intelligence"

  - name: "retail-client-analysis"
    type: "GENERIC"
    identifier: "RETAIL_DEMO.PUBLIC.AGENT_IA_CLIENTS"
    description: "Analyse intelligente des clients retail avec Cortex AI"
    title: "Analyse Clients IA"
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          question:
            type: "string"
            description: "Question ou demande d analyse client"

  - name: "retail-backup-agent"
    type: "GENERIC"
    identifier: "RETAIL_DEMO.PUBLIC.AGENT_CLIENTS"
    description: "Agent de backup SQL pour questions clients (fallback si Cortex indisponible)"
    title: "Agent Clients Backup"
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          question:
            type: "string"
            description: "Type d analyse souhaitee (VIP, fidelisation, segmentation)"
$$;

-- ===============================================
-- 🔐 PERMISSIONS POUR SERVEUR MCP
-- ===============================================

-- Créer un rôle spécifique pour MCP
CREATE OR REPLACE ROLE MCP_RETAIL_ROLE;

-- Permissions minimales nécessaires
GRANT USAGE ON DATABASE RETAIL_DEMO TO ROLE MCP_RETAIL_ROLE;
GRANT USAGE ON SCHEMA RETAIL_DEMO.PUBLIC TO ROLE MCP_RETAIL_ROLE;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE MCP_RETAIL_ROLE;

-- Accès aux agents exposés via MCP
GRANT USAGE ON AGENT RETAIL_DEMO.PUBLIC.RETAIL_CLIENT_ADVISOR TO ROLE MCP_RETAIL_ROLE;
GRANT USAGE ON PROCEDURE RETAIL_DEMO.PUBLIC.AGENT_IA_CLIENTS(STRING) TO ROLE MCP_RETAIL_ROLE;
GRANT USAGE ON PROCEDURE RETAIL_DEMO.PUBLIC.AGENT_CLIENTS(STRING) TO ROLE MCP_RETAIL_ROLE;

-- Accès aux tables (lecture seule pour contexte)
GRANT SELECT ON ALL TABLES IN SCHEMA RETAIL_DEMO.PUBLIC TO ROLE MCP_RETAIL_ROLE;

-- ===============================================
-- 🧪 VALIDATION SERVEUR MCP
-- ===============================================

-- Vérifier la création du serveur MCP
SHOW MCP SERVERS LIKE 'retail_mcp_server';

-- Décrire le serveur MCP et ses outils
DESCRIBE MCP SERVER retail_mcp_server;



-- ===============================================
-- 📋 UTILISATION DU SERVEUR MCP
-- ===============================================

/*
🤖 SERVEUR MCP SNOWFLAKE CONFIGURÉ !

✅ SERVEUR MCP CRÉÉ: retail_mcp_server (MANAGED)

🛠️ OUTILS EXPOSÉS VIA MCP:
1. snowflake-retail-agent    - Agent Intelligence principal (Cortex AI)
2. retail-client-analysis    - Fonction Cortex analyse clients  
3. retail-backup-agent       - Agent SQL backup (haute dispo)

🔗 CONNEXION MCP:
- **Type**: Serveur managed Snowflake
- **Endpoint**: `https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server`
- **URL Pattern**: `https://{account_URL}/api/v2/databases/{database}/schemas/{schema}/mcp-servers/{name}`
- **Auth**: Via rôle MCP_RETAIL_ROLE + credentials Snowflake
- **Protocol**: MCP standard (JSON-RPC over HTTPS)

📡 OBTENIR L'ENDPOINT:
```sql
-- Commandes pour récupérer l'endpoint MCP :
SELECT SYSTEM$GET_MCP_SERVER_ENDPOINT('retail_mcp_server') AS endpoint;
SHOW MCP SERVER ENDPOINTS LIKE 'retail_mcp_server';
```

💡 UTILISATION:
Les modèles IA (Claude, GPT, etc.) peuvent utiliser ces outils via:
- **MCP Client** configuré avec ce serveur
- **Appels JSON-RPC** vers les outils exposés  
- **Contexte automatique** depuis les tables retail

🎯 EXEMPLE APPEL MCP:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call", 
  "params": {
    "name": "snowflake-retail-agent",
    "arguments": {
      "question": "Analysez les tendances ventes Q1 2026"
    }
  }
}

🔧 CONFIGURATION CLIENT MCP:
```json
{
  "mcpServers": {
    "snowflake-retail": {
      "command": "mcp-client",
      "args": [
        "--endpoint", "https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server",
        "--auth", "snowflake",
        "--role", "MCP_RETAIL_ROLE",
        "--warehouse", "COMPUTE_WH"
      ]
    }
  }
}
```

🚀 AVANTAGES SERVEUR MANAGED:
✅ Configuration automatique par Snowflake
✅ Scaling et performance optimisés
✅ Sécurité enterprise intégrée  
✅ Monitoring et logs centralisés
✅ Maintenance zero pour l'équipe
✅ Intégration native avec Cortex AI

VOTRE SERVEUR MCP EST PRÊT POUR LES MODÈLES IA ! 🎉
*/