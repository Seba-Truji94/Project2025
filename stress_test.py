#!/usr/bin/env python
"""
Pruebas de Estrés Avanzadas para Dulce Bias
Simula cargas pesadas y mide tiempos bajo presión
"""

import time
import urllib.request
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class StressTestSuite:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = {}
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def heavy_load_test(self, url_path, name, concurrent_users=20, requests_per_user=10, duration=60):
        """Prueba de carga pesada sostenida"""
        self.log(f"🔥 PRUEBA DE ESTRÉS: {name}")
        self.log(f"   👥 {concurrent_users} usuarios concurrentes")
        self.log(f"   📦 {requests_per_user} requests por usuario") 
        self.log(f"   ⏱️ Duración: {duration} segundos")
        
        full_url = f"{self.base_url}{url_path}"
        all_times = []
        errors = 0
        start_time = time.time()
        
        def make_sustained_requests(user_id):
            user_times = []
            user_errors = 0
            
            while time.time() - start_time < duration:
                request_start = time.time()
                try:
                    response = urllib.request.urlopen(full_url, timeout=30)
                    request_end = time.time()
                    
                    response_time = (request_end - request_start) * 1000
                    user_times.append(response_time)
                    
                    # Leer contenido para simular usuario real
                    content = response.read()
                    
                except Exception as e:
                    user_errors += 1
                    
                # Pausa pequeña entre requests
                time.sleep(0.1)
                
            return user_times, user_errors
            
        # Ejecutar prueba con múltiples threads
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_sustained_requests, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    times, user_errors = future.result()
                    all_times.extend(times)
                    errors += user_errors
                except Exception as e:
                    print(f"  ❌ Error en thread: {str(e)}")
                    
        total_time = time.time() - start_time
        total_requests = len(all_times)
        
        if all_times:
            result = {
                'total_requests': total_requests,
                'total_errors': errors,
                'success_rate': ((total_requests - errors) / total_requests) * 100,
                'total_time': total_time,
                'requests_per_second': total_requests / total_time,
                'avg_response_time': statistics.mean(all_times),
                'min_response_time': min(all_times),
                'max_response_time': max(all_times),
                'p95_response_time': statistics.quantiles(all_times, n=20)[18] if len(all_times) > 20 else max(all_times),
                'p99_response_time': statistics.quantiles(all_times, n=100)[98] if len(all_times) > 100 else max(all_times),
            }
            
            self.results[f"{name}_stress"] = result
            
            print(f"  📊 Total requests: {total_requests}")
            print(f"  📊 Errores: {errors}")
            print(f"  📊 Tasa de éxito: {result['success_rate']:.1f}%")
            print(f"  📊 Throughput: {result['requests_per_second']:.1f} req/s")
            print(f"  📊 Tiempo promedio: {result['avg_response_time']:.1f}ms")
            print(f"  📊 P95 (95%): {result['p95_response_time']:.1f}ms")
            print(f"  📊 P99 (99%): {result['p99_response_time']:.1f}ms")
            print(f"  📊 Máximo: {result['max_response_time']:.1f}ms")
            print()
            
        return result if all_times else None
        
    def burst_test(self, url_path, name, burst_size=50, bursts=5, interval=10):
        """Prueba de ráfagas de tráfico"""
        self.log(f"💥 PRUEBA DE RÁFAGAS: {name}")
        self.log(f"   📦 {burst_size} requests por ráfaga")
        self.log(f"   🔄 {bursts} ráfagas con {interval}s de intervalo")
        
        full_url = f"{self.base_url}{url_path}"
        burst_results = []
        
        for burst_num in range(bursts):
            self.log(f"   🚀 Ejecutando ráfaga {burst_num + 1}/{bursts}")
            
            burst_times = []
            burst_start = time.time()
            
            def single_request():
                start = time.time()
                try:
                    response = urllib.request.urlopen(full_url, timeout=30)
                    end = time.time()
                    content = response.read()  # Simular lectura completa
                    return (end - start) * 1000
                except:
                    return None
                    
            # Ejecutar ráfaga
            with ThreadPoolExecutor(max_workers=burst_size) as executor:
                futures = [executor.submit(single_request) for _ in range(burst_size)]
                
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        burst_times.append(result)
                        
            burst_duration = time.time() - burst_start
            
            if burst_times:
                burst_result = {
                    'burst_number': burst_num + 1,
                    'successful_requests': len(burst_times),
                    'burst_duration': burst_duration,
                    'burst_rps': len(burst_times) / burst_duration,
                    'avg_time': statistics.mean(burst_times),
                    'max_time': max(burst_times),
                    'min_time': min(burst_times)
                }
                burst_results.append(burst_result)
                
                print(f"    ✅ {len(burst_times)}/{burst_size} exitosos")
                print(f"    ⚡ {burst_result['burst_rps']:.1f} req/s")
                print(f"    📊 Promedio: {burst_result['avg_time']:.1f}ms")
                print(f"    📊 Máximo: {burst_result['max_time']:.1f}ms")
                
            # Esperar antes de la siguiente ráfaga
            if burst_num < bursts - 1:
                print(f"    ⏳ Esperando {interval}s antes de la siguiente ráfaga...")
                time.sleep(interval)
                
        # Resumen de ráfagas
        if burst_results:
            avg_rps = statistics.mean([b['burst_rps'] for b in burst_results])
            avg_response = statistics.mean([b['avg_time'] for b in burst_results])
            max_response = max([b['max_time'] for b in burst_results])
            
            summary = {
                'total_bursts': len(burst_results),
                'avg_burst_rps': avg_rps,
                'avg_response_time': avg_response,
                'max_response_time': max_response,
                'burst_details': burst_results
            }
            
            self.results[f"{name}_burst"] = summary
            
            print(f"  📊 RESUMEN DE RÁFAGAS:")
            print(f"    Promedio RPS: {avg_rps:.1f}")
            print(f"    Tiempo promedio: {avg_response:.1f}ms")
            print(f"    Tiempo máximo: {max_response:.1f}ms")
            print()
            
        return summary if burst_results else None
        
    def endurance_test(self, url_path, name, duration_minutes=5, steady_rps=10):
        """Prueba de resistencia de larga duración"""
        self.log(f"🏃 PRUEBA DE RESISTENCIA: {name}")
        self.log(f"   ⏱️ Duración: {duration_minutes} minutos")
        self.log(f"   📊 Carga sostenida: {steady_rps} req/s")
        
        full_url = f"{self.base_url}{url_path}"
        duration_seconds = duration_minutes * 60
        interval = 1.0 / steady_rps
        
        times = []
        errors = 0
        start_time = time.time()
        
        def make_request():
            try:
                request_start = time.time()
                response = urllib.request.urlopen(full_url, timeout=30)
                request_end = time.time()
                content = response.read()
                return (request_end - request_start) * 1000
            except:
                return None
                
        request_count = 0
        last_report = start_time
        
        while time.time() - start_time < duration_seconds:
            result = make_request()
            if result is not None:
                times.append(result)
            else:
                errors += 1
                
            request_count += 1
            
            # Reporte cada minuto
            if time.time() - last_report >= 60:
                elapsed = time.time() - start_time
                current_rps = request_count / elapsed
                current_avg = statistics.mean(times[-60:]) if len(times) >= 60 else statistics.mean(times)
                
                print(f"    📊 {elapsed/60:.1f}min - RPS: {current_rps:.1f}, Avg: {current_avg:.1f}ms")
                last_report = time.time()
                
            # Mantener ritmo constante
            time.sleep(interval)
            
        total_time = time.time() - start_time
        
        if times:
            result = {
                'duration_minutes': duration_minutes,
                'total_requests': len(times),
                'total_errors': errors,
                'success_rate': (len(times) / (len(times) + errors)) * 100,
                'actual_rps': len(times) / total_time,
                'target_rps': steady_rps,
                'avg_response_time': statistics.mean(times),
                'min_response_time': min(times),
                'max_response_time': max(times),
                'response_stability': statistics.stdev(times) if len(times) > 1 else 0
            }
            
            self.results[f"{name}_endurance"] = result
            
            print(f"  📊 RESULTADOS DE RESISTENCIA:")
            print(f"    Total requests: {result['total_requests']}")
            print(f"    Tasa de éxito: {result['success_rate']:.1f}%")
            print(f"    RPS real: {result['actual_rps']:.1f}")
            print(f"    Tiempo promedio: {result['avg_response_time']:.1f}ms")
            print(f"    Estabilidad (stdev): {result['response_stability']:.1f}ms")
            print()
            
        return result if times else None
        
    def run_comprehensive_stress_tests(self):
        """Ejecuta suite completa de pruebas de estrés"""
        self.log("🔥 INICIANDO PRUEBAS DE ESTRÉS AVANZADAS")
        self.log("=" * 60)
        
        # Verificar servidor
        try:
            response = urllib.request.urlopen(self.base_url, timeout=5)
            print(f"✅ Servidor detectado en {self.base_url}")
        except:
            print(f"❌ Servidor no disponible en {self.base_url}")
            return
            
        print()
        
        # Pruebas de estrés en páginas críticas
        critical_pages = [
            ('/', 'Página de Inicio'),
            ('/productos/', 'Lista de Productos'),
        ]
        
        for url_path, name in critical_pages:
            # Prueba de carga pesada
            self.heavy_load_test(url_path, name, concurrent_users=15, duration=30)
            
            # Prueba de ráfagas
            self.burst_test(url_path, name, burst_size=30, bursts=3, interval=5)
            
        # Prueba de resistencia en página principal
        self.endurance_test('/', 'Página Principal', duration_minutes=2, steady_rps=8)
        
        # Generar reporte final
        self.generate_stress_report()
        
    def generate_stress_report(self):
        """Genera reporte de pruebas de estrés"""
        self.log("📋 REPORTE DE PRUEBAS DE ESTRÉS")
        self.log("=" * 60)
        
        print("\n🔥 RESULTADOS DE ESTRÉS:")
        print("-" * 50)
        
        for test_name, result in self.results.items():
            if test_name.endswith('_stress'):
                page_name = test_name.replace('_stress', '')
                rps = result['requests_per_second']
                avg_time = result['avg_response_time']
                max_time = result['max_response_time']
                success_rate = result['success_rate']
                
                if avg_time < 100 and success_rate > 95:
                    status = "🟢 EXCELENTE"
                elif avg_time < 500 and success_rate > 90:
                    status = "🟡 BUENO"
                elif avg_time < 2000 and success_rate > 80:
                    status = "🟠 REGULAR"
                else:
                    status = "🔴 PROBLEMÁTICO"
                    
                print(f"{page_name}:")
                print(f"  RPS: {rps:.1f} | Promedio: {avg_time:.1f}ms")
                print(f"  Máximo: {max_time:.1f}ms | Éxito: {success_rate:.1f}%")
                print(f"  Estado: {status}")
                print()
                
        # Evaluación general
        print("💡 EVALUACIÓN GENERAL:")
        print("-" * 50)
        
        stress_tests = [r for k, r in self.results.items() if k.endswith('_stress')]
        if stress_tests:
            avg_success = statistics.mean([r['success_rate'] for r in stress_tests])
            avg_response = statistics.mean([r['avg_response_time'] for r in stress_tests])
            max_rps = max([r['requests_per_second'] for r in stress_tests])
            
            if avg_success > 95 and avg_response < 200:
                print("🟢 Tu sitio maneja EXCELENTEMENTE el estrés")
                print("✅ Listo para tráfico alto en producción")
            elif avg_success > 90 and avg_response < 500:
                print("🟡 Tu sitio maneja BIEN el estrés")
                print("⚠️ Considerar optimizaciones para picos de tráfico")
            else:
                print("🔴 Tu sitio necesita optimización para cargas altas")
                print("🔧 Revisar servidor, base de datos y código")
                
            print(f"\n📊 Métricas bajo estrés:")
            print(f"  Tasa de éxito promedio: {avg_success:.1f}%")
            print(f"  Tiempo de respuesta promedio: {avg_response:.1f}ms")
            print(f"  Capacidad máxima: {max_rps:.1f} req/s")
            
        print("\n✨ Pruebas de estrés completadas!")

if __name__ == "__main__":
    print("🔥 DULCE BIAS - PRUEBAS DE ESTRÉS AVANZADAS")
    print("=" * 60)
    print("⚠️  Estas pruebas someten el servidor a cargas intensas")
    print("🎯 Objetivo: Verificar comportamiento bajo presión")
    print()
    
    tester = StressTestSuite()
    tester.run_comprehensive_stress_tests()
