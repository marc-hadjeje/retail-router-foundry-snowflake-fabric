# 🤖 Guide d'utilisation Snowflake Intelligence

## **✅ ÉTAPES POUR EXPOSER VOTRE AGENT**

### **1. Exécuter le script de configuration**
```sql
-- Copiez-collez le contenu de 20_agent_intelligence.sql dans Snowflake
-- Exécutez tout le script pour créer l'agent RETAIL_CLIENT_ADVISOR
```

### **2. Accéder à l'interface Intelligence**

1. **Dans Snowflake Web Interface:**
   - Cliquez sur l'icône **"Intelligence"** 🤖 dans le menu de gauche
   - Ou allez dans **"Data"** → **"Intelligence"**

2. **Sélectionner votre agent:**
   - Cliquez sur **"Agents"**
   - Trouvez **"RETAIL_CLIENT_ADVISOR"**
   - Cliquez pour ouvrir la conversation

### **3. Commencer à utiliser l'agent**

## **🎯 EXEMPLES DE QUESTIONS À POSER**

### **Questions stratégiques:**
```
• "Analyse mes clients VIP et propose une stratégie de fidélisation"
• "Comment augmenter le panier moyen de 20% ?"
• "Quels clients risquent de partir et comment les retenir ?"
• "Stratégie pour conquérir les clients de 25-35 ans"
```

### **Questions opérationnelles:**
```
• "Qui sont mes 10 meilleurs clients cette année ?"
• "Programme de fidélité pour les gros acheteurs"
• "Actions pour réactiver les clients inactifs"
• "Segmentation client pour campagne marketing"
```

### **Questions d'analyse:**
```
• "Profil type de mes clients VIP Premium"
• "Différences entre clients Gold et Premium"
• "Tendances d'achat par segment client"
• "ROI potentiel d'un programme VIP exclusif"
```

## **💡 FONCTIONNALITÉS DISPONIBLES**

### **🧠 Intelligence conversationnelle:**
- ✅ Conversation naturelle en français
- ✅ Contexte maintenu entre questions  
- ✅ Clarifications automatiques si besoin
- ✅ Recommandations personnalisées

### **📊 Accès aux données:**
- ✅ Données temps réel (10K clients, 50K commandes)
- ✅ Segmentation automatique VIP
- ✅ Métriques business calculées à la volée
- ✅ Historique et tendances

### **🎯 Réponses business:**
- ✅ Actions concrètes et chiffrées
- ✅ Plans d'action prioritaires  
- ✅ Estimations de ROI
- ✅ KPIs de suivi recommandés

## **🔧 UTILISATION AVANCÉE**

### **Via SQL (pour intégrations):**
```sql
SELECT SNOWFLAKE.INTELLIGENCE.CHAT_WITH_AGENT(
    'RETAIL_CLIENT_ADVISOR',
    'Analyse complète de mes clients VIP avec plan d''action 6 mois'
) as reponse_agent;
```

### **Intégration dans applications:**
```python
# Via Snowflake Python Connector
cursor.execute("""
    SELECT SNOWFLAKE.INTELLIGENCE.CHAT_WITH_AGENT(
        'RETAIL_CLIENT_ADVISOR',
        %s
    )
""", (question_utilisateur,))
```

## **📈 CAS D'USAGE RECOMMANDÉS**

### **Pour le Marketing:**
- Segmentation client avancée
- Campagnes personnalisées VIP
- Analyse comportementale
- Prédiction de churn

### **Pour le Commercial:** 
- Identification prospects prioritaires
- Stratégies up-sell/cross-sell
- Programmes fidélisation
- Optimisation panier moyen

### **Pour la Direction:**
- KPIs client stratégiques  
- Plans de croissance chiffrés
- Analyse de la valeur client
- Priorisation investissements

## **⚙️ CONFIGURATION ENTREPRISE**

### **Permissions d'accès:**
```sql
-- Limiter l'accès à certains rôles
REVOKE USAGE ON AGENT RETAIL_CLIENT_ADVISOR FROM ROLE PUBLIC;
GRANT USAGE ON AGENT RETAIL_CLIENT_ADVISOR TO ROLE MARKETING_TEAM;
GRANT USAGE ON AGENT RETAIL_CLIENT_ADVISOR TO ROLE SALES_TEAM;
```

### **Monitoring et logs:**
```sql
-- Voir l'historique des conversations
SELECT * FROM SNOWFLAKE.INTELLIGENCE.AGENT_CONVERSATIONS 
WHERE AGENT_NAME = 'RETAIL_CLIENT_ADVISOR'
ORDER BY CREATED_AT DESC;
```

## **🚀 VOTRE AGENT EST PRÊT !**

1. **Exécutez** le script `20_agent_intelligence.sql`
2. **Ouvrez** l'interface Intelligence dans Snowflake  
3. **Sélectionnez** RETAIL_CLIENT_ADVISOR
4. **Commencez** à poser vos questions !

L'agent vous donnera des analyses intelligentes avec vos vraies données clients ! 🎉