#!/usr/bin/env python3
"""
Générateur de Données Retail Synthétiques pour Démonstration Snowflake
========================================================================

Ce script génère des données retail réalistes incluant :
- Catégories et produits 
- Magasins et clients
- Commandes et lignes de commande
- Données géographiques françaises et internationales

Usage:
    python generate_retail_data.py --size medium --output csv
    python generate_retail_data.py --size large --format json --locale fr
"""

import random
import json
import csv
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import uuid

# Configuration des tailles de données
DATA_SIZES = {
    'small': {
        'categories': 20, 'products': 500, 'stores': 25, 
        'customers': 2000, 'orders': 10000, 'max_items_per_order': 8
    },
    'medium': {
        'categories': 50, 'products': 2000, 'stores': 100, 
        'customers': 10000, 'orders': 50000, 'max_items_per_order': 12
    },
    'large': {
        'categories': 100, 'products': 5000, 'stores': 250, 
        'customers': 50000, 'orders': 200000, 'max_items_per_order': 15
    }
}

# Données de référence
CATEGORIES_FR = [
    "Électronique", "Mode & Vêtements", "Maison & Jardin", "Sports & Loisirs", 
    "Beauté & Santé", "Alimentaire", "Automobile", "Livres & Média", 
    "Jouets & Enfants", "Bricolage & Outillage", "Informatique", "Téléphonie",
    "Électroménager", "Mobilier", "Décoration", "Bijoux & Montres",
    "Chaussures", "Bagagerie", "Lingerie", "Parfumerie"
]

BRANDS = [
    "TechnoMax", "StylePlus", "HomeComfort", "SportZone", "BeautyLux", 
    "FoodMart", "AutoParts", "ReadMore", "PlayTime", "BuildIt",
    "Samsung", "Apple", "Nike", "Adidas", "L'Oréal", "Zara", "H&M",
    "IKEA", "Decathlon", "Sephora", "Amazon", "Microsoft"
]

FRENCH_CITIES = [
    ("Paris", "Île-de-France", "75001"), ("Lyon", "Auvergne-Rhône-Alpes", "69000"),
    ("Marseille", "Provence-Alpes-Côte d'Azur", "13000"), ("Toulouse", "Occitanie", "31000"),
    ("Nice", "Provence-Alpes-Côte d'Azur", "06000"), ("Nantes", "Pays de la Loire", "44000"),
    ("Montpellier", "Occitanie", "34000"), ("Strasbourg", "Grand Est", "67000"),
    ("Bordeaux", "Nouvelle-Aquitaine", "33000"), ("Lille", "Hauts-de-France", "59000"),
    ("Rennes", "Bretagne", "35000"), ("Reims", "Grand Est", "51100"),
    ("Saint-Étienne", "Auvergne-Rhône-Alpes", "42000"), ("Toulon", "Provence-Alpes-Côte d'Azur", "83000"),
    ("Le Havre", "Normandie", "76600"), ("Grenoble", "Auvergne-Rhône-Alpes", "38000")
]

FIRST_NAMES_FR = [
    "Marie", "Jean", "Pierre", "Michel", "André", "Philippe", "Alain", "Bernard", 
    "Christophe", "Christian", "Daniel", "Patrice", "François", "Frédéric", "Laurent",
    "Nicolas", "Olivier", "Sébastien", "Julien", "David", "Stéphane", "Pascal",
    "Nathalie", "Isabelle", "Sylvie", "Catherine", "Françoise", "Monique", "Martine",
    "Brigitte", "Corinne", "Véronique", "Sandrine", "Céline", "Valérie", "Karine",
    "Émilie", "Julie", "Caroline", "Aurélie", "Manon", "Clara", "Léa", "Camille"
]

