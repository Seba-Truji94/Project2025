#!/usr/bin/env python
"""
Monitor de Rendimiento Continuo para Dulce Bias
Ejecuta pruebas de rendimiento periódicas y genera alertas
"""

import time
import urllib.request
import urllib.error
import json
import os
from datetime import datetime, timedelta
import threading

class PerformanceMonitor:
    def __init__(self, base_url="http://127.0.0.1:8000", check_interval=60):
        self.base_url = base_url
        self.check_interval = check_interval  # segundos
        self.monitoring = False
        self.alerts = []
        self.performance_history = []
        
        # Umbrales de alerta
        self.thresholds = {
            'response_time_warning': 100,    # ms
            'response_time_critical': 500,   # ms
            'success_rate_warning': 95,      # %
            'success_rate_critical': 90,     # %
        }
        
    def log(self, message, level="INFO"):
        """Log con timestamp y nivel"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def test_url(self, url_path, max_retries=3):
        """Prueba una URL específica"""
        full_url = f"{self.base_url}{url_path}"
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                response = urllib.request.urlopen(full_url, timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                status_code = response.getcode()
                content_length = len(response.read())
                
                return {
                    'success': True,
                    'response_time': response_time,
                    'status_code': status_code,
                    'content_length': content_length,
                    'attempt': attempt + 1
                }
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': str(e),
                        'response_time': None,
                        'status_code': None,
                        'attempt': attempt + 1
                    }
                time.sleep(1)  # Esperar antes del siguiente intento
                
    def check_performance(self):
        """Ejecuta un chequeo completo de rendimiento"""
        timestamp = datetime.now()
        
        # URLs críticas a monitorear
        critical_urls = [
            ('/', 'Página de Inicio'),
            ('/productos/', 'Lista de Productos'),
            ('/support/', 'Centro de Soporte'),
        ]
        
        results = {
            'timestamp': timestamp.isoformat(),
            'overall_status': 'OK',
            'issues': [],
            'pages': {}
        }
        
        total_success = 0
        total_checks = 0
        
        for url_path, name in critical_urls:
            result = self.test_url(url_path)
            results['pages'][name] = result
            
            total_checks += 1
            if result['success']:
                total_success += 1
                
                # Verificar umbrales de tiempo de respuesta
                response_time = result['response_time']
                if response_time > self.thresholds['response_time_critical']:
                    issue = f"🔴 CRÍTICO: {name} - {response_time:.1f}ms"
                    results['issues'].append(issue)
                    results['overall_status'] = 'CRITICAL'
                    
                elif response_time > self.thresholds['response_time_warning']:
                    issue = f"🟡 ADVERTENCIA: {name} - {response_time:.1f}ms"
                    results['issues'].append(issue)
                    if results['overall_status'] == 'OK':
                        results['overall_status'] = 'WARNING'
            else:
                issue = f"🔴 ERROR: {name} - {result.get('error', 'Fallo desconocido')}"
                results['issues'].append(issue)
                results['overall_status'] = 'CRITICAL'
                
        # Verificar tasa de éxito general
        success_rate = (total_success / total_checks) * 100
        results['success_rate'] = success_rate
        
        if success_rate < self.thresholds['success_rate_critical']:
            results['issues'].append(f"🔴 CRÍTICO: Tasa de éxito {success_rate:.1f}%")
            results['overall_status'] = 'CRITICAL'
        elif success_rate < self.thresholds['success_rate_warning']:
            results['issues'].append(f"🟡 ADVERTENCIA: Tasa de éxito {success_rate:.1f}%")
            if results['overall_status'] == 'OK':
                results['overall_status'] = 'WARNING'
                
        return results
        
    def process_results(self, results):
        """Procesa y muestra los resultados"""
        status = results['overall_status']
        timestamp = datetime.fromisoformat(results['timestamp'])
        
        # Log del estado general
        if status == 'OK':
            self.log("✅ Sistema funcionando correctamente", "INFO")
        elif status == 'WARNING':
            self.log("⚠️ Sistema con advertencias", "WARNING")
        elif status == 'CRITICAL':
            self.log("🔴 Sistema con problemas críticos", "CRITICAL")
            
        # Mostrar detalles de las páginas
        for page_name, page_result in results['pages'].items():
            if page_result['success']:
                rt = page_result['response_time']
                size = page_result['content_length']
                
                if rt < self.thresholds['response_time_warning']:
                    status_icon = "🟢"
                elif rt < self.thresholds['response_time_critical']:
                    status_icon = "🟡"
                else:
                    status_icon = "🔴"
                    
                self.log(f"  {status_icon} {page_name}: {rt:.1f}ms ({size} bytes)")
            else:
                self.log(f"  🔴 {page_name}: ERROR - {page_result.get('error', 'Fallo')}")
                
        # Mostrar issues si existen
        if results['issues']:
            self.log("⚠️ PROBLEMAS DETECTADOS:")
            for issue in results['issues']:
                self.log(f"  {issue}")
                
        # Agregar al historial
        self.performance_history.append(results)
        
        # Mantener solo las últimas 24 horas de datos
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.performance_history = [
            r for r in self.performance_history 
            if datetime.fromisoformat(r['timestamp']) > cutoff_time
        ]
        
    def generate_summary_report(self):
        """Genera un reporte resumen de las últimas horas"""
        if not self.performance_history:
            return "No hay datos de rendimiento disponibles"
            
        recent_data = self.performance_history[-10:]  # Últimas 10 mediciones
        
        # Estadísticas generales
        total_checks = len(recent_data)
        ok_checks = len([r for r in recent_data if r['overall_status'] == 'OK'])
        warning_checks = len([r for r in recent_data if r['overall_status'] == 'WARNING'])
        critical_checks = len([r for r in recent_data if r['overall_status'] == 'CRITICAL'])
        
        availability = (ok_checks / total_checks) * 100
        
        # Tiempos de respuesta promedio
        page_stats = {}
        for result in recent_data:
            for page_name, page_data in result['pages'].items():
                if page_data['success']:
                    if page_name not in page_stats:
                        page_stats[page_name] = []
                    page_stats[page_name].append(page_data['response_time'])
                    
        report = f"""
