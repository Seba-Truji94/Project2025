// Script de reparación del botón del carrito
// Este script asegura que el botón del carrito funcione correctamente
(function() {
    'use strict';
    
    // Función para verificar y reparar el botón del carrito
    function repairCartButton() {
        console.log('🔧 Reparando botón del carrito...');
        
        const cartBtn = document.querySelector('.cart-btn');
        if (!cartBtn) {
            console.error('❌ Botón del carrito no encontrado');
            return;
        }
        
        // Verificar si ya tiene event listeners
        const hasListeners = cartBtn.onclick !== null;
        console.log(`📡 Event listeners presentes: ${hasListeners}`);
        
        // Remover listeners existentes si los hay
        const newCartBtn = cartBtn.cloneNode(true);
        cartBtn.parentNode.replaceChild(newCartBtn, cartBtn);
        
        // Agregar el event listener correcto
        newCartBtn.addEventListener('click', function(e) {
            console.log('🖱️ Click en botón del carrito detectado');
            
            // Obtener contador actual
            const cartCount = document.querySelector('.cart-count');
            const itemCount = cartCount ? parseInt(cartCount.textContent) || 0 : 0;
            
            console.log(`📊 Items en carrito: ${itemCount}`);
            
            // Verificar si existe el modal
            const cartModal = document.getElementById('cart-modal');
            
            if (cartModal && itemCount > 0) {
                // Si hay items y el modal existe, usar el modal
                e.preventDefault();
                console.log('📱 Abriendo modal del carrito...');
                
                cartModal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                
                // Actualizar contenido del modal si es necesario
                updateCartModal();
                
            } else {
                // Si no hay items o no hay modal, ir a la página del carrito
                console.log('🔗 Redirigiendo a página del carrito...');
                // El enlace funcionará normalmente
            }
        });
        
        console.log('✅ Botón del carrito reparado');
    }
    
    // Función para actualizar el modal del carrito
    function updateCartModal() {
        // Hacer una petición AJAX para obtener el contenido actual del carrito
        fetch('/cart/summary/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderCartModalContent(data);
            } else {
                console.warn('⚠️ Error al cargar contenido del carrito');
            }
        })
        .catch(error => {
            console.error('❌ Error en petición AJAX:', error);
        });
    }
    
    // Función para renderizar el contenido del modal
    function renderCartModalContent(cartData) {
        const cartItems = document.getElementById('cart-items');
        const cartEmpty = document.getElementById('cart-empty');
        const cartFooter = document.getElementById('cart-footer');
        
        if (!cartItems) return;
        
        if (cartData.total_items === 0) {
            cartItems.style.display = 'none';
            cartEmpty.style.display = 'block';
            cartFooter.style.display = 'none';
            return;
        }
        
        cartItems.style.display = 'block';
        cartEmpty.style.display = 'none';
        cartFooter.style.display = 'block';
        
        // Limpiar contenido existente
        cartItems.innerHTML = '';
        
        // Renderizar items
        cartData.items.forEach(item => {
            const cartItemElement = document.createElement('div');
            cartItemElement.className = 'cart-item-modal';
            cartItemElement.innerHTML = `
                <div class="cart-item-info">
                    ${item.image ? `<img src="${item.image}" alt="${item.name}" class="cart-item-image">` : ''}
                    <div class="cart-item-details">
                        <h5>${item.name}</h5>
                        <p>Cantidad: ${item.quantity}</p>
                        <p>Precio: ${item.price}</p>
                        <p><strong>Total: ${item.total}</strong></p>
                    </div>
                </div>
            `;
            cartItems.appendChild(cartItemElement);
        });
        
        // Actualizar totales
        const cartSubtotal = document.getElementById('cart-subtotal');
        const shippingCost = document.getElementById('shipping-cost');
        const cartTotalFinal = document.getElementById('cart-total-final');
        
        if (cartSubtotal) cartSubtotal.textContent = cartData.total_price;
        if (shippingCost) shippingCost.textContent = cartData.shipping_cost;
        if (cartTotalFinal) cartTotalFinal.textContent = cartData.final_total;
        
        console.log('✅ Contenido del modal actualizado');
    }
    
    // Función para cerrar el modal
    function setupModalCloseEvents() {
        const cartModal = document.getElementById('cart-modal');
        const closeBtn = document.querySelector('#cart-modal .close-btn');
        const continueShoppingBtn = document.querySelector('.continue-shopping');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                if (cartModal) {
                    cartModal.style.display = 'none';
                    document.body.style.overflow = '';
                }
            });
        }
        
        if (continueShoppingBtn) {
            continueShoppingBtn.addEventListener('click', () => {
                if (cartModal) {
                    cartModal.style.display = 'none';
                    document.body.style.overflow = '';
                }
            });
        }
        
        // Cerrar modal al hacer clic fuera
        if (cartModal) {
            cartModal.addEventListener('click', (e) => {
                if (e.target === cartModal) {
                    cartModal.style.display = 'none';
                    document.body.style.overflow = '';
                }
            });
        }
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            repairCartButton();
            setupModalCloseEvents();
        });
    } else {
        repairCartButton();
        setupModalCloseEvents();
    }
    
    // También ejecutar después de un pequeño retraso para asegurar compatibilidad
    setTimeout(function() {
        repairCartButton();
        setupModalCloseEvents();
    }, 1000);
    
    console.log('🚀 Script de reparación del carrito cargado');
})();
