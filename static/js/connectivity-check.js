/**
 * Sistema de verificación de conectividad del servidor
 */

// Función para verificar si el servidor está disponible
async function checkServerConnectivity() {
    try {
        const response = await fetch('/cart/', {
            method: 'HEAD',
            headers: {
                'Cache-Control': 'no-cache'
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Error de conectividad:', error);
        return false;
    }
}

// Función para mostrar estado de conectividad
function showConnectivityStatus(isConnected) {
    const statusElement = document.getElementById('connectivity-status');
    if (!statusElement) {
        // Crear elemento de estado si no existe
        const status = document.createElement('div');
        status.id = 'connectivity-status';
        status.className = 'connectivity-status';
        document.body.appendChild(status);
    }
    
    const status = document.getElementById('connectivity-status');
    if (isConnected) {
        status.className = 'connectivity-status connected';
        status.innerHTML = '<i class="fas fa-wifi"></i> Conectado';
        status.style.display = 'none'; // Solo mostrar cuando hay problemas
    } else {
        status.className = 'connectivity-status disconnected';
        status.innerHTML = '<i class="fas fa-wifi-slash"></i> Sin conexión al servidor';
        status.style.display = 'block';
    }
}

// Verificar conectividad periódicamente
setInterval(async () => {
    const isConnected = await checkServerConnectivity();
    showConnectivityStatus(isConnected);
}, 30000); // Verificar cada 30 segundos

// Verificar conectividad al cargar la página
document.addEventListener('DOMContentLoaded', async () => {
    const isConnected = await checkServerConnectivity();
    showConnectivityStatus(isConnected);
});

// Función para usar en las peticiones AJAX
async function safeAjaxRequest(url, options) {
    const isConnected = await checkServerConnectivity();
    if (!isConnected) {
        throw new Error('No hay conexión con el servidor. Verifica que Django esté ejecutándose en http://127.0.0.1:8000');
    }
    return fetch(url, options);
}
