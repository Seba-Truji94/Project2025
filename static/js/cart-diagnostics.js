// Funciones de diagnóstico del carrito
window.CartDiagnostics = {
    // Verificar estado del carrito
    checkCartStatus: function() {
        console.log('🔍 Verificando estado del carrito...');
        
        // Obtener contador del header
        const cartCount = document.querySelector('.cart-count');
        const floatingCartCount = document.querySelector('.floating-cart-count');
        
        console.log('📊 Contadores visibles:');
        console.log('- Header:', cartCount ? cartCount.textContent : 'No encontrado');
        console.log('- Flotante:', floatingCartCount ? floatingCartCount.textContent : 'No encontrado');
        
        // Verificar items visibles en la página
        const cartItems = document.querySelectorAll('.cart-item');
        console.log('📦 Items visibles en página:', cartItems.length);
        
        // Verificar totales
        const itemsCountElement = document.querySelector('#items-count');
        const productTypesCount = document.querySelector('#product-types-count');
        
        if (itemsCountElement) {
            console.log('🧮 Total items:', itemsCountElement.textContent);
        }
        
        if (productTypesCount) {
            console.log('🏷️  Tipos de productos:', productTypesCount.textContent);
        }
        
        return {
            headerCount: cartCount ? cartCount.textContent : 0,
            floatingCount: floatingCartCount ? floatingCartCount.textContent : 0,
            visibleItems: cartItems.length,
            totalItems: itemsCountElement ? itemsCountElement.textContent : 'N/A',
            productTypes: productTypesCount ? productTypesCount.textContent : 'N/A'
        };
    },
    
    // Limpiar caché del navegador
    clearCache: function() {
        console.log('🧹 Limpiando caché del navegador...');
        
        // Limpiar localStorage
        localStorage.clear();
        
        // Limpiar sessionStorage
        sessionStorage.clear();
        
        console.log('✅ Caché limpiado');
        
        // NO recargar página automáticamente
        console.log('ℹ️ Recarga manual disponible si es necesaria');
    },
    
    // Verificar conexión con el servidor
    testConnection: async function() {
        console.log('🌐 Probando conexión con el servidor...');
        
        try {
            const response = await fetch('/cart/summary/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Conexión exitosa:', data);
                return data;
            } else {
                console.log('❌ Error de respuesta:', response.status);
                return null;
            }
        } catch (error) {
            console.log('❌ Error de conexión:', error);
            return null;
        }
    },
    
    // Sincronizar carrito
    syncCart: async function() {
        console.log('🔄 Sincronizando carrito...');
        
        const data = await this.testConnection();
        if (data) {
            // Actualizar contadores
            const cartCount = document.querySelector('.cart-count');
            const floatingCartCount = document.querySelector('.floating-cart-count');
            const itemsCountElement = document.querySelector('#items-count');
            const productTypesCount = document.querySelector('#product-types-count');
            
            if (cartCount) cartCount.textContent = data.total_items || 0;
            if (floatingCartCount) floatingCartCount.textContent = data.total_items || 0;
            
            // Actualizar totales si estamos en la página del carrito
            if (itemsCountElement) {
                itemsCountElement.innerHTML = `${data.total_items || 0} unidades`;
            }
            
            console.log('✅ Carrito sincronizado:', {
                totalItems: data.total_items,
                itemsInCart: data.items?.length || 0
            });
            
            // Mostrar notificación de éxito
            this.showNotification('✅ Carrito sincronizado correctamente', 'success');
        } else {
            console.log('❌ No se pudo sincronizar el carrito');
            this.showNotification('❌ Error al sincronizar el carrito', 'error');
        }
    },
    
    // Mostrar notificación al usuario
    showNotification: function(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remover después de 4 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    },
    
    // Diagnóstico completo
    fullDiagnosis: async function() {
        console.log('🏥 DIAGNÓSTICO COMPLETO DEL CARRITO');
        console.log('=====================================');
        
        // 1. Estado visual
        const status = this.checkCartStatus();
        
        // 2. Conexión al servidor
        await this.testConnection();
        
        // 3. Información del usuario
        console.log('👤 Usuario autenticado:', document.body.dataset.userAuthenticated === 'true');
        
        // 4. Cookies y sesión
        console.log('🍪 Cookies disponibles:', document.cookie.length > 0);
        
        return status;
    }
};

// Auto-ejecutar diagnóstico si hay problemas aparentes
document.addEventListener('DOMContentLoaded', function() {
    const cartCount = document.querySelector('.cart-count');
    const cartItems = document.querySelectorAll('.cart-item');
    const isCartPage = window.location.pathname.includes('/cart/');
    
    // Solo ejecutar diagnóstico en la página del carrito
    if (isCartPage) {
        const headerCount = cartCount ? parseInt(cartCount.textContent) : 0;
        const visibleItems = cartItems.length;
        
        console.log('🔍 Verificación automática del carrito:', {
            headerCount,
            visibleItems,
            location: window.location.pathname
        });
        
        // Si el contador del header dice que hay items pero no se ven items en la página
        if (headerCount > 0 && visibleItems === 0) {
            console.warn('⚠️ Posible problema de carrito detectado. Ejecuta CartDiagnostics.fullDiagnosis() para más información');
            
            // ALERTA DESHABILITADA - No mostrar mensaje molesto al usuario
            // La inconsistencia se maneja automáticamente en el backend
            /*
            // Esperar un momento para que la página cargue completamente
            setTimeout(() => {
                // Verificar nuevamente después de la carga
                const updatedItems = document.querySelectorAll('.cart-item');
                if (updatedItems.length === 0 && headerCount > 0) {
                    // Mostrar mensaje al usuario
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-warning alert-dismissible fade show position-fixed';
                    alertDiv.style.cssText = `
                        top: 20px;
                        right: 20px;
                        z-index: 9999;
                        min-width: 350px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    `;
                    alertDiv.innerHTML = `
                        <strong>🔧 Problema detectado:</strong> Hay una inconsistencia en tu carrito.
                        <div class="mt-2">
                            <button onclick="CartDiagnostics.syncCart()" class="btn btn-sm btn-outline-primary me-2">🔄 Sincronizar</button>
                            <button onclick="CartDiagnostics.clearCache()" class="btn btn-sm btn-outline-secondary">🧹 Limpiar Caché</button>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    
                    document.body.appendChild(alertDiv);
                    
                    // Auto-remover después de 15 segundos
                    setTimeout(() => {
                        if (alertDiv.parentNode) {
                            alertDiv.remove();
                        }
                    }, 15000);
                }
            }, 2000); // Esperar 2 segundos
            */
        }
    }
    
    // Agregar comandos globales para debugging
    window.cartDebug = {
        sync: () => CartDiagnostics.syncCart(),
        check: () => CartDiagnostics.checkCartStatus(),
        clear: () => CartDiagnostics.clearCache(),
        full: () => CartDiagnostics.fullDiagnosis(),
        fix: () => CartUtils.autoFix(),
        reload: () => {
            // Solo log - no recargar automáticamente
            console.log('ℹ️ Función de recarga deshabilitada para evitar interrupciones');
            console.log('💡 Recarga manual con F5 si es necesario');
        }
    };
    
    console.log('🛠️ Comandos de carrito disponibles:');
    console.log('  cartDebug.sync()   - Sincronizar con servidor');
    console.log('  cartDebug.check()  - Verificar estado');
    console.log('  cartDebug.clear()  - Limpiar caché');
    console.log('  cartDebug.full()   - Diagnóstico completo');
    console.log('  cartDebug.fix()    - Corrección automática');
    console.log('  cartDebug.reload() - Recargar página');
});
