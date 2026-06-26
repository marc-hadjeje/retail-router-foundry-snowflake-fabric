# 🤖 Demo Snowflake Agents IA - Retail Analytics

## 🎯 Objectif de la Démonstration

Cette démonstration présente l'utilisation **d'agents IA conversationnels** pour l'analyse de données retail avec :
- **🧠 Agent IA Snowflake** : Analyse intelligente via Cortex (Llama3.1-70b) + données tabulaires
- **📊 Snowflake Intelligence** : Interface conversationnelle web intégrée
- **🏗️ Agent Fabric Data** : Analyse des données agrégées  
- **📈 Power BI** : Rapports et dashboards interactifs

## 📊 Modèle de Données Retail

Le modèle comprend 6 tables principales avec **données synthétiques réalistes** :
- `CUSTOMERS` : 10,000 clients français avec géolocalisation
- `PRODUCTS` : 2,000 produits dans 30 catégories  
- `CATEGORIES` : Catégories localisées en français
- `STORES` : 100 magasins à travers la France
- `ORDERS` : 50,000 commandes avec historique temporel
- `ORDER_ITEMS` : 325,000+ lignes de commande détaillées

## 🚀 Guide de Déploiement (4 étapes)

### **1. Génération des données**
```bash
cd data_generation
python generate_retail_data.py --size medium --format both
```

### **2. Setup Snowflake Database**
```sql
-- Exécuter dans l'ordre :
snowflake/01_create_database.sql      # Création base + warehouse
snowflake/02_create_tables.sql        # Structure tables + vues analytiques
```
*Puis importer les CSV via l'interface web Snowflake*

### **3. Activation des Agents IA + MCP** 
```sql  
snowflake/99_nettoyage_complet.sql    # 🧠 Agents IA + fonctions de backup
snowflake/20_agent_intelligence.sql   # 🤖 Agent Snowflake Intelligence
snowflake/21_foundry_integration.sql  # 🤖 Serveur MCP (Managed)
```

### **4. Test du Serveur MCP**
```bash
# Tester le serveur MCP et ses outils
python test_mcp_server.py
```

### **4. Utilisation Interface Intelligence**
1. **Snowflake Web** → **Intelligence** 🤖 → **"Agents"**
2. **Sélectionner** → **"RETAIL_CLIENT_ADVISOR"** 
3. **Poser vos questions** en français naturel !

## 💬 Exemples d'Utilisation Agent IA

### **🎯 Questions Stratégiques**
```
• "Analyse mes clients VIP et propose une stratégie de fidélisation"
• "Comment augmenter le panier moyen de mes clients de 25-35 ans ?"  
• "Quels clients risquent de partir et comment les retenir ?"
• "Programme fidélité pour les gros acheteurs - ROI estimé ?"
```

### **📊 Analyses Opérationnelles**  
```
• "Top 10 clients VIP cette année avec leurs habitudes d'achat"
• "Performance des magasins parisiens vs province"
• "Produits bestsellers et actions marketing recommandées"
• "Segmentation client pour campagne de Noël"
```

## 📁 Structure Finale (Après Nettoyage)

```
demo_snow_agents/
├── 📂 snowflake/              # 🎯 Scripts SQL essentiels
│   ├── 01_create_database.sql     # Setup base de données
│   ├── 02_create_tables.sql       # Structure + vues analytiques  
│   ├── 99_nettoyage_complet.sql   # 🧠 AGENTS IA PRINCIPAUX
│   ├── 20_agent_intelligence.sql  # 🤖 Interface Intelligence
│   └── 21_foundry_integration.sql # 🤖 Serveur MCP Snowflake (Managed)
├── 📂 data_generation/         # Générateur données + exports CSV/JSON
├── 📂 agents/                  # Configurations Fabric + Snowflake
├── 📂 powerbi/                 # Configuration modèle Power BI
├── 📂 fabric/                  # Scripts agrégation Fabric  
├── 📂 docs/                    # 📖 Guides d'utilisation détaillés
│   ├── guide_snowflake_intelligence.md  # Interface conversationnelle
│   ├── guide_partage_foundry.md         # 🌉 NOUVEAU ! Intégration entreprise
│   ├── demo_scenarios.md                # Scénarios business  
│   └── ETAT_DOCUMENTATION.md           # État documentation
└── 📂 semantic_model/          # Modèle sémantique YAML
```

## 🔧 Prérequis Techniques

- **Python 3.10+** avec packages : `faker`, `pandas`, `snowflake-connector-python`
- **Compte Snowflake** avec Cortex AI activé
- **Interface Snowflake Intelligence** (inclus)
- **Microsoft Fabric** (optionnel pour agent agrégé)
- **Power BI Desktop** (optionnel pour rapports)

## 🚀 Démarrage Rapide (5 minutes)

### **Étape 1 : Préparer l'environnement**
```bash  
pip install -r requirements.txt
python test_connection.py  # Vérifier connexion Snowflake
```

### **Étape 2 : Générer et charger les données**
```bash
cd data_generation  
python generate_retail_data.py --size medium --format both
# Puis importer les CSV via interface Snowflake Web
```