LAST_NAMES_FR = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
    "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David",
    "Bertrand", "Morel", "Fournier", "Girard", "Bonnet", "Dupont", "Lambert", "Fontaine",
    "Rousseau", "Vincent", "Müller", "Lefevre", "Faure", "Andre", "Mercier", "Blanc",
    "Guerin", "Boyer", "Garnier", "Chevalier", "Francois", "Legrand", "Gauthier", "Garcia"
]

@dataclass
class Category:
    category_id: int
    name: str
    description: str
    parent_category_id: int = None
    created_date: str = None

@dataclass
class Product:
    product_id: int
    name: str
    category_id: int
    brand: str
    price: float
    cost: float
    stock_quantity: int
    supplier: str
    created_date: str = None

@dataclass
class Store:
    store_id: int
    name: str
    address: str
    city: str
    region: str
    country: str
    postal_code: str
    manager_name: str
    opening_date: str
    store_type: str
    surface_m2: int
    created_date: str = None

@dataclass
class Customer:
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    region: str
    country: str
    postal_code: str
    date_of_birth: str
    gender: str
    customer_segment: str
    registration_date: str
    last_login_date: str = None
    is_active: bool = True
    created_date: str = None

@dataclass  
class Order:
    order_id: int
    customer_id: int
    store_id: int
    order_date: str
    status: str
    total_amount: float
    discount_amount: float
    tax_amount: float
    payment_method: str
    shipping_address: str
    delivery_date: str = None
    notes: str = None
    created_date: str = None

@dataclass
class OrderItem:
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount_percent: float
    created_date: str = None

