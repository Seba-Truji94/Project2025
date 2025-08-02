#!/usr/bin/env python
"""
Pruebas de Rendimiento Básicas para Dulce Bias
Ejecuta pruebas usando el cliente de pruebas de Django
"""

import os
import sys
import time
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import Client, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from shop.models import Product, Category
from support.models import SupportTicket, SupportCategory

class BasicPerformanceTests:
    def __init__(self):
        self.client = Client()
        self.results = {}
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_page_response_time(self, url_name, name, iterations=10, url_kwargs=None):
        """Prueba tiempo de respuesta de página"""
        self.log(f"🔍 Probando {name} ({iterations} iteraciones)")
        
        times = []
        status_codes = []
        
        for i in range(iterations):
            start_time = time.time()
            try:
                if url_kwargs:
                    url = reverse(url_name, kwargs=url_kwargs)
                else:
                    url = reverse(url_name)
                    
                response = self.client.get(url)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                times.append(response_time)
                status_codes.append(response.status_code)
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                print(f"  {status_icon} Iteración {i+1}: {response_time:.2f}ms (Status: {response.status_code})")
                
            except Exception as e:
                print(f"  ❌ Iteración {i+1}: Error - {str(e)}")
                
        if times:
            result = {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'median_time': statistics.median(times),
                'total_requests': len(times),
                'success_rate': (status_codes.count(200) / len(status_codes)) * 100,
                'status_codes': status_codes
            }
            
            self.results[name] = result
            
            print(f"  📊 Promedio: {result['avg_time']:.2f}ms")
            print(f"  📊 Mínimo: {result['min_time']:.2f}ms")
            print(f"  📊 Máximo: {result['max_time']:.2f}ms")
            print(f"  📊 Éxito: {result['success_rate']:.1f}%")
            print()
            
        return result if times else None
        
    def test_database_queries(self):
        """Prueba rendimiento de consultas de base de datos"""
        self.log("🗄️ Probando rendimiento de base de datos")
        
        # Medir consultas básicas
        queries = {
            'productos_todos': lambda: list(Product.objects.all()),
            'productos_disponibles': lambda: list(Product.objects.filter(available=True)),
            'productos_destacados': lambda: list(Product.objects.filter(featured=True)),
            'categorias_todas': lambda: list(Category.objects.all()),
            'usuarios_todos': lambda: list(User.objects.all()),
            'tickets_soporte': lambda: list(SupportTicket.objects.all()),
            'categorias_soporte': lambda: list(SupportCategory.objects.all())
        }
        
        results = {}
        
        for query_name, query_func in queries.items():
            times = []
            counts = []
            
            # Ejecutar 5 veces para obtener promedio
            for _ in range(5):
                start_time = time.time()
                try:
                    result_set = query_func()
                    end_time = time.time()
                    
                    query_time = (end_time - start_time) * 1000  # ms
                    times.append(query_time)
                    counts.append(len(result_set))
                    
                except Exception as e:
                    print(f"  ❌ Error en {query_name}: {str(e)}")
                    
            if times:
                avg_time = statistics.mean(times)
                avg_count = statistics.mean(counts)
                
                results[query_name] = {
                    'avg_time': avg_time,
                    'min_time': min(times),
                    'max_time': max(times),
                    'avg_count': avg_count
                }
                
                status = "🟢 RÁPIDO" if avg_time < 10 else \
                        "🟡 NORMAL" if avg_time < 50 else \
                        "🟠 LENTO" if avg_time < 100 else "🔴 MUY LENTO"
                        
                print(f"  {status} {query_name}: {avg_time:.2f}ms ({avg_count:.0f} registros)")
                
        self.results['database_queries'] = results
        print()
        return results
        
    def test_concurrent_requests(self, url_name, name, num_threads=5, requests_per_thread=3):
        """Prueba requests concurrentes"""
        self.log(f"🚀 Prueba concurrente: {name} ({num_threads} threads, {requests_per_thread} req/thread)")
        
        def make_requests(thread_id):
            client = Client()  # Cliente separado por thread
            times = []
            
            for i in range(requests_per_thread):
                start_time = time.time()
                try:
                    url = reverse(url_name)
                    response = client.get(url)
                    end_time = time.time()
                    
                    request_time = (end_time - start_time) * 1000
                    times.append(request_time)
                    
                except Exception as e:
                    print(f"  ❌ Thread {thread_id}, Request {i+1}: {str(e)}")
                    
            return times
            
        start_time = time.time()
        all_times = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_requests, i) for i in range(num_threads)]
            
            for future in futures:
                try:
                    times = future.result()
                    all_times.extend(times)
                except Exception as e:
                    print(f"  ❌ Error en thread: {str(e)}")
                    
        total_time = time.time() - start_time
        
        if all_times:
            result = {
                'total_requests': len(all_times),
                'total_time': total_time,
                'requests_per_second': len(all_times) / total_time,
                'avg_response_time': statistics.mean(all_times),
                'min_response_time': min(all_times),
                'max_response_time': max(all_times)
            }
            
            self.results[f"{name}_concurrent"] = result
            
            print(f"  📊 Total requests: {result['total_requests']}")
            print(f"  📊 Tiempo total: {result['total_time']:.2f}s")
            print(f"  📊 Requests/segundo: {result['requests_per_second']:.2f}")
            print(f"  📊 Tiempo promedio: {result['avg_response_time']:.2f}ms")
            print()
            
        return result if all_times else None
        
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.log("🚀 INICIANDO PRUEBAS DE RENDIMIENTO")
        self.log("=" * 60)
        
        # Pruebas de páginas individuales
        pages_to_test = [
            ('shop:home', 'Página de Inicio'),
            ('shop:product_list', 'Lista de Productos'),
            ('support:home', 'Centro de Soporte'),
            ('support:admin_management', 'Admin Management'),
            ('support:admin_categories', 'Admin Categorías'),
            ('support:admin_statistics', 'Admin Estadísticas'),
        ]
        
        for url_name, name in pages_to_test:
            try:
                self.test_page_response_time(url_name, name, iterations=8)
            except Exception as e:
                print(f"❌ Error probando {name}: {str(e)}")
                
        # Pruebas de base de datos
        self.test_database_queries()
        
        # Pruebas concurrentes en páginas críticas
        critical_pages = [
            ('shop:home', 'Inicio'),
            ('shop:product_list', 'Productos'),
            ('support:home', 'Soporte')
        ]
        
        for url_name, name in critical_pages:
            try:
                self.test_concurrent_requests(url_name, name, num_threads=3, requests_per_thread=2)
            except Exception as e:
                print(f"❌ Error en prueba concurrente {name}: {str(e)}")
                
        # Generar reporte
        self.generate_report()
        
    def generate_report(self):
        """Genera reporte final"""
        self.log("📋 REPORTE FINAL DE RENDIMIENTO")
        self.log("=" * 60)
        
        # Páginas individuales
        print("\n🌐 RENDIMIENTO POR PÁGINA:")
        print("-" * 50)
        for name, result in self.results.items():
            if not name.endswith('_concurrent') and name != 'database_queries':
                avg_time = result['avg_time']
                success_rate = result['success_rate']
                
                if avg_time < 100:
                    performance = "🟢 EXCELENTE"
                elif avg_time < 300:
                    performance = "🟡 BUENO"
                elif avg_time < 800:
                    performance = "🟠 REGULAR"
                else:
                    performance = "🔴 LENTO"
                    
                print(f"{name:25} {avg_time:6.1f}ms  {success_rate:5.1f}%  {performance}")
                
        # Carga concurrente
        print("\n🚀 RENDIMIENTO BAJO CARGA:")
        print("-" * 50)
        for name, result in self.results.items():
            if name.endswith('_concurrent'):
                rps = result['requests_per_second']
                avg_time = result['avg_response_time']
                
                if rps > 30:
                    performance = "🟢 EXCELENTE"
                elif rps > 15:
                    performance = "🟡 BUENO"
                elif rps > 8:
                    performance = "🟠 REGULAR"
                else:
                    performance = "🔴 LENTO"
                    
                print(f"{name:25} {rps:6.1f} req/s  {avg_time:6.1f}ms  {performance}")
                
        # Base de datos
        if 'database_queries' in self.results:
            print("\n🗄️ RENDIMIENTO DE BASE DE DATOS:")
            print("-" * 50)
            db_results = self.results['database_queries']
            
            for query_name, data in db_results.items():
                avg_time = data['avg_time']
                count = data['avg_count']
                
                if avg_time < 5:
                    performance = "🟢 EXCELENTE"
                elif avg_time < 20:
                    performance = "🟡 BUENO"
                elif avg_time < 50:
                    performance = "🟠 REGULAR"
                else:
                    performance = "🔴 LENTO"
                    
                print(f"{query_name:25} {avg_time:6.1f}ms  {count:4.0f} reg  {performance}")
                
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        print("-" * 50)
        
        # Analizar páginas lentas
        slow_pages = []
        for name, result in self.results.items():
            if not name.endswith('_concurrent') and name != 'database_queries':
                if result['avg_time'] > 500:
                    slow_pages.append(name)
                    
        if slow_pages:
            print(f"• ⚠️  Optimizar páginas lentas: {', '.join(slow_pages)}")
            print("• 🔧 Considerar implementar caché")
            print("• 🗄️  Revisar consultas de base de datos")
        else:
            print("• ✅ Todas las páginas tienen buen rendimiento")
            
        # Analizar carga concurrente
        low_concurrent = []
        for name, result in self.results.items():
            if name.endswith('_concurrent'):
                if result['requests_per_second'] < 10:
                    low_concurrent.append(name)
                    
        if low_concurrent:
            print(f"• ⚠️  Mejorar capacidad concurrente: {', '.join(low_concurrent)}")
            print("• 🚀 Considerar optimizaciones de servidor")
        else:
            print("• ✅ Buena capacidad de manejo concurrente")
            
        # Analizar base de datos
        if 'database_queries' in self.results:
            slow_queries = []
            for query_name, data in self.results['database_queries'].items():
                if data['avg_time'] > 30:
                    slow_queries.append(query_name)
                    
            if slow_queries:
                print(f"• ⚠️  Optimizar consultas: {', '.join(slow_queries)}")
                print("• 🗄️  Considerar índices de base de datos")
            else:
                print("• ✅ Consultas de base de datos eficientes")
                
        print("\n✨ Pruebas de rendimiento completadas!")
        print(f"📊 Total de pruebas ejecutadas: {len(self.results)}")

if __name__ == "__main__":
    print("🔥 DULCE BIAS - PRUEBAS DE RENDIMIENTO BÁSICAS")
    print("=" * 60)
    print("📋 Utilizando el cliente de pruebas de Django")
    print("⚡ No requiere servidor externo ejecutándose")
    print()
    
    # Ejecutar pruebas
    tester = BasicPerformanceTests()
    tester.run_all_tests()