### **Étape 3 : Créer les agents IA**
```sql
-- Dans Snowflake Web Interface :
-- 1. Exécuter 01_create_database.sql
-- 2. Exécuter 02_create_tables.sql  
-- 3. Importer les CSV depuis data_generation/data_output/
-- 4. Exécuter 99_nettoyage_complet.sql (agents IA)
-- 5. Exécuter 20_agent_intelligence.sql (interface web)
```

### **Étape 4 : Tester le serveur MCP** 
```bash
# Valider le serveur MCP et ses outils
python test_mcp_server.py
```

### **Étape 5 : Utiliser l'agent conversationnel** 
1. **Snowflake Web** → **Intelligence** 🤖
2. **Agents** → **RETAIL_CLIENT_ADVISOR**  
3. Posez vos questions en français !

## 🎯 Agents IA Disponibles

### **🧠 Agent IA Contextuel (AGENT_IA_CLIENTS)**
- **Moteur** : Snowflake Cortex + Llama3.1-70b
- **Fonction** : Analyse contextuelle intelligente  
- **Usage** : `SELECT AGENT_IA_CLIENTS('Question stratégique');`
- **Avantage** : Comprend le contexte, recommandations personnalisées

### **🤖 Agent Données Tabulaires (AGENT_CLIENTS)**  
- **Moteur** : SQL optimisé sans IA
- **Fonction** : Données structurées pour Power BI
- **Usage** : `SELECT * FROM TABLE(AGENT_CLIENTS('VIP'));`
- **Avantage** : Performance rapide, format tabulaire

### **💬 Agent Intelligence Web (RETAIL_CLIENT_ADVISOR)**
- **Moteur** : Interface Snowflake Intelligence 
- **Fonction** : Conversation naturelle en français
- **Usage** : Interface web conversationnelle
- **Avantage** : Accessible à toute l'équipe business

## 🛠️ Scripts de Test et Validation

```bash
# Test connexion Snowflake
python test_connection.py  

# Validation données générées
python test_data.py

# 🤖 Test serveur MCP (NOUVEAU !)  
python test_mcp_server.py

# Vérifier les données importées (via Snowflake Web)
SELECT COUNT(*) FROM CUSTOMERS;  -- Devrait retourner 10,000
SELECT COUNT(*) FROM ORDERS;     -- Devrait retourner 50,000  
SELECT COUNT(*) FROM ORDER_ITEMS; -- Devrait retourner 325,800+
```

## � Partage et Intégration Entreprise

### **🤖 Serveur MCP Snowflake (Managed)**
Vos agents Snowflake sont exposés comme outils MCP directement hébergés dans Snowflake :

```sql
-- Serveur MCP créé dans Snowflake :
snowflake/21_foundry_integration.sql     # CREATE MCP SERVER retail_mcp_server
```

### **�️ Outils MCP Exposés :**
- **🤖 snowflake-retail-agent** : Agent Intelligence principal (Cortex AI)
- **📊 retail-client-analysis** : Analyse clients via Cortex  
- **🔄 retail-backup-agent** : Agent SQL backup (haute disponibilité)
- **🛍️ retail-products-agent** : Analyse produits et bestsellers
- **🏪 retail-stores-agent** : Performance magasins
- **📈 retail-executive-agent** : Dashboard KPIs direction

### **✨ Avantages Serveur MCP Managed :**
- ✅ **Hébergé dans Snowflake** : Zero infrastructure externe
- ✅ **Protocol MCP standard** : Compatible Claude, GPT, autres LLMs
- ✅ **Performance optimisée** : Accès direct aux données
- ✅ **Sécurité intégrée** : RBAC Snowflake natif
- ✅ **Scaling automatique** : Géré par Snowflake
- ✅ **Maintenance zero** : Pas de serveur à maintenir

## 📖 Documentation Complète

- **[Guide Snowflake Intelligence](docs/guide_snowflake_intelligence.md)** - Utilisation interface conversationnelle
- **[Guide Partage Foundry](docs/guide_partage_foundry.md)** - Options de partage avancées  
- **[Scénarios Demo](docs/demo_scenarios.md)** - Exemples d'utilisation métier
- **[État Documentation](docs/ETAT_DOCUMENTATION.md)** - Statut mise à jour

## ⚡ Avantages de Cette Architecture

- **✅ Hybrid AI** : IA conversationnelle + backup SQL garanti
- **✅ Données réalistes** : 10K clients, 50K commandes, géolocalisation France  
- **✅ Interface intuitive** : Conversation naturelle en français
- **✅ Performance** : Requêtes optimisées + clustering Snowflake
- **✅ Évolutif** : Facile d'ajouter des agents spécialisés  
- **✅ Business ready** : Recommandations chiffrées actionnables

---

## 🎉 Votre Démo est Prête !

Une fois les agents déployés, vous pouvez **immédiatement** commencer à poser des questions business en français dans l'interface Snowflake Intelligence. L'agent comprendra le contexte et fournira des analyses chiffrées avec des plans d'action concrets ! 🚀