"""
Script para poblar la base de datos con productos de ejemplo
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from shop.models import Category, Product
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_data():
    """Crear datos de ejemplo para el sitio"""
    
    # Crear superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@dulcebias.cl', 'admin123')
        print("✅ Superusuario 'admin' creado con contraseña 'admin123'")
    else:
        print("ℹ️ Superusuario 'admin' ya existe")
    
    # Crear categorías
    categories_data = [
        {
            'name': 'Galletas Clásicas',
            'slug': 'galletas-clasicas',
            'description': 'Nuestras recetas tradicionales que han conquistado corazones por generaciones.'
        },
        {
            'name': 'Galletas Premium',
            'slug': 'galletas-premium',
            'description': 'Ediciones especiales con ingredientes selectos y sabores únicos.'
        },
        {
            'name': 'Galletas Saludables',
            'slug': 'galletas-saludables',
            'description': 'Opciones nutritivas sin sacrificar el sabor que tanto amas.'
        },
        {
            'name': 'Mix y Variedades',
            'slug': 'mix-variedades',
            'description': 'Cajas variadas para que disfrutes de todos nuestros sabores.'
        }
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Categoría creada: {category.name}")
        else:
            print(f"ℹ️ Categoría ya existe: {category.name}")
    
    # Crear productos
    products_data = [
        {
            'name': 'Galletas de Chocolate Premium',
            'slug': 'galletas-chocolate-premium',
            'category_slug': 'galletas-premium',
            'product_type': 'premium',
            'description': 'Galletas artesanales con chocolate belga de la más alta calidad. Perfectas para acompañar tu café de la tarde.',
            'ingredients': 'Harina de trigo, chocolate belga 30%, mantequilla, azúcar, huevos, vainilla, sal',
            'price': 8990,
            'stock': 25,
            'featured': True,
            'weight': 200,
            'nutrition_facts': 'Calorías: 450 por 100g, Grasas: 22g, Carbohidratos: 58g, Proteínas: 6g'
        },
        {
            'name': 'Galletas de Avena y Miel',
            'slug': 'galletas-avena-miel',
            'category_slug': 'galletas-saludables',
            'product_type': 'healthy',
            'description': 'Galletas nutritivas hechas con avena integral y miel natural. Una opción deliciosa y saludable.',
            'ingredients': 'Avena integral, miel natural, aceite de coco, harina integral, canela, sal marina',
            'price': 7990,
            'stock': 30,
            'featured': True,
            'weight': 180,
            'nutrition_facts': 'Calorías: 380 por 100g, Grasas: 15g, Carbohidratos: 55g, Proteínas: 8g, Fibra: 6g'
        },
        {
            'name': 'Galletas de Mantequilla Clásicas',
            'slug': 'galletas-mantequilla-clasicas',
            'category_slug': 'galletas-clasicas',
            'product_type': 'classic',
            'description': 'La receta tradicional de la abuela. Galletas doradas y crujientes con el sabor de siempre.',
            'ingredients': 'Harina, mantequilla, azúcar, huevos, vainilla, polvo de hornear',
            'price': 6990,
            'stock': 40,
            'featured': True,
            'weight': 150,
            'nutrition_facts': 'Calorías: 420 por 100g, Grasas: 18g, Carbohidratos: 62g, Proteínas: 5g'
        },
        {
            'name': 'Mix Dulce Bias Especial',
            'slug': 'mix-dulce-bias-especial',
            'category_slug': 'mix-variedades',
            'product_type': 'bestseller',
            'description': 'Una selección de nuestras 5 galletas más populares en una caja especial. ¡Perfecto para regalar!',
            'ingredients': 'Variedad de ingredientes según las galletas incluidas',
            'price': 18990,
            'stock': 15,
            'featured': True,
            'weight': 400,
            'nutrition_facts': 'Valores nutricionales variables según la variedad'
        },
        {
            'name': 'Galletas de Coco y Almendras',
            'slug': 'galletas-coco-almendras',
            'category_slug': 'galletas-premium',
            'product_type': 'premium',
            'description': 'Exquisita combinación de coco rallado y almendras tostadas en una galleta única.',
            'ingredients': 'Coco rallado, almendras tostadas, harina, mantequilla, azúcar morena, huevos',
            'price': 9990,
            'stock': 20,
            'featured': False,
            'weight': 170,
            'nutrition_facts': 'Calorías: 480 por 100g, Grasas: 28g, Carbohidratos: 52g, Proteínas: 8g'
        },
        {
            'name': 'Galletas Integrales de Semillas',
            'slug': 'galletas-integrales-semillas',
            'category_slug': 'galletas-saludables',
            'product_type': 'healthy',
            'description': 'Galletas integrales con una mezcla especial de semillas de chía, girasol y calabaza.',
            'ingredients': 'Harina integral, semillas de chía, semillas de girasol, semillas de calabaza, aceite de oliva, miel',
            'price': 8490,
            'stock': 22,
            'featured': False,
            'weight': 160,
            'nutrition_facts': 'Calorías: 400 por 100g, Grasas: 20g, Carbohidratos: 48g, Proteínas: 12g, Fibra: 8g'
        },
        {
            'name': 'Galletas de Naranja y Canela',
            'slug': 'galletas-naranja-canela',
            'category_slug': 'galletas-clasicas',
            'product_type': 'classic',
            'description': 'Galletas aromáticas con el toque cítrico de la naranja y el calor de la canela.',
            'ingredients': 'Harina, ralladura de naranja, canela, mantequilla, azúcar, huevos',
            'price': 7490,
            'stock': 35,
            'featured': False,
            'weight': 165,
            'nutrition_facts': 'Calorías: 410 por 100g, Grasas: 16g, Carbohidratos: 64g, Proteínas: 5g'
        },
        {
            'name': 'Caja Regalo Dulce Bias',
            'slug': 'caja-regalo-dulce-bias',
            'category_slug': 'mix-variedades',
            'product_type': 'bestseller',
            'description': 'Caja de regalo elegante con una selección premium de nuestras mejores galletas.',
            'ingredients': 'Selección variada de galletas premium y clásicas',
            'price': 24990,
            'stock': 10,
            'featured': True,
            'weight': 500,
            'nutrition_facts': 'Valores nutricionales variables según el contenido'
        }
    ]
    
    for prod_data in products_data:
        category = Category.objects.get(slug=prod_data['category_slug'])
        product_data = prod_data.copy()
        del product_data['category_slug']
        product_data['category'] = category
        
        product, created = Product.objects.get_or_create(
            slug=product_data['slug'],
            defaults=product_data
        )
        if created:
            print(f"✅ Producto creado: {product.name}")
        else:
            print(f"ℹ️ Producto ya existe: {product.name}")
    
    print("\n🎉 ¡Base de datos poblada exitosamente!")
    print("\n📋 Información del panel de administración:")
    print("URL: http://127.0.0.1:8000/admin/")
    print("Usuario: admin")
    print("Contraseña: admin123")
    print("\n💡 Puedes modificar los productos destacados desde el admin para controlar qué se muestra en la página de inicio.")

if __name__ == '__main__':
    create_sample_data()
