// JavaScript para gestión de stock en el admin
function updateStock(productId, change) {
    if (confirm(`¿Estás seguro de que quieres ${change > 0 ? 'aumentar' : 'reducir'} el stock en ${Math.abs(change)} unidades?`)) {
        // Aquí iría la llamada AJAX para actualizar el stock
        // Por ahora, mostramos un mensaje
        alert(`Stock ${change > 0 ? 'aumentado' : 'reducido'} en ${Math.abs(change)} unidades para el producto ${productId}`);
        
        // Recargar la página para ver los cambios
        window.location.reload();
    }
}

// Funciones para destacar productos con stock crítico
document.addEventListener('DOMContentLoaded', function() {
    // Resaltar filas con stock crítico
    const rows = document.querySelectorAll('tr');
    rows.forEach(function(row) {
        const stockCell = row.querySelector('td'); // Buscar la celda de stock
        if (stockCell && stockCell.textContent.includes('CRÍTICO')) {
            row.style.backgroundColor = '#ffebee';
        } else if (stockCell && stockCell.textContent.includes('AGOTADO')) {
            row.style.backgroundColor = '#ffcdd2';
        } else if (stockCell && stockCell.textContent.includes('BAJO')) {
            row.style.backgroundColor = '#fff3e0';
        }
    });
    
    // Agregar notificación de stock bajo
    const criticalItems = document.querySelectorAll('span:contains("CRÍTICO"), span:contains("AGOTADO")').length;
    if (criticalItems > 0) {
        const notification = document.createElement('div');
        notification.innerHTML = `
            <div style="background: #f44336; color: white; padding: 10px; margin: 10px 0; border-radius: 5px;">
                ⚠️ Atención: Hay ${criticalItems} productos con stock crítico o agotado que requieren reabastecimiento.
            </div>
        `;
        const content = document.querySelector('.content');
        if (content) {
            content.insertBefore(notification, content.firstChild);
        }
    }
});

// Función para exportar datos de stock
function exportStockData() {
    // Recopilar datos de la tabla
    const rows = document.querySelectorAll('table tbody tr');
    let csvContent = 'Producto,Stock,Estado,Última Actualización\n';
    
    rows.forEach(function(row) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            const product = cells[1].textContent.trim();
            const stock = cells[3].textContent.trim();
            const status = cells[4].textContent.trim();
            const updated = cells[5].textContent.trim();
            csvContent += `"${product}","${stock}","${status}","${updated}"\n`;
        }
    });
    
    // Crear y descargar archivo
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'stock_report_' + new Date().toISOString().split('T')[0] + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Función para buscar productos por stock
function filterByStock(level) {
    const searchBox = document.querySelector('#searchbar');
    if (searchBox) {
        switch(level) {
            case 'critical':
                searchBox.value = 'CRÍTICO';
                break;
            case 'low':
                searchBox.value = 'BAJO';
                break;
            case 'out':
                searchBox.value = 'AGOTADO';
                break;
            default:
                searchBox.value = '';
        }
        
        // Trigger search
        const event = new Event('input', { bubbles: true });
        searchBox.dispatchEvent(event);
    }
}
