#!/usr/bin/env python3
import pandas as pd

print("📊 Test des données générées...")

# Lecture des fichiers
customers = pd.read_csv('data_generation/data_output/customers.csv')
orders = pd.read_csv('data_generation/data_output/orders.csv') 
products = pd.read_csv('data_generation/data_output/products.csv')
categories = pd.read_csv('data_generation/data_output/categories.csv')
stores = pd.read_csv('data_generation/data_output/stores.csv')

print(f"✅ {len(customers):,} clients")
print(f"✅ {len(orders):,} commandes") 
print(f"✅ {len(products):,} produits")
print(f"✅ {len(categories):,} catégories")
print(f"✅ {len(stores):,} magasins")

# Calculs business
ca_total = orders['total_amount'].sum()
panier_moyen = orders['total_amount'].mean()
clients_actifs = orders['customer_id'].nunique()

print(f"\n💰 KPIs Générés:")
print(f"   • CA Total: {ca_total:,.0f} €")
print(f"   • Panier Moyen: {panier_moyen:.2f} €") 
print(f"   • Clients Actifs: {clients_actifs:,}")
print(f"   • Taux Activation: {clients_actifs/len(customers)*100:.1f}%")

print("\n🎉 Données prêtes pour Snowflake !")