#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from cart.templatetags.cart_extras import format_price

def test_format_price():
    print("🧮 TESTING FORMATEO DE PRECIOS")
    print("=" * 40)
    
    test_values = [
        1500,
        15000,
        21241.50,
        169932.00,
        1234567.89
    ]
    
    for value in test_values:
        formatted = format_price(value)
        print(f"💰 {value} → {formatted}")
    
    print("\n✅ Test de formateo completado")

if __name__ == "__main__":
    test_format_price()