class RetailDataGenerator:
    
    def __init__(self, size: str = 'medium', locale: str = 'fr'):
        self.config = DATA_SIZES[size]
        self.locale = locale
        self.categories = []
        self.products = []
        self.stores = []
        self.customers = []
        self.orders = []
        self.order_items = []
        
    def generate_all_data(self):
        """Génère toutes les données dans l'ordre correct"""
        print("🏗️  Génération des données retail...")
        
        print(f"📁 Génération de {self.config['categories']} catégories...")
        self.generate_categories()
        
        print(f"📦 Génération de {self.config['products']} produits...")
        self.generate_products()
        
        print(f"🏪 Génération de {self.config['stores']} magasins...")
        self.generate_stores()
        
        print(f"👥 Génération de {self.config['customers']} clients...")
        self.generate_customers()
        
        print(f"🛒 Génération de {self.config['orders']} commandes...")
        self.generate_orders()
        
        print("✅ Génération terminée!")
        
    def generate_categories(self):
        """Génère les catégories de produits"""
        main_categories = CATEGORIES_FR[:self.config['categories']//2]
        
        for i, cat_name in enumerate(main_categories, 1):
            category = Category(
                category_id=i,
                name=cat_name,
                description=f"Catégorie {cat_name} - Large sélection de produits",
                created_date=self._random_date_str(days_back=365)
            )
            self.categories.append(category)
            
        # Sous-catégories
        sub_cat_id = len(main_categories) + 1
        for parent in self.categories[:10]:  # Sous-catégories pour les 10 premières
            if sub_cat_id <= self.config['categories']:
                sub_category = Category(
                    category_id=sub_cat_id,
                    name=f"{parent.name} Premium",
                    description=f"Sous-catégorie premium de {parent.name}",
                    parent_category_id=parent.category_id,
                    created_date=self._random_date_str(days_back=300)
                )
                self.categories.append(sub_category)
                sub_cat_id += 1
                
    def generate_products(self):
        """Génère les produits"""
        for i in range(1, self.config['products'] + 1):
            category = random.choice(self.categories)
            brand = random.choice(BRANDS)
            cost = round(random.uniform(5.0, 500.0), 2)
            price = round(cost * random.uniform(1.2, 3.5), 2)  # Marge entre 20% et 250%
            
            product = Product(
                product_id=i,
                name=f"{brand} {category.name} {random.randint(100, 999)}",
                category_id=category.category_id,
                brand=brand,
                price=price,
                cost=cost,
                stock_quantity=random.randint(0, 1000),
                supplier=f"Supplier_{random.randint(1, 50)}",
                created_date=self._random_date_str(days_back=500)
            )
            self.products.append(product)
            
    def generate_stores(self):
        """Génère les magasins"""
        store_types = ["Flagship", "Standard", "Outlet", "Pop-up"]
        
        for i in range(1, self.config['stores'] + 1):
            city_data = random.choice(FRENCH_CITIES)
            city, region, postal = city_data
            
            store = Store(
                store_id=i,
                name=f"Store {city} {random.choice(['Centre', 'Nord', 'Sud', 'Est', 'Ouest'])}",
                address=f"{random.randint(1, 200)} Rue {random.choice(['de la Paix', 'des Fleurs', 'du Commerce', 'Principale'])}",
                city=city,
                region=region,
                country="France",
                postal_code=postal,
                manager_name=f"{random.choice(FIRST_NAMES_FR)} {random.choice(LAST_NAMES_FR)}",
                opening_date=self._random_date_str(days_back=2000, date_only=True),
                store_type=random.choice(store_types),
                surface_m2=random.randint(100, 2000),
                created_date=self._random_date_str(days_back=1000)
            )
            self.stores.append(store)
            
    def generate_customers(self):
        """Génère les clients"""
        segments = ["Premium", "Standard", "Bronze"]
        genders = ["M", "F", "Non-binaire"]
        
        for i in range(1, self.config['customers'] + 1):
            first_name = random.choice(FIRST_NAMES_FR)
            last_name = random.choice(LAST_NAMES_FR)
            city_data = random.choice(FRENCH_CITIES)
            
            customer = Customer(
                customer_id=i,
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}@email.com".replace(" ", ""),
                phone=f"0{random.randint(100000000, 799999999)}",
                address=f"{random.randint(1, 200)} Avenue {random.choice(['des Champs', 'de la République', 'Victor Hugo'])}",
                city=city_data[0],
                region=city_data[1], 
                country="France",
                postal_code=city_data[2],
                date_of_birth=self._random_date_str(days_back=random.randint(18*365, 80*365), date_only=True),
                gender=random.choice(genders),
                customer_segment=random.choice(segments),
                registration_date=self._random_date_str(days_back=random.randint(1, 1000), date_only=True),
                last_login_date=self._random_date_str(days_back=random.randint(0, 30)),
                is_active=random.choices([True, False], weights=[0.9, 0.1])[0],
                created_date=self._random_date_str(days_back=800)
            )
            self.customers.append(customer)
            
    def generate_orders(self):
        """Génère les commandes et leurs lignes"""
        statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        payment_methods = ["Credit Card", "Debit Card", "Cash", "PayPal", "Apple Pay"]
        
        order_item_id = 1
        
        for i in range(1, self.config['orders'] + 1):
            customer = random.choice(self.customers)
            store = random.choice(self.stores)
            order_date = self._random_date_str(days_back=365)
            status = random.choice(statuses)
            
            # Génération des lignes de commande
            num_items = random.randint(1, self.config['max_items_per_order'])
            order_total = 0
            current_order_items = []
            
            for _ in range(num_items):
                product = random.choice(self.products)
                quantity = random.randint(1, 5)
                unit_price = product.price * random.uniform(0.8, 1.2)  # Variation de prix
                discount = random.choices([0, 5, 10, 15, 20], weights=[0.6, 0.15, 0.15, 0.05, 0.05])[0]
                
                order_item = OrderItem(
                    order_item_id=order_item_id,
                    order_id=i,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                    discount_percent=discount,
                    created_date=order_date
                )
                
                line_total = quantity * unit_price * (1 - discount/100)
                order_total += line_total
                current_order_items.append(order_item)
                order_item_id += 1
                
            # Calculs des montants de commande
            discount_amount = round(order_total * random.uniform(0, 0.1), 2)  # 0-10% de remise
            tax_amount = round((order_total - discount_amount) * 0.2, 2)  # TVA 20%
            final_total = round(order_total - discount_amount + tax_amount, 2)
            
            # Création de la commande
            order = Order(
                order_id=i,
                customer_id=customer.customer_id,
                store_id=store.store_id,
                order_date=order_date,
                status=status,
                total_amount=final_total,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                payment_method=random.choice(payment_methods),
                shipping_address=f"{customer.address}, {customer.city} {customer.postal_code}",
                delivery_date=self._add_days_to_date_str(order_date, random.randint(1, 14)) if status == "Delivered" else None,
                notes=random.choice([None, "Livraison rapide", "Fragile", "Cadeau", ""])
            )
            
            self.orders.append(order)
            self.order_items.extend(current_order_items)
            
    def export_to_csv(self, output_dir: str = "data_output"):
        """Exporte toutes les données en CSV"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        datasets = {
            'categories': self.categories,
            'products': self.products, 
            'stores': self.stores,
            'customers': self.customers,
            'orders': self.orders,
            'order_items': self.order_items
        }
        
        for name, data in datasets.items():
            if data:
                file_path = f"{output_dir}/{name}.csv"
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=asdict(data[0]).keys())
                    writer.writeheader()
                    for item in data:
                        writer.writerow(asdict(item))
                print(f"✅ Export CSV: {file_path} ({len(data)} records)")
                
    def export_to_json(self, output_dir: str = "data_output"):
        """Exporte toutes les données en JSON"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        datasets = {
            'categories': self.categories,
            'products': self.products,
            'stores': self.stores, 
            'customers': self.customers,
            'orders': self.orders,
            'order_items': self.order_items
        }
        
        for name, data in datasets.items():
            if data:
                file_path = f"{output_dir}/{name}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json_data = [asdict(item) for item in data]
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print(f"✅ Export JSON: {file_path} ({len(data)} records)")
                
    def _random_date_str(self, days_back: int, date_only: bool = False):
        """Génère une date aléatoire dans le passé"""
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        if date_only:
            return random_date.strftime('%Y-%m-%d')
        return random_date.strftime('%Y-%m-%d %H:%M:%S')
        
    def _add_days_to_date_str(self, date_str: str, days: int):
        """Ajoute des jours à une date string"""
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        new_dt = dt + timedelta(days=days)
        return new_dt.strftime('%Y-%m-%d %H:%M:%S')

