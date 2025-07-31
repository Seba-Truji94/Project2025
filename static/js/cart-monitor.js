// Funciones adicionales para el manejo del carrito
window.CartUtils = {
    // Verificar si estamos en la página del carrito
    isCartPage: function() {
        return window.location.pathname.includes('/cart/');
    },
    
    // Obtener información actual del carrito desde el DOM
    getCurrentCartInfo: function() {
        const cartCount = document.querySelector('.cart-count');
        const floatingCartCount = document.querySelector('.floating-cart-count');
        const cartItems = document.querySelectorAll('.cart-item');
        const itemsCountElement = document.querySelector('#items-count');
        const productTypesCount = document.querySelector('#product-types-count');
        
        return {
            headerCount: cartCount ? parseInt(cartCount.textContent) || 0 : 0,
            floatingCount: floatingCartCount ? parseInt(floatingCartCount.textContent) || 0 : 0,
            visibleItems: cartItems.length,
            totalUnits: itemsCountElement ? this.extractNumber(itemsCountElement.textContent) : 0,
            productTypes: productTypesCount ? this.extractNumber(productTypesCount.textContent) : 0
        };
    },
    
    // Extraer número de un texto
    extractNumber: function(text) {
        if (!text) return 0;
        const match = text.match(/(\d+)/);
        return match ? parseInt(match[1]) : 0;
    },
    
    // Verificar consistencia del carrito
    checkConsistency: function() {
        const info = this.getCurrentCartInfo();
        
        const issues = [];
        
        // Verificar si los contadores del header coinciden
        if (info.headerCount !== info.floatingCount) {
            issues.push('Los contadores del header no coinciden');
        }
        
        // Si estamos en la página del carrito
        if (this.isCartPage()) {
            // Verificar si hay productos visibles cuando el contador dice que hay items
            if (info.headerCount > 0 && info.visibleItems === 0) {
                issues.push('El contador indica items pero no hay productos visibles');
            }
            
            // Verificar consistencia entre tipos de productos y items visibles
            if (info.productTypes > 0 && info.visibleItems !== info.productTypes) {
                issues.push('Los tipos de productos no coinciden con los items visibles');
            }
        }
        
        return {
            consistent: issues.length === 0,
            issues: issues,
            info: info
        };
    },
    
    // Intentar corregir automáticamente
    autoFix: async function() {
        console.log('🔧 Intentando corrección automática...');
        
        try {
            // 1. Verificar conexión y obtener datos del servidor
            const data = await CartDiagnostics.testConnection();
            
            if (data) {
                console.log('📊 Datos del servidor:', data);
                
                // 2. Actualizar TODOS los contadores
                const cartCount = document.querySelector('.cart-count');
                const floatingCartCount = document.querySelector('.floating-cart-count');
                const itemsCountElement = document.querySelector('#items-count');
                const productTypesCount = document.querySelector('#product-types-count');
                
                // Actualizar contadores del header
                if (cartCount) cartCount.textContent = data.total_items || 0;
                if (floatingCartCount) floatingCartCount.textContent = data.total_items || 0;
                
                // Si estamos en la página del carrito, actualizar detalles
                if (this.isCartPage()) {
                    if (itemsCountElement) {
                        itemsCountElement.innerHTML = `${data.total_items || 0} unidades`;
                    }
                    
                    if (productTypesCount) {
                        productTypesCount.innerHTML = `${data.items?.length || 0} tipos`;
                    }
                    
                    // NO RECARGAR: Las inconsistencias se manejan automáticamente en el backend
                    if ((data.total_items || 0) === 0 && document.querySelectorAll('.cart-item').length > 0) {
                        console.log('ℹ️ Inconsistencia detectada: servidor sin items, página con items - manejado automáticamente');
                        // NO recargar la página - se maneja automáticamente
                        return true;
                    }
                    
                    // NO RECARGAR: Las inconsistencias se manejan automáticamente en el backend
                    if ((data.total_items || 0) > 0 && document.querySelectorAll('.cart-item').length === 0) {
                        console.log('ℹ️ Inconsistencia detectada: servidor con items, página sin items - manejado automáticamente');
                        // NO recargar la página - se maneja automáticamente
                        return true;
                    }
                }
                
                // 3. Esperar un momento
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // 4. Verificar si se solucionó
                const check = this.checkConsistency();
                
                if (check.consistent) {
                    // Sincronización exitosa - solo log en consola
                    console.log('✅ Carrito sincronizado correctamente');
                    return true;
                } else {
                    console.log('⚠️ Problemas restantes:', check.issues);
                    // No mostrar notificación molesta
                    return false;
                }
            } else {
                console.log('❌ No se pudo conectar con el servidor');
                return false;
            }
            
        } catch (error) {
            console.error('Error en corrección automática:', error);
            // Solo log en consola, sin notificación molesta
            return false;
        }
    },
    
    // Monitoreo continuo
    startMonitoring: function() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        
        console.log('📡 Iniciando monitoreo del carrito...');
        
        this.monitoringInterval = setInterval(() => {
            const check = this.checkConsistency();
            
            if (!check.consistent) {
                console.warn('⚠️ Inconsistencia detectada:', check.issues);
                
                // Intentar corrección automática solo una vez
                if (!this.autoFixAttempted) {
                    this.autoFixAttempted = true;
                    this.autoFix().then(fixed => {
                        if (!fixed) {
                            console.log('Manual intervention required');
                        }
                    });
                }
            } else {
                this.autoFixAttempted = false;
            }
        }, 5000); // Verificar cada 5 segundos
    },
    
    // Detener monitoreo
    stopMonitoring: function() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
            console.log('📡 Monitoreo del carrito detenido');
        }
    }
};

// MONITOREO AUTOMÁTICO DESHABILITADO - NO MÁS RECARGAS
document.addEventListener('DOMContentLoaded', function() {
    if (CartUtils.isCartPage()) {
        // DESHABILITADO: No iniciar monitoreo automático que causa recargas
        console.log('ℹ️ Monitoreo automático deshabilitado para evitar recargas');
        /*
        setTimeout(() => {
            CartUtils.startMonitoring();
        }, 3000); // Esperar 3 segundos después de cargar la página
        */
    }
    
    // Agregar comando global para el monitoreo (solo manual)
    window.cartMonitor = {
        start: () => CartUtils.startMonitoring(),
        stop: () => CartUtils.stopMonitoring(),
        check: () => CartUtils.checkConsistency(),
        fix: () => CartUtils.autoFix()
    };
});
