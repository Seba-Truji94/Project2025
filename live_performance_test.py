#!/usr/bin/env python
"""
Pruebas de Rendimiento del Servidor en Vivo
Prueba el servidor Django que está ejecutándose
"""

import time
import urllib.request
import urllib.error
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class LiveServerPerformanceTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = {}
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_server_availability(self):
        """Verifica si el servidor está disponible"""
        try:
            response = urllib.request.urlopen(self.base_url, timeout=5)
            return response.getcode() == 200
        except:
            return False
            
    def test_url_performance(self, url_path, name, iterations=10):
        """Prueba rendimiento de una URL específica"""
        self.log(f"🔍 Probando {name} ({iterations} iteraciones)")
        
        full_url = f"{self.base_url}{url_path}"
        times = []
        status_codes = []
        
        for i in range(iterations):
            start_time = time.time()
            try:
                response = urllib.request.urlopen(full_url, timeout=30)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                status_code = response.getcode()
                
                times.append(response_time)
                status_codes.append(status_code)
                
                # Leer contenido para asegurar descarga completa
                content = response.read()
                content_size = len(content)
                
                status_icon = "✅" if status_code == 200 else "❌"
                print(f"  {status_icon} Iter {i+1}: {response_time:.2f}ms ({content_size} bytes)")
                
            except urllib.error.HTTPError as e:
                print(f"  ❌ Iter {i+1}: HTTP Error {e.code}")
                status_codes.append(e.code)
            except Exception as e:
                print(f"  ❌ Iter {i+1}: Error - {str(e)[:50]}")
                
        if times:
            result = {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'median_time': statistics.median(times),
                'success_rate': (status_codes.count(200) / len(status_codes)) * 100,
                'total_requests': len(times)
            }
            
            self.results[name] = result
            
            print(f"  📊 Promedio: {result['avg_time']:.2f}ms")
            print(f"  📊 Rango: {result['min_time']:.2f}ms - {result['max_time']:.2f}ms")
            print(f"  📊 Éxito: {result['success_rate']:.1f}%")
            print()
            
        return result if times else None
        
    def test_concurrent_load(self, url_path, name, concurrent_users=5, requests_per_user=3):
        """Prueba carga concurrente"""
        self.log(f"🚀 Carga concurrente: {name} ({concurrent_users} usuarios, {requests_per_user} req c/u)")
        
        full_url = f"{self.base_url}{url_path}"
        
        def make_requests(user_id):
            times = []
            for i in range(requests_per_user):
                start_time = time.time()
                try:
                    response = urllib.request.urlopen(full_url, timeout=30)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000
                    times.append(response_time)
                    
                    # Leer contenido
                    content = response.read()
                    
                except Exception as e:
                    print(f"  ❌ Usuario {user_id}, Req {i+1}: {str(e)[:30]}")
                    
            return times
            
        start_time = time.time()
        all_times = []
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_requests, i+1) for i in range(concurrent_users)]
            
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
                'max_response_time': max(all_times),
                'concurrent_users': concurrent_users
            }
            
            self.results[f"{name}_concurrent"] = result
            
            print(f"  📊 Total requests: {result['total_requests']}")
            print(f"  📊 Tiempo total: {result['total_time']:.2f}s")
            print(f"  📊 Throughput: {result['requests_per_second']:.2f} req/s")
            print(f"  📊 Tiempo promedio: {result['avg_response_time']:.2f}ms")
            print()
            
        return result if all_times else None
        
    def test_static_resources(self):
        """Prueba rendimiento de recursos estáticos"""
        self.log("📁 Probando recursos estáticos")
        
        static_resources = [
            '/static/css/styles.css',
            '/static/js/script.js',
            # Agregar más recursos según disponibilidad
        ]
        
        for resource in static_resources:
            try:
                start_time = time.time()
                response = urllib.request.urlopen(f"{self.base_url}{resource}", timeout=10)
                end_time = time.time()
                
                if response.getcode() == 200:
                    response_time = (end_time - start_time) * 1000
                    content_size = len(response.read())
                    print(f"  ✅ {resource}: {response_time:.2f}ms ({content_size} bytes)")
                else:
                    print(f"  ❌ {resource}: Status {response.getcode()}")
                    
            except Exception as e:
                print(f"  ⚠️  {resource}: No disponible")
                
        print()
        
    def run_comprehensive_test(self):
        """Ejecuta pruebas completas del servidor en vivo"""
        self.log("🚀 INICIANDO PRUEBAS DEL SERVIDOR EN VIVO")
        self.log("=" * 60)
        
        # Verificar servidor
        if not self.check_server_availability():
            print("❌ Servidor no disponible en", self.base_url)
            print("   Asegúrate de ejecutar: python manage.py runserver")
            return
            
        print(f"✅ Servidor detectado en {self.base_url}")
        print()
        
        # Pruebas de páginas principales
        pages = [
            ('/', 'Página de Inicio'),
            ('/productos/', 'Lista de Productos'),
            ('/support/', 'Centro de Soporte'),
            ('/support/admin/', 'Admin Soporte'),
            ('/support/admin/categories/', 'Admin Categorías'),
            ('/support/admin/statistics/', 'Admin Estadísticas'),
        ]
        
        for url_path, name in pages:
            self.test_url_performance(url_path, name, iterations=8)
            
        # Pruebas de recursos estáticos
        self.test_static_resources()
        
        # Pruebas de carga concurrente
        critical_pages = [
            ('/', 'Inicio'),
            ('/productos/', 'Productos'),
            ('/support/', 'Soporte')
        ]
        
        for url_path, name in critical_pages:
            self.test_concurrent_load(url_path, name, concurrent_users=3, requests_per_user=2)
            
        # Generar reporte
        self.generate_live_report()
        
    def generate_live_report(self):
        """Genera reporte de pruebas del servidor en vivo"""
        self.log("📋 REPORTE DEL SERVIDOR EN VIVO")
        self.log("=" * 60)
        
        # Rendimiento individual
        print("\n🌐 RENDIMIENTO DE PÁGINAS:")
        print("-" * 55)
        print(f"{'Página':<25} {'Tiempo':<10} {'Éxito':<8} {'Estado'}")
        print("-" * 55)
        
        for name, result in self.results.items():
            if not name.endswith('_concurrent'):
                avg_time = result['avg_time']
                success_rate = result['success_rate']
                
                if avg_time < 200 and success_rate >= 100:
                    status = "🟢 EXCELENTE"
                elif avg_time < 500 and success_rate >= 90:
                    status = "🟡 BUENO"
                elif avg_time < 1000 and success_rate >= 80:
                    status = "🟠 REGULAR"
                else:
                    status = "🔴 PROBLEMÁTICO"
                    
                print(f"{name:<25} {avg_time:>6.1f}ms   {success_rate:>5.1f}%   {status}")
                
        # Rendimiento concurrente
        print("\n🚀 CAPACIDAD DE CARGA:")
        print("-" * 55)
        print(f"{'Página':<25} {'Req/s':<8} {'T.Resp':<10} {'Estado'}")
        print("-" * 55)
        
        for name, result in self.results.items():
            if name.endswith('_concurrent'):
                rps = result['requests_per_second']
                avg_time = result['avg_response_time']
                
                if rps > 20 and avg_time < 500:
                    status = "🟢 EXCELENTE"
                elif rps > 10 and avg_time < 1000:
                    status = "🟡 BUENO"
                elif rps > 5 and avg_time < 2000:
                    status = "🟠 REGULAR"
                else:
                    status = "🔴 INSUFICIENTE"
                    
                clean_name = name.replace('_concurrent', '')
                print(f"{clean_name:<25} {rps:>6.1f}   {avg_time:>7.1f}ms   {status}")
                
        # Recomendaciones finales
        print("\n💡 RECOMENDACIONES:")
        print("-" * 55)
        
        total_pages = len([k for k in self.results.keys() if not k.endswith('_concurrent')])
        slow_pages = len([k for k, v in self.results.items() 
                         if not k.endswith('_concurrent') and v['avg_time'] > 800])
        
        if slow_pages == 0:
            print("• ✅ Excelente rendimiento general")
            print("• ✅ Todas las páginas responden rápidamente")
        elif slow_pages <= total_pages * 0.3:
            print(f"• ⚠️  {slow_pages} páginas necesitan optimización")
            print("• 🔧 Considerar caché y optimización de consultas")
        else:
            print(f"• 🔴 {slow_pages} páginas con problemas de rendimiento")
            print("• 🚨 Revisar servidor, base de datos y código")
            
        concurrent_issues = len([k for k, v in self.results.items() 
                               if k.endswith('_concurrent') and v['requests_per_second'] < 8])
        
        if concurrent_issues == 0:
            print("• ✅ Buena capacidad de manejo concurrente")
        else:
            print(f"• ⚠️  {concurrent_issues} páginas con problemas de concurrencia")
            print("• 🚀 Considerar optimizaciones de servidor")
            
        print("\n✨ Pruebas del servidor completadas!")

if __name__ == "__main__":
    print("🔥 DULCE BIAS - PRUEBAS DE SERVIDOR EN VIVO")
    print("=" * 60)
    print("🌐 Probando servidor Django en ejecución")
    print("⚠️  Asegúrate de que el servidor esté corriendo")
    print()
    
    tester = LiveServerPerformanceTest()
    tester.run_comprehensive_test()