def main():
    parser = argparse.ArgumentParser(description='Générateur de données retail')
    parser.add_argument('--size', choices=['small', 'medium', 'large'], 
                       default='medium', help='Taille du jeu de données')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], 
                       default='both', help='Format de sortie')
    parser.add_argument('--output', default='data_output', 
                       help='Répertoire de sortie')
    parser.add_argument('--locale', default='fr', 
                       help='Locale pour les données')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏪 GÉNÉRATEUR DE DONNÉES RETAIL POUR DÉMONSTRATION SNOWFLAKE")
    print("=" * 60)
    print(f"📊 Taille: {args.size}")
    print(f"📁 Format: {args.format}")
    print(f"🌍 Locale: {args.locale}")
    print(f"💾 Sortie: {args.output}")
    print("=" * 60)
    
    generator = RetailDataGenerator(size=args.size, locale=args.locale)
    generator.generate_all_data()
    
    if args.format in ['csv', 'both']:
        generator.export_to_csv(args.output)
        
    if args.format in ['json', 'both']:
        generator.export_to_json(args.output)
        
    print("=" * 60)
    print("🎉 Génération terminée avec succès!")
    print(f"📈 Statistiques:")
    print(f"   • {len(generator.categories)} catégories")
    print(f"   • {len(generator.products)} produits") 
    print(f"   • {len(generator.stores)} magasins")
    print(f"   • {len(generator.customers)} clients")
    print(f"   • {len(generator.orders)} commandes")
    print(f"   • {len(generator.order_items)} lignes de commande")
    print("=" * 60)

if __name__ == "__main__":
    main()