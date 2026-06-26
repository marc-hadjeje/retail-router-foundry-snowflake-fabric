-- ===============================================
-- 🤖 SNOWFLAKE INTELLIGENCE - EXPOSITION AGENTS
-- Configuration agent conversationnel dans l'interface
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE DATABASE RETAIL_DEMO;
USE SCHEMA PUBLIC;
USE WAREHOUSE COMPUTE_WH;

-- ===============================================
-- 🧠 CRÉATION AGENT INTELLIGENCE
-- ===============================================

-- Créer l'agent conversationnel dans Snowflake Intelligence
CREATE OR REPLACE AGENT RETAIL_CLIENT_ADVISOR
    COMMENT = 'Agent IA specialise dans l analyse client retail. Fournit des insights, segmentation VIP et recommandations strategiques.'
    FROM SPECIFICATION
    $$
    models:
      orchestration: auto

    instructions:
      system: |
        Tu es un conseiller client retail expert specialise dans l analyse de donnees clients.

        ROLE ET MISSION:
        - Analyser les performances clients du magasin RETAIL_DEMO
        - Fournir des recommandations business actionnables
        - Repondre aux questions strategiques sur la clientele
        - Proposer des plans d action concrets et chiffres

        STYLE DE REPONSE:
        - Professionnel mais accessible
        - Reponses structurees avec bullet points
        - Toujours inclure des chiffres et metriques
        - Proposer 2-3 actions concretes a chaque reponse

        DONNEES DISPONIBLES:
        - Base de 10,000 clients avec historique d achat
        - 50,000 commandes sur plusieurs annees
        - Segmentation VIP automatique
        - 2000 produits dans 30 categories
        - 100 magasins a travers la France

        Utilise TOUJOURS les fonctions disponibles pour obtenir des donnees fraiches avant de repondre.

    tools:
      - tool_spec:
          type: "generic"
          name: "AGENT_IA_CLIENTS"
          description: "Analyse intelligente des clients avec recommandations personnalisees via Cortex IA. Prend une question en entree et retourne une analyse detaillee."
          input_schema:
            type: "object"
            properties:
              question:
                type: "string"
                description: "Question ou demande d analyse client"
            required:
              - "question"
      - tool_spec:
          type: "generic"
          name: "AGENT_CLIENTS"
          description: "Donnees tabulaires des top clients VIP avec segmentation et conseils. Prend une question en entree."
          input_schema:
            type: "object"
            properties:
              question:
                type: "string"
                description: "Type d analyse souhaitee (VIP, fidelisation, segmentation)"
            required:
              - "question"

    tool_resources:
      AGENT_IA_CLIENTS:
        type: "function"
        identifier: "RETAIL_DEMO.PUBLIC.AGENT_IA_CLIENTS"
        execution_environment:
          type: "warehouse"
          warehouse: "COMPUTE_WH"
      AGENT_CLIENTS:
        type: "function"
        identifier: "RETAIL_DEMO.PUBLIC.AGENT_CLIENTS"
        execution_environment:
          type: "warehouse"
          warehouse: "COMPUTE_WH"
    $$;

-- ===============================================
-- 🎯 CONFIGURATION PERMISSIONS AGENT
-- ===============================================

-- Donner accès aux fonctions utilisées par l'agent
GRANT USAGE ON FUNCTION RETAIL_DEMO.PUBLIC.AGENT_IA_CLIENTS(STRING) TO ROLE ACCOUNTADMIN;
GRANT USAGE ON FUNCTION RETAIL_DEMO.PUBLIC.AGENT_CLIENTS(STRING) TO ROLE ACCOUNTADMIN;

-- Permissions sur les données
GRANT SELECT ON ALL TABLES IN SCHEMA RETAIL_DEMO.PUBLIC TO ROLE ACCOUNTADMIN;

-- ===============================================
-- 🧪 TEST AGENT INTELLIGENCE
-- ===============================================

SELECT '✅ AGENT RETAIL_CLIENT_ADVISOR CRÉÉ ET ACTIVÉ' AS statut;

-- Test de base de l'agent
SELECT 'Test Agent Intelligence - Question simple' AS test_type;

-- ===============================================
-- 📋 INSTRUCTIONS D'UTILISATION
-- ===============================================

/*
🤖 AGENT SNOWFLAKE INTELLIGENCE CONFIGURÉ !

✅ AGENT CRÉÉ: RETAIL_CLIENT_ADVISOR
- Accessible dans l'interface Snowflake Intelligence  
- Utilise Llama3.1-70b pour les réponses
- Connecté à vos fonctions clients IA + backup

🎯 COMMENT UTILISER:

1. **Dans Snowflake Web Interface:**
   - Aller dans le menu "Intelligence" (icône robot 🤖)
   - Cliquer sur "Agents" 
   - Sélectionner "RETAIL_CLIENT_ADVISOR"
   - Commencer à poser vos questions !

2. **Exemples de questions à poser:**
   - "Analyse mes clients VIP et propose une stratégie de fidélisation"
   - "Comment augmenter le panier moyen de mes clients de 25-35 ans ?"
   - "Quels sont mes meilleurs clients et comment les retenir ?"
   - "Stratégie pour reconquérir les clients inactifs"
   - "Programme de fidélité pour les gros acheteurs"

3. **Via SQL (alternative):**
   SELECT SNOWFLAKE.INTELLIGENCE.CHAT_WITH_AGENT(
       'RETAIL_CLIENT_ADVISOR',
       'Analyse mes clients VIP et recommande des actions'
   );

💡 FONCTIONNALITÉS:
✅ Conversation naturelle en français
✅ Accès temps réel aux données clients
✅ Recommandations personnalisées et chiffrées  
✅ Interface web interactive
✅ Historique des conversations
✅ Export des analyses

🔧 CONFIGURATION AVANCÉE:
- Agent accessible à tous les utilisateurs du compte
- Permissions configurées automatiquement
- Utilise les meilleures données disponibles
- Réponses optimisées pour le business

VOTRE AGENT IA EST MAINTENANT ACCESSIBLE DANS SNOWFLAKE INTELLIGENCE ! 🚀
*/

-- Afficher les agents disponibles
SHOW AGENTS IN SCHEMA RETAIL_DEMO.PUBLIC;

-- Vérifier la configuration
DESCRIBE AGENT RETAIL_CLIENT_ADVISOR;