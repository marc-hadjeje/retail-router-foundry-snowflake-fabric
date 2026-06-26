"""
🌉 Test d'Intégration Foundry Agent Framework
===========================================
Script de test pour valider l'intégration entre Snowflake et Microsoft Foundry.

Prérequis :
- Agent Snowflake déployé (99_nettoyage_complet.sql)
- Bridge Foundry configuré (21_foundry_integration.sql)
- Foundry Agent Framework installé

Usage :
    python test_foundry_integration.py --mode local    # Test local
    python test_foundry_integration.py --mode foundry  # Test Foundry complet
"""

import asyncio
import json
import os
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Simuler les imports Foundry (à remplacer par vrais imports en production)
try:
    from foundry_agent_framework import Agent, SnowflakeConnector
    FOUNDRY_AVAILABLE = True
except ImportError:
    FOUNDRY_AVAILABLE = False
    print("⚠️  Foundry Agent Framework non détecté - Mode simulation activé")

import snowflake.connector
from snowflake.connector import DictCursor

class SnowflakeRetailAgent:
    """Agent retail Snowflake avec support Foundry"""
    
    def __init__(self, 
                 account: str = "nfhtxdc-gg96899",
                 warehouse: str = "COMPUTE_WH", 
                 database: str = "RETAIL_DEMO",
                 schema: str = "PUBLIC"):
        
        self.account = account
        self.warehouse = warehouse  
        self.database = database
        self.schema = schema
        self.connection = None
        
    def connect(self) -> bool:
        """Connexion sécurisée à Snowflake"""
        try:
            # Utiliser variables d'environnement pour sécurité
            user = os.getenv('SNOWFLAKE_USER')
            password = os.getenv('SNOWFLAKE_PASSWORD')
            
            if not user or not password:
                print("🔐 Variables SNOWFLAKE_USER et SNOWFLAKE_PASSWORD requises")
                return False
                
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=user,
                password=password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )
            print(f"✅ Connexion Snowflake établie : {self.account}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion Snowflake : {e}")
            return False
    
    def ask_agent(self, question: str, agent_type: str = "IA") -> Dict[str, Any]:
        """Interroger l'agent retail avec fallback"""
        if not self.connection:
            return {"error": "Pas de connexion Snowflake"}
        
        try:
            cursor = self.connection.cursor(DictCursor)
            
            # Tenter agent IA en premier
            if agent_type == "IA":
                try:
                    cursor.execute(
                        "SELECT AGENT_IA_CLIENTS(%s) as response", 
                        (question,)
                    )
                    result = cursor.fetchone()
                    
                    if result and result['RESPONSE']:
                        return {
                            "success": True,
                            "agent_type": "IA_CORTEX",
                            "response": result['RESPONSE'],
                            "timestamp": datetime.now().isoformat(),
                            "question": question
                        }
                except Exception as e:
                    print(f"⚠️  Agent IA indisponible, fallback SQL : {e}")
            
            # Fallback sur agents SQL  
            cursor.execute(
                "SELECT AGENT_CLIENTS(%s) as response", 
                (question,)
            )
            result = cursor.fetchone()
            
            return {
                "success": True,
                "agent_type": "SQL_BACKUP",  
                "response": result['RESPONSE'] if result else "Aucune réponse",
                "timestamp": datetime.now().isoformat(),
                "question": question
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "question": question
            }
        finally:
            if cursor:
                cursor.close()

