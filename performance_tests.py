#!/usr/bin/env python
"""
Pruebas de Rendimiento para Dulce Bias
Ejecuta pruebas de carga, memoria y tiempo de respuesta
"""

import os
import sys
import time
import requests
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from shop.models import Product, Category
from support.models import Ticket, Category as SupportCategory

class PerformanceTestSuite:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = Client()
        self.results = {}
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def measure_memory_usage(self):
        """Mide el uso actual de memoria"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
        
    def test_page_load_time(self, url, name, iterations=10):
        """Prueba tiempo de carga de página"""
        self.log(f"🔍 Probando {name} ({iterations} iteraciones)")
        
        times = []
        memory_before = self.measure_memory_usage()
        
        for i in range(iterations):
            start_time = time.time()
            try:
                if url.startswith('http'):
                    response = requests.get(url, timeout=30)
                    status_code = response.status_code
                else:
                    response = self.client.get(url)
                    status_code = response.status_code
                    
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                
                if status_code == 200:
                    times.append(response_time)
                    print(f"  ✅ Iteración {i+1}: {response_time:.2f}ms")
                else:
                    print(f"  ❌ Iteración {i+1}: Error {status_code}")
                    
            except Exception as e:
                print(f"  ❌ Iteración {i+1}: Error - {str(e)}")
                
        memory_after = self.measure_memory_usage()
        
        if times:
            result = {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'median_time': statistics.median(times),
                'total_requests': len(times),
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_diff': memory_after['rss'] - memory_before['rss']
            }
            
            self.results[name] = result
            
            print(f"  📊 Promedio: {result['avg_time']:.2f}ms")
            print(f"  📊 Mínimo: {result['min_time']:.2f}ms")
            print(f"  📊 Máximo: {result['max_time']:.2f}ms")
            print(f"  📊 Mediana: {result['median_time']:.2f}ms")
            print(f"  🧠 Memoria: {result['memory_diff']:.2f}MB")
            print()
            
        return result if times else None
        
    def test_concurrent_load(self, url, name, concurrent_users=10, requests_per_user=5):
        """Prueba carga concurrente"""
        self.log(f"🚀 Prueba de carga concurrente: {name}")
        self.log(f"   👥 {concurrent_users} usuarios, {requests_per_user} requests c/u")
        
        def make_request(user_id):
            times = []
            for i in range(requests_per_user):
                start_time = time.time()
                try:
                    if url.startswith('http'):
                        response = requests.get(url, timeout=30)
                    else:
                        response = self.client.get(url)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    times.append(response_time)
                except Exception as e:
                    print(f"  ❌ Usuario {user_id}, Request {i+1}: {str(e)}")
            return times
            
        memory_before = self.measure_memory_usage()
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request, i) for i in range(concurrent_users)]
            all_times = []
            
            for future in as_completed(futures):
                try:
                    times = future.result()
                    all_times.extend(times)
                except Exception as e:
                    print(f"  ❌ Error en thread: {str(e)}")
                    
        total_time = time.time() - start_time
        memory_after = self.measure_memory_usage()
        
        if all_times:
            result = {
                'concurrent_users': concurrent_users,
                'requests_per_user': requests_per_user,
                'total_requests': len(all_times),
                'total_time': total_time,
                'requests_per_second': len(all_times) / total_time,
                'avg_response_time': statistics.mean(all_times),
                'min_response_time': min(all_times),
                'max_response_time': max(all_times),
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_diff': memory_after['rss'] - memory_before['rss']
            }
            
            self.results[f"{name}_concurrent"] = result
            
            print(f"  📊 Total requests: {result['total_requests']}")
            print(f"  📊 Tiempo total: {result['total_time']:.2f}s")
            print(f"  📊 Requests/segundo: {result['requests_per_second']:.2f}")
            print(f"  📊 Tiempo promedio: {result['avg_response_time']:.2f}ms")
            print(f"  🧠 Memoria usada: {result['memory_diff']:.2f}MB")
            print()
            
        return result if all_times else None
        
    def test_database_performance(self):
        """Prueba rendimiento de la base de datos"""
        self.log("🗄️ Probando rendimiento de base de datos")
        
        # Test de consultas simples
        start_time = time.time()
        products = list(Product.objects.all())
        products_time = (time.time() - start_time) * 1000
        
        start_time = time.time()
        categories = list(Category.objects.all())
        categories_time = (time.time() - start_time) * 1000
        
        start_time = time.time()
        users = list(User.objects.all())
        users_time = (time.time() - start_time) * 1000
        
        # Test de consultas complejas
        start_time = time.time()
        featured_products = list(Product.objects.filter(featured=True, available=True).select_related('category'))
        featured_time = (time.time() - start_time) * 1000
        
        result = {
            'products_query': {'time': products_time, 'count': len(products)},
            'categories_query': {'time': categories_time, 'count': len(categories)},
            'users_query': {'time': users_time, 'count': len(users)},
            'featured_products_query': {'time': featured_time, 'count': len(featured_products)}
        }
        
        self.results['database_performance'] = result
        
        print(f"  📊 Productos ({len(products)}): {products_time:.2f}ms")
        print(f"  📊 Categorías ({len(categories)}): {categories_time:.2f}ms")
        print(f"  📊 Usuarios ({len(users)}): {users_time:.2f}ms")
        print(f"  📊 Productos destacados ({len(featured_products)}): {featured_time:.2f}ms")
        print()
        
        return result
        
    def run_comprehensive_tests(self):
        """Ejecuta todas las pruebas de rendimiento"""
        self.log("🚀 Iniciando pruebas de rendimiento completas")
        self.log("=" * 60)
        
        # Información del sistema
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        self.log(f"💻 Sistema: {cpu_count} CPUs, {memory.total / 1024**3:.1f}GB RAM")
        
        # Pruebas básicas de páginas
        pages_to_test = [
            ('/', 'Página de inicio'),
            ('/productos/', 'Lista de productos'),
            ('/support/', 'Centro de soporte'),
            ('/support/admin/categories/', 'Admin categorías'),
            ('/support/admin/statistics/', 'Admin estadísticas'),
        ]
        
        for url, name in pages_to_test:
            self.test_page_load_time(url, name, iterations=10)
            
        # Pruebas de carga concurrente
        critical_pages = [
            ('/', 'Inicio'),
            ('/productos/', 'Productos'),
        ]
        
        for url, name in critical_pages:
            self.test_concurrent_load(url, name, concurrent_users=5, requests_per_user=3)
            
        # Pruebas de base de datos
        self.test_database_performance()
        
        # Generar reporte final
        self.generate_report()
        
    def generate_report(self):
        """Genera reporte final de rendimiento"""
        self.log("📋 REPORTE FINAL DE RENDIMIENTO")
        self.log("=" * 60)
        
        # Resumen de páginas individuales
        print("\n🌐 RENDIMIENTO POR PÁGINA:")
        print("-" * 40)
        for name, result in self.results.items():
            if not name.endswith('_concurrent') and name != 'database_performance':
                status = "🟢 EXCELENTE" if result['avg_time'] < 100 else \
                        "🟡 BUENO" if result['avg_time'] < 500 else \
                        "🟠 REGULAR" if result['avg_time'] < 1000 else "🔴 LENTO"
                print(f"{name}: {result['avg_time']:.2f}ms {status}")
                
        # Resumen de carga concurrente
        print("\n🚀 RENDIMIENTO BAJO CARGA:")
        print("-" * 40)
        for name, result in self.results.items():
            if name.endswith('_concurrent'):
                rps = result['requests_per_second']
                status = "🟢 EXCELENTE" if rps > 50 else \
                        "🟡 BUENO" if rps > 20 else \
                        "🟠 REGULAR" if rps > 10 else "🔴 LENTO"
                print(f"{name}: {rps:.2f} req/s {status}")
                
        # Resumen de base de datos
        if 'database_performance' in self.results:
            print("\n🗄️ RENDIMIENTO DE BASE DE DATOS:")
            print("-" * 40)
            db_result = self.results['database_performance']
            for query_name, data in db_result.items():
                status = "🟢 RÁPIDO" if data['time'] < 10 else \
                        "🟡 NORMAL" if data['time'] < 50 else \
                        "🟠 LENTO" if data['time'] < 100 else "🔴 MUY LENTO"
                print(f"{query_name}: {data['time']:.2f}ms ({data['count']} registros) {status}")
                
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        print("-" * 40)
        
        slow_pages = [name for name, result in self.results.items() 
                     if not name.endswith('_concurrent') and name != 'database_performance' 
                     and result['avg_time'] > 500]
        
        if slow_pages:
            print("• Optimizar páginas lentas:", ", ".join(slow_pages))
            print("• Considerar caché de páginas")
            print("• Optimizar consultas de base de datos")
        else:
            print("• ✅ Todas las páginas tienen buen rendimiento")
            
        low_rps = [name for name, result in self.results.items() 
                  if name.endswith('_concurrent') and result['requests_per_second'] < 20]
        
        if low_rps:
            print("• Mejorar capacidad de carga concurrente")
            print("• Considerar balanceador de carga")
        else:
            print("• ✅ Buena capacidad de carga concurrente")
            
        print("\n✨ Pruebas completadas!")

if __name__ == "__main__":
    print("🔥 DULCE BIAS - SUITE DE PRUEBAS DE RENDIMIENTO")
    print("=" * 60)
    
    # Verificar si el servidor está corriendo
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        print("✅ Servidor detectado en http://127.0.0.1:8000")
    except:
        print("❌ Servidor no detectado. Asegúrate de ejecutar 'python manage.py runserver'")
        sys.exit(1)
        
    # Ejecutar pruebas
    suite = PerformanceTestSuite()
    suite.run_comprehensive_tests()
