"""
Script para validar la lógica de cupones en el carrito
Simula diferentes escenarios para asegurar que la lógica funciona correctamente
"""

print("=== VALIDACIÓN DE LÓGICA DE CUPONES ===\n")

# Escenarios a probar:
scenarios = [
    {
        "name": "Carrito pequeño ($8,000) + Cupón 20% (TEST20)",
        "subtotal": 8000,
        "coupon_type": "percentage",
        "coupon_value": 20,
        "coupon_min": 5000,
        "expected_discount": 1600,  # 20% de 8000
        "expected_shipping": 3000,  # No califica para envío gratis
        "expected_total": 9400      # 8000 - 1600 + 3000
    },
    {
        "name": "Carrito grande ($20,000) + Cupón 20% (TEST20)",
        "subtotal": 20000,
        "coupon_type": "percentage", 
        "coupon_value": 20,
        "coupon_min": 5000,
        "expected_discount": 4000,  # 20% de 20000
        "expected_shipping": 0,     # Envío gratis por monto
        "expected_total": 16000     # 20000 - 4000 + 0
    },
    {
        "name": "Carrito pequeño ($8,000) + Cupón envío gratis (GRATIS2025)",
        "subtotal": 8000,
        "coupon_type": "free_shipping",
        "coupon_value": 0,
        "coupon_min": 1000,
        "expected_discount": 3000,  # Descuento = costo de envío
        "expected_shipping": 0,     # Envío gratis por cupón
        "expected_total": 8000      # 8000 - 0 + 0 (descuento se ve pero no afecta subtotal)
    },
    {
        "name": "Carrito grande ($20,000) + Cupón envío gratis (GRATIS2025)",
        "subtotal": 20000,
        "coupon_type": "free_shipping",
        "coupon_value": 0,
        "coupon_min": 1000,
        "expected_discount": 0,     # Ya tenía envío gratis, no hay descuento adicional
        "expected_shipping": 0,     # Envío gratis por monto
        "expected_total": 20000     # 20000 - 0 + 0
    },
    {
        "name": "Carrito sin cupón ($8,000)",
        "subtotal": 8000,
        "coupon_type": None,
        "coupon_value": 0,
        "coupon_min": 0,
        "expected_discount": 0,     # Sin cupón
        "expected_shipping": 3000,  # Paga envío
        "expected_total": 11000     # 8000 + 3000
    },
    {
        "name": "Carrito sin cupón ($20,000)",
        "subtotal": 20000,
        "coupon_type": None,
        "coupon_value": 0,
        "coupon_min": 0,
        "expected_discount": 0,     # Sin cupón
        "expected_shipping": 0,     # Envío gratis por monto
        "expected_total": 20000     # 20000 + 0
    }
]

def simulate_cart_logic(subtotal, coupon_type=None, coupon_value=0, coupon_min=0):
    """Simula la lógica del carrito"""
    
    # 1. Calcular descuento
    discount_amount = 0
    if coupon_type and subtotal >= coupon_min:
        if coupon_type == 'percentage':
            discount_amount = subtotal * (coupon_value / 100)
        elif coupon_type == 'fixed_amount':
            discount_amount = min(coupon_value, subtotal)
        elif coupon_type == 'free_shipping':
            # Solo hay descuento visual si el carrito no califica para envío gratis automático
            if subtotal < 15000:
                discount_amount = 3000  # Costo de envío estándar
            else:
                discount_amount = 0  # Ya tenía envío gratis
    
    # 2. Calcular total después del descuento
    if coupon_type == 'free_shipping':
        # Para envío gratis, el descuento es visual pero no afecta el subtotal
        total_after_discount = subtotal
    else:
        total_after_discount = max(0, subtotal - discount_amount)
    
    # 3. Calcular costo de envío
    shipping_cost = 0
    if coupon_type == 'free_shipping' and subtotal >= coupon_min:
        # Cupón de envío gratis aplicado
        shipping_cost = 0
    elif subtotal >= 15000:
        # Envío gratis por monto
        shipping_cost = 0
    else:
        # Paga envío
        shipping_cost = 3000
    
    # 4. Total final
    final_total = total_after_discount + shipping_cost
    
    return {
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_after_discount': total_after_discount,
        'shipping_cost': shipping_cost,
        'final_total': final_total
    }

# Ejecutar pruebas
for i, scenario in enumerate(scenarios, 1):
    print(f"{i}. {scenario['name']}")
    print("-" * 50)
    
    result = simulate_cart_logic(
        scenario['subtotal'],
        scenario['coupon_type'],
        scenario['coupon_value'],
        scenario['coupon_min']
    )
    
    print(f"Subtotal:           ${result['subtotal']:,}")
    print(f"Descuento:         -${result['discount_amount']:,}")
    print(f"Total s/envío:      ${result['total_after_discount']:,}")
    print(f"Envío:             +${result['shipping_cost']:,}")
    print(f"TOTAL FINAL:        ${result['final_total']:,}")
    
    # Validar resultados
    tests_passed = 0
    total_tests = 3
    
    if result['discount_amount'] == scenario['expected_discount']:
        print("✅ Descuento correcto")
        tests_passed += 1
    else:
        print(f"❌ Descuento incorrecto: esperado ${scenario['expected_discount']:,}, obtenido ${result['discount_amount']:,}")
    
    if result['shipping_cost'] == scenario['expected_shipping']:
        print("✅ Envío correcto")
        tests_passed += 1
    else:
        print(f"❌ Envío incorrecto: esperado ${scenario['expected_shipping']:,}, obtenido ${result['shipping_cost']:,}")
    
    if result['final_total'] == scenario['expected_total']:
        print("✅ Total final correcto")
        tests_passed += 1
    else:
        print(f"❌ Total final incorrecto: esperado ${scenario['expected_total']:,}, obtenido ${result['final_total']:,}")
    
    print(f"Resultado: {tests_passed}/{total_tests} pruebas pasaron")
    print("\n")

print("=== RESUMEN DE LA LÓGICA CORREGIDA ===")
print("""
1. SUBTOTAL: Suma de todos los productos
2. ENVÍO GRATIS: Se evalúa basado en el SUBTOTAL (≥ $15,000)
3. DESCUENTO: Se aplica al subtotal
4. TOTAL FINAL: Subtotal - descuento + envío

TIPOS DE CUPONES:
- Porcentaje: Descuenta % del subtotal
- Monto fijo: Descuenta cantidad fija del subtotal  
- Envío gratis: Elimina costo de envío (descuento visual de $3,000 si aplica)

CASOS ESPECIALES:
- Si el carrito ya califica para envío gratis (≥$15,000), 
  un cupón de envío gratis no muestra descuento adicional
- Los descuentos nunca pueden hacer que el subtotal sea negativo
""")