class FoundryAgentBridge:
    """Bridge pour intégration Foundry Agent Framework"""
    
    def __init__(self, snowflake_agent: SnowflakeRetailAgent):
        self.snowflake_agent = snowflake_agent
        
    async def process_message(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Interface Foundry standard pour traitement messages"""
        
        # Log de la demande  
        self._log_request(message, context)
        
        # Traitement via agent Snowflake
        response = self.snowflake_agent.ask_agent(message)
        
        # Formatage réponse Foundry
        foundry_response = {
            "agent_name": "snowflake-retail-advisor",
            "version": "1.0.0",
            "input": message,
            "output": response,
            "metadata": {
                "platform": "snowflake",
                "database": "RETAIL_DEMO",
                "foundry_integration": True,
                "context": context or {}
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Log de la réponse
        self._log_response(foundry_response)
        
        return foundry_response
    
    def _log_request(self, message: str, context: Dict):
        """Logger les demandes pour audit Foundry"""
        if self.snowflake_agent.connection:
            try:
                cursor = self.snowflake_agent.connection.cursor()
                cursor.execute("""
                    INSERT INTO FOUNDRY_INTEGRATION_LOG 
                    (REQUEST_MESSAGE, REQUEST_CONTEXT, LOG_TYPE)
                    VALUES (%s, %s, 'REQUEST')
                """, (message, json.dumps(context or {})))
                cursor.close()
            except Exception as e:
                print(f"⚠️  Erreur log request : {e}")
    
    def _log_response(self, response: Dict):
        """Logger les réponses pour audit Foundry"""  
        if self.snowflake_agent.connection:
            try:
                cursor = self.snowflake_agent.connection.cursor()
                cursor.execute("""
                    INSERT INTO FOUNDRY_INTEGRATION_LOG 
                    (RESPONSE_DATA, LOG_TYPE)
                    VALUES (%s, 'RESPONSE')  
                """, (json.dumps(response),))
                cursor.close()
            except Exception as e:
                print(f"⚠️  Erreur log response : {e}")

async def test_local_integration():
    """Test intégration locale (sans Foundry déployé)"""
    print("🧪 === TEST LOCAL INTEGRATION SNOWFLAKE → FOUNDRY ===")
    
    # 1. Setup agent Snowflake
    agent = SnowflakeRetailAgent()
    if not agent.connect():
        return False
    
    # 2. Setup bridge Foundry  
    bridge = FoundryAgentBridge(agent)
    
    # 3. Questions de test
    test_questions = [
        "Qui sont mes clients VIP ?",
        "Analyse des ventes par catégorie",  
        "Performance du magasin de Paris",
        "Recommandations pour Black Friday"
    ]
    
    print(f"\n📋 Test de {len(test_questions)} questions...")
    
    results = []
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question : {question}")
        
        # Context simulation Foundry
        context = {
            "user_id": "test_user",
            "session_id": f"session_{i}",  
            "platform": "foundry_test"
        }
        
        # Appel via bridge
        response = await bridge.process_message(question, context)
        results.append(response)
        
        # Affichage résultat
        if response['output'].get('success'):
            agent_type = response['output']['agent_type']
            answer = response['output']['response']
            print(f"   ✅ Agent {agent_type} : {answer[:100]}...")
        else:
            error = response['output'].get('error', 'Erreur inconnue')
            print(f"   ❌ Erreur : {error}")
    
    # 4. Résumé 
    success_count = sum(1 for r in results if r['output'].get('success'))
    print(f"\n📊 RÉSULTATS : {success_count}/{len(results)} réussites")
    
    if success_count == len(results):
        print("🎉 Intégration locale VALIDÉE ! Prête pour déploiement Foundry.")
    else:
        print("⚠️  Problèmes détectés - Vérifier configuration Snowflake")
    
    # Nettoyage
    if agent.connection:
        agent.connection.close()
        
    return success_count == len(results)

async def test_foundry_production():
    """Test avec vrai Foundry Agent Framework (si disponible)"""
    print("🚀 === TEST FOUNDRY PRODUCTION ===")
    
    if not FOUNDRY_AVAILABLE:
        print("❌ Foundry Agent Framework non installé")
        print("   Installation : pip install foundry-agent-framework")
        return False
    
    # TODO: Implémenter avec vrais composants Foundry
    print("🔧 À implémenter avec Foundry Agent Framework réel")
    print("   Nécessite : configuration agent.yaml + déploiement cloud")
    
    return False

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Test intégration Foundry")
    parser.add_argument('--mode', choices=['local', 'foundry'], 
                       default='local', help='Mode de test')
    
    args = parser.parse_args()
    
    print("🌉 TEST INTÉGRATION SNOWFLAKE ↔️ MICROSOFT FOUNDRY")
    print("=" * 55)
    
    if args.mode == 'local':
        success = asyncio.run(test_local_integration())
    else:
        success = asyncio.run(test_foundry_production())
    
    if success:
        print("\n🎊 Tests réussis ! Intégration opérationnelle.")
        print("\n📋 PROCHAINES ÉTAPES :")
        print("   1. Déployer agent.yaml vers Foundry")
        print("   2. Configurer monitoring et alertes")  
        print("   3. Former les équipes utilisatrices")
        print("   4. Mesurer adoption et ROI")
    else:
        print("\n🔧 Ajustements nécessaires avant production")

if __name__ == "__main__":
    main()