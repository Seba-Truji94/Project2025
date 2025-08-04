#!/usr/bin/env python
"""
Verificación completa de URLs problemáticas
Busca y reporta todas las URLs que podrían causar errores 404
"""
import os
import re
import glob

def scan_file_for_urls(filepath):
    """Escanea un archivo en busca de URLs problemáticas"""
    problems = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Patrones de URLs problemáticas
        patterns = [
            (r'/management/stock/movement/', 'URL incorrecta: usar /movimiento/'),
            (r'/management/purchase-orders/', 'URL no implementada: sistema de órdenes'),
            (r'stock/movement', 'Referencia incorrecta de stock movement'),
            (r'purchase-orders', 'Referencia a órdenes no implementadas')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line):
                    problems.append({
                        'line': i,
                        'content': line.strip(),
                        'issue': description,
                        'pattern': pattern
                    })
    except Exception as e:
        pass
    
    return problems

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DE URLs PROBLEMÁTICAS")
    print("=" * 60)
    
    # Archivos a escanear
    file_patterns = [
        'management/templates/**/*.html',
        'management/urls.py',
        'management/views.py',
        '**/*.py',
        '**/*.html'
    ]
    
    all_problems = {}
    total_issues = 0
    
    for pattern in file_patterns:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if os.path.isfile(filepath):
                problems = scan_file_for_urls(filepath)
                if problems:
                    all_problems[filepath] = problems
                    total_issues += len(problems)
    
    # Reportar problemas
    if all_problems:
        print(f"❌ PROBLEMAS ENCONTRADOS: {total_issues}")
        print("=" * 60)
        
        for filepath, problems in all_problems.items():
            print(f"\n📁 {filepath}")
            for problem in problems:
                print(f"   Línea {problem['line']}: {problem['issue']}")
                print(f"   → {problem['content'][:100]}...")
    else:
        print("✅ NO SE ENCONTRARON PROBLEMAS DE URLs")
        print("=" * 60)
        print("🎉 Todas las URLs están correctamente configuradas")
    
    # Verificar configuración de URLs
    print(f"\n🔧 VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 60)
    
    # Verificar management/urls.py
    urls_file = 'management/urls.py'
    if os.path.exists(urls_file):
        with open(urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('stock/movimiento/', 'URL de movimiento de stock'),
            ('stock/alertas/', 'URL de alertas de stock'),
            ('stock/reporte/', 'URL de reporte de stock'),
            ('proveedores/', 'URL de proveedores')
        ]
        
        for url, description in checks:
            if url in content:
                print(f"✅ {description}: Configurada")
            else:
                print(f"❌ {description}: NO configurada")
    
    print(f"\n💡 INSTRUCCIONES DE USO")
    print("=" * 60)
    print("1. Ejecutar servidor: python run_server.py")
    print("2. O usar batch: run_server.bat") 
    print("3. URLs principales:")
    print("   • Panel: http://127.0.0.1:8002/management/")
    print("   • Alertas: http://127.0.0.1:8002/management/stock/alertas/")
    print("   • Reportes: http://127.0.0.1:8002/management/stock/reporte/")
    print("   • Movimientos: http://127.0.0.1:8002/management/stock/movimiento/")

if __name__ == '__main__':
    main()