📊 REPORTE DE MONITOREO (Últimas {total_checks} mediciones)
{'='*60}
⏰ Período: {datetime.fromisoformat(recent_data[0]['timestamp']).strftime('%H:%M')} - {datetime.fromisoformat(recent_data[-1]['timestamp']).strftime('%H:%M')}

📈 DISPONIBILIDAD GENERAL: {availability:.1f}%
  🟢 OK: {ok_checks} checks
  🟡 Advertencias: {warning_checks} checks  
  🔴 Críticos: {critical_checks} checks

⚡ RENDIMIENTO PROMEDIO:"""

        for page_name, times in page_stats.items():
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                if avg_time < self.thresholds['response_time_warning']:
                    status_icon = "🟢"
                elif avg_time < self.thresholds['response_time_critical']:
                    status_icon = "🟡"
                else:
                    status_icon = "🔴"
                    
                report += f"\n  {status_icon} {page_name}: {avg_time:.1f}ms (rango: {min_time:.1f}-{max_time:.1f}ms)"
                
        return report
        
    def start_monitoring(self):
        """Inicia el monitoreo continuo"""
        self.monitoring = True
        self.log("🚀 Iniciando monitoreo continuo de rendimiento")
        self.log(f"📊 Intervalo de chequeo: {self.check_interval} segundos")
        self.log(f"🎯 Monitoreando: {self.base_url}")
        
        check_count = 0
        
        try:
            while self.monitoring:
                check_count += 1
                self.log(f"🔍 Ejecutando chequeo #{check_count}")
                
                # Ejecutar chequeo de rendimiento
                results = self.check_performance()
                self.process_results(results)
                
                # Mostrar reporte cada 10 chequeos
                if check_count % 10 == 0:
                    print(self.generate_summary_report())
                    
                # Esperar hasta el siguiente chequeo
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.log("⏹️ Monitoreo detenido por el usuario")
        except Exception as e:
            self.log(f"❌ Error en monitoreo: {str(e)}", "ERROR")
        finally:
            self.monitoring = False
            
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.monitoring = False
        
    def save_performance_data(self, filename=None):
        """Guarda los datos de rendimiento en un archivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_data_{timestamp}.json"
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.performance_history, f, indent=2, ensure_ascii=False)
            self.log(f"💾 Datos guardados en: {filename}")
            return True
        except Exception as e:
            self.log(f"❌ Error guardando datos: {str(e)}", "ERROR")
            return False

def main():
    print("🔥 DULCE BIAS - MONITOR DE RENDIMIENTO CONTINUO")
    print("=" * 60)
    print("⚠️  Presiona Ctrl+C para detener el monitoreo")
    print("📊 El reporte resumen se muestra cada 10 chequeos")
    print()
    
    # Configuración del monitor
    monitor = PerformanceMonitor(
        base_url="http://127.0.0.1:8000",
        check_interval=30  # 30 segundos entre chequeos
    )
    
    # Verificar servidor antes de comenzar
    try:
        response = urllib.request.urlopen(monitor.base_url, timeout=5)
        print(f"✅ Servidor detectado en {monitor.base_url}")
    except:
        print(f"❌ Servidor no disponible en {monitor.base_url}")
        print("   Asegúrate de ejecutar: python manage.py runserver")
        return
        
    # Iniciar monitoreo
    try:
        monitor.start_monitoring()
    finally:
        # Guardar datos al terminar
        if monitor.performance_history:
            monitor.save_performance_data()
            print(monitor.generate_summary_report())
            print("\n✨ Monitoreo finalizado. Datos guardados.")

if __name__ == "__main__":
    main()
