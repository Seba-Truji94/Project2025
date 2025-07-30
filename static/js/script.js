// Enhanced Product Data with Chilean Values
const products = [
    {
        id: 1,
        name: "Galletas de Chocolate Premium",
        description: "Galletas artesanales con chocolate belga y mantequilla europea. Perfectas para el once o cualquier momento especial.",
        price: 3200.00,
        originalPrice: 4000.00,
        emoji: "🍪",
        category: "premium",
        tags: ["bestseller", "premium"],
        rating: 4.8,
        reviews: 147,
        inStock: true,
        stockCount: 25,
        features: ["Chocolate Belga", "Sin Conservadores", "Artesanal"]
    },
    {
        id: 2,
        name: "Galletas de Avena Integral",
        description: "Nutritivas galletas con avena chilena, pasas y miel natural. Perfectas para un desayuno saludable o el once.",
        price: 2800.00,
        originalPrice: 3500.00,
        emoji: "🥜",
        category: "healthy",
        tags: ["healthy", "organic"],
        rating: 4.7,
        reviews: 89,
        inStock: true,
        stockCount: 18,
        features: ["Avena Chilena", "Alta Fibra", "Miel Natural"]
    },
    {
        id: 3,
        name: "Galletas de Mantequilla Clásicas",
        description: "Tradicionales galletas de mantequilla, suaves y aromáticas. La receta de la abuela que conquistó Valparaíso.",
        price: 2500.00,
        originalPrice: 3200.00,
        emoji: "🧈",
        category: "classic",
        tags: ["classic"],
        rating: 4.6,
        reviews: 76,
        inStock: true,
        stockCount: 22,
        features: ["Receta Tradicional", "Mantequilla Natural", "Sin Aditivos"]
    },
    {
        id: 4,
        name: "Galletas de Jengibre Especiadas",
        description: "Aromáticas galletas con jengibre fresco y especias importadas. Perfectas para acompañar tu té o café.",
        price: 2900.00,
        originalPrice: 3600.00,
        emoji: "🫚",
        category: "premium",
        tags: ["bestseller", "spiced"],
        rating: 4.8,
        reviews: 103,
        inStock: true,
        stockCount: 15,
        features: ["Jengibre Fresco", "Especias Premium", "Energizante"]
    },
    {
        id: 5,
        name: "Galletas de Coco Tropical",
        description: "Exóticas galletas con coco rallado natural y un toque de limón chileno. Un sabor tropical irresistible.",
        price: 3000.00,
        originalPrice: 3800.00,
        emoji: "🥥",
        category: "premium",
        tags: ["tropical", "premium"],
        rating: 4.5,
        reviews: 64,
        inStock: true,
        stockCount: 12,
        features: ["Coco Natural", "Limón Chileno", "Toque Cítrico"]
    },
    {
        id: 6,
        name: "Galletas de Doble Chocolate",
        description: "Para los verdaderos amantes del chocolate: masa de cacao, chispas de chocolate negro y cobertura especial.",
        price: 3500.00,
        originalPrice: 4500.00,
        emoji: "🍫",
        category: "premium",
        tags: ["bestseller", "premium", "chocolate"],
        rating: 4.9,
        reviews: 182,
        inStock: true,
        stockCount: 8,
        features: ["Triple Chocolate", "Cacao Premium", "Edición Especial"]
    },
    {
        id: 7,
        name: "Galletas Integrales de Almendra",
        description: "Galletas saludables con harina integral chilena y almendras naturales. Endulzadas con stevia.",
        price: 3200.00,
        originalPrice: 4000.00,
        emoji: "🌰",
        category: "healthy",
        tags: ["healthy", "fitness", "sugar-free"],
        rating: 4.4,
        reviews: 58,
        inStock: true,
        stockCount: 20,
        features: ["Sin Azúcar", "Harina Integral", "Almendras Naturales"]
    },
    {
        id: 8,
        name: "Galletas de Vainilla Gourmet",
        description: "Elegantes galletas con extracto de vainilla natural y mantequilla clarificada. Un toque de sofisticación.",
        price: 3300.00,
        originalPrice: 4200.00,
        emoji: "🌟",
        category: "premium",
        tags: ["premium", "gourmet"],
        rating: 4.7,
        reviews: 67,
        inStock: true,
        stockCount: 16,
        features: ["Vainilla Natural", "Gourmet", "Mantequilla Premium"]
    }
];

// Enhanced Application State
class CookieShopApp {
    constructor() {
        this.cart = this.loadCart();
        this.wishlist = this.loadWishlist();
        this.currentFilter = 'all';
        this.isNewsletterShown = false;
        this.init();
    }

    init() {
        this.renderProducts();
        this.updateCartUI();
        this.updateWishlistUI();
        this.setupEventListeners();
        this.setupIntersectionObserver();
        this.scheduleNewsletterPopup();
        this.handleAnnouncementBar();
    }

    // Product Management
    renderProducts() {
        const productGrid = document.getElementById('product-grid');
        if (!productGrid) return;

        const filteredProducts = this.filterProducts(products, this.currentFilter);
        
        productGrid.innerHTML = '';
        
        filteredProducts.forEach((product, index) => {
            const productCard = this.createProductCard(product, index);
            productGrid.appendChild(productCard);
        });

        // Apply intersection observer to new cards
        this.observeProductCards();
    }

    createProductCard(product, index) {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        const discountPercentage = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100);
        const isInWishlist = this.wishlist.some(item => item.id === product.id);
        
        card.innerHTML = `
            ${product.tags.includes('bestseller') ? '<div class="product-badge bestseller">🔥 Más Vendida</div>' : ''}
            ${product.tags.includes('premium') ? '<div class="product-badge premium">⭐ Premium</div>' : ''}
            
            <button class="product-wishlist ${isInWishlist ? 'active' : ''}" onclick="app.toggleWishlist(${product.id})">
                <i class="fa${isInWishlist ? 's' : 'r'} fa-heart"></i>
            </button>
            
            <div class="product-image">
                ${product.emoji}
            </div>
            
            <div class="product-info">
                <div class="product-rating">
                    <span class="rating-stars">${'⭐'.repeat(Math.floor(product.rating))}</span>
                    <span class="rating-count">(${product.reviews})</span>
                </div>
                
                <h3>${product.name}</h3>
                <p>${product.description}</p>
                
                <div class="product-features">
                    ${product.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('')}
                </div>
                
                <div class="product-pricing">
                    <div class="product-price">
                        <span class="price-current">$${product.price.toLocaleString('es-CL')}</span>
                        ${product.originalPrice > product.price ? `
                            <span class="price-original">$${product.originalPrice.toLocaleString('es-CL')}</span>
                            <span class="price-discount">-${discountPercentage}%</span>
                        ` : ''}
                    </div>
                </div>
                
                <div class="product-actions">
                    <button class="add-to-cart" onclick="app.addToCart(${product.id})" ${!product.inStock ? 'disabled' : ''}>
                        <i class="fas fa-shopping-cart"></i>
                        ${product.inStock ? 'Agregar al Carrito' : 'Agotado'}
                    </button>
                    <button class="quick-view" onclick="app.showQuickView(${product.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
                
                ${product.stockCount < 10 ? `<div class="stock-warning">¡Solo quedan ${product.stockCount}!</div>` : ''}
            </div>
        `;
        
        return card;
    }

    filterProducts(products, filter) {
        switch (filter) {
            case 'bestseller':
                return products.filter(p => p.tags.includes('bestseller'));
            case 'premium':
                return products.filter(p => p.tags.includes('premium'));
            case 'healthy':
                return products.filter(p => p.tags.includes('healthy'));
            default:
                return products;
        }
    }

    // Cart Management
    addToCart(productId) {
        const product = products.find(p => p.id === productId);
        if (!product || !product.inStock) return;

        const existingItem = this.cart.find(item => item.id === productId);
        
        if (existingItem) {
            if (existingItem.quantity < product.stockCount) {
                existingItem.quantity += 1;
                this.showNotification(`${product.name} agregado al carrito`, 'success');
            } else {
                this.showNotification('No hay más stock disponible', 'warning');
                return;
            }
        } else {
            this.cart.push({
                ...product,
                quantity: 1
            });
            this.showNotification(`${product.name} agregado al carrito`, 'success');
        }
        
        this.updateCartUI();
        this.saveCart();
        this.animateCartButton();
    }

    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.updateCartUI();
        this.renderCartItems();
        this.saveCart();
    }

    updateQuantity(productId, change) {
        const item = this.cart.find(item => item.id === productId);
        const product = products.find(p => p.id === productId);
        
        if (item && product) {
            const newQuantity = item.quantity + change;
            
            if (newQuantity <= 0) {
                this.removeFromCart(productId);
            } else if (newQuantity <= product.stockCount) {
                item.quantity = newQuantity;
                this.updateCartUI();
                this.renderCartItems();
                this.saveCart();
            } else {
                this.showNotification('No hay más stock disponible', 'warning');
            }
        }
    }

    updateCartUI() {
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        const cartCount = document.getElementById('cart-count');
        const cartTotalPreview = document.getElementById('cart-total-preview');
        const cartSubtotal = document.getElementById('cart-subtotal');
        const cartTotalFinal = document.getElementById('cart-total-final');
        const shippingCost = document.getElementById('shipping-cost');
        
        if (cartCount) cartCount.textContent = totalItems;
        if (cartTotalPreview) cartTotalPreview.textContent = `$${totalPrice.toLocaleString('es-CL')}`;
        if (cartSubtotal) cartSubtotal.textContent = `$${totalPrice.toLocaleString('es-CL')}`;
        
        // Calculate shipping (free over $15,000 CLP)
        const shipping = totalPrice >= 15000 ? 0 : 3000;
        const finalTotal = totalPrice + shipping;
        
        if (shippingCost) {
            shippingCost.textContent = shipping === 0 ? 'GRATIS' : `$${shipping.toLocaleString('es-CL')}`;
            shippingCost.style.color = shipping === 0 ? 'var(--success)' : 'var(--black)';
        }
        
        if (cartTotalFinal) cartTotalFinal.textContent = `$${finalTotal.toLocaleString('es-CL')}`;
    }

    renderCartItems() {
        const cartItems = document.getElementById('cart-items');
        const cartEmpty = document.getElementById('cart-empty');
        const cartFooter = document.getElementById('cart-footer');
        
        if (!cartItems) return;
        
        if (this.cart.length === 0) {
            cartItems.style.display = 'none';
            cartEmpty.style.display = 'block';
            cartFooter.style.display = 'none';
            return;
        }
        
        cartItems.style.display = 'block';
        cartEmpty.style.display = 'none';
        cartFooter.style.display = 'block';
        
        cartItems.innerHTML = '';
        
        this.cart.forEach(item => {
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <div class="cart-item-image">${item.emoji}</div>
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">$${item.price.toLocaleString('es-CL')} c/u</div>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn" onclick="app.updateQuantity(${item.id}, -1)">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="quantity-display">${item.quantity}</span>
                        <button class="quantity-btn" onclick="app.updateQuantity(${item.id}, 1)">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <button class="remove-btn" onclick="app.removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            cartItems.appendChild(cartItem);
        });
    }

    // Wishlist Management
    toggleWishlist(productId) {
        const product = products.find(p => p.id === productId);
        if (!product) return;

        const existingIndex = this.wishlist.findIndex(item => item.id === productId);
        
        if (existingIndex > -1) {
            this.wishlist.splice(existingIndex, 1);
            this.showNotification(`${product.name} removido de favoritos`, 'info');
        } else {
            this.wishlist.push(product);
            this.showNotification(`${product.name} agregado a favoritos`, 'success');
        }
        
        this.updateWishlistUI();
        this.saveWishlist();
        this.renderProducts(); // Re-render to update heart icons
    }

    updateWishlistUI() {
        const wishlistCount = document.querySelector('.wishlist-count');
        if (wishlistCount) {
            wishlistCount.textContent = this.wishlist.length;
            wishlistCount.style.display = this.wishlist.length > 0 ? 'flex' : 'none';
        }
    }

    // Enhanced Notifications
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="${icons[type]}"></i>
            <span>${message}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: type === 'success' ? 'var(--success)' : 
                       type === 'error' ? 'var(--error)' : 
                       type === 'warning' ? 'var(--warning)' : 'var(--primary-color)',
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: 'var(--border-radius)',
            boxShadow: 'var(--shadow-lg)',
            zIndex: '3000',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            maxWidth: '350px',
            animation: 'slideInRight 0.3s ease',
            fontSize: '0.9rem',
            fontWeight: '500'
        });
        
        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                notification.remove();
                style.remove();
            }, 300);
        });
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    notification.remove();
                    style.remove();
                }, 300);
            }
        }, 4000);
    }

    // Local Storage Management
    saveCart() {
        localStorage.setItem('galletas-kati-cart', JSON.stringify(this.cart));
    }

    loadCart() {
        try {
            const saved = localStorage.getItem('galletas-kati-cart');
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            return [];
        }
    }

    saveWishlist() {
        localStorage.setItem('galletas-kati-wishlist', JSON.stringify(this.wishlist));
    }

    loadWishlist() {
        try {
            const saved = localStorage.getItem('galletas-kati-wishlist');
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            return [];
        }
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Cart modal events
        const cartBtn = document.querySelector('.cart-btn');
        const cartModal = document.getElementById('cart-modal');
        const closeBtn = document.querySelector('.close-btn');
        const continueShoppingBtn = document.querySelector('.continue-shopping');
        const checkoutBtn = document.querySelector('.checkout-btn');
        
        if (cartBtn) {
            cartBtn.addEventListener('click', (e) => {
                e.preventDefault();
                cartModal.style.display = 'block';
                this.renderCartItems();
                document.body.style.overflow = 'hidden';
            });
        }
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                cartModal.style.display = 'none';
                document.body.style.overflow = 'auto';
            });
        }
        
        if (continueShoppingBtn) {
            continueShoppingBtn.addEventListener('click', () => {
                cartModal.style.display = 'none';
                document.body.style.overflow = 'auto';
                document.getElementById('productos').scrollIntoView({ behavior: 'smooth' });
            });
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === cartModal) {
                cartModal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
        
        // Product filter buttons
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.dataset.filter;
                this.renderProducts();
            });
        });
        
        // CTA buttons
        const ctaPrimary = document.querySelector('.cta-primary');
        const ctaSecondary = document.querySelector('.cta-secondary');
        
        if (ctaPrimary) {
            ctaPrimary.addEventListener('click', () => {
                document.getElementById('productos').scrollIntoView({ behavior: 'smooth' });
            });
        }
        
        if (ctaSecondary) {
            ctaSecondary.addEventListener('click', () => {
                this.showNotification('¡Próximamente disponible! Video del proceso artesanal', 'info');
            });
        }
        
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
        
        // Checkout functionality
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                this.processCheckout();
            });
        }
        
        // Newsletter form
        const newsletterForm = document.querySelector('.newsletter-form');
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const email = e.target.querySelector('input[type="email"]').value;
                this.subscribeNewsletter(email);
            });
        }
        
        // Contact form
        const contactForm = document.querySelector('.quick-contact');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitContactForm(e.target);
            });
        }
        
        // Announcement bar close
        const announcementClose = document.querySelector('.announcement-close');
        if (announcementClose) {
            announcementClose.addEventListener('click', () => {
                document.querySelector('.announcement-bar').style.display = 'none';
                localStorage.setItem('announcement-closed', 'true');
            });
        }
        
        // Search functionality (placeholder)
        const searchBtn = document.querySelector('.search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.showNotification('Función de búsqueda próximamente disponible', 'info');
            });
        }
        
        // Navbar scroll effect
        this.setupNavbarScroll();
    }

    // Advanced Features
    processCheckout() {
        if (this.cart.length === 0) {
            this.showNotification('Tu carrito está vacío', 'warning');
            return;
        }
        
        const total = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const itemCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        const shipping = total >= 15000 ? 0 : 3000;
        const finalTotal = total + shipping;
        
        // Simulate payment process
        const modal = document.getElementById('cart-modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        this.showNotification('Procesando pago...', 'info');
        
        setTimeout(() => {
            this.showNotification(
                `¡Compra exitosa! Total: $${finalTotal.toLocaleString('es-CL')} | Productos: ${itemCount} | Recibirás confirmación por email`,
                'success'
            );
            
            // Clear cart after successful purchase
            this.cart = [];
            this.updateCartUI();
            this.saveCart();
            
            // Show order confirmation
            setTimeout(() => {
                this.showOrderConfirmation(finalTotal, itemCount);
            }, 2000);
        }, 1500);
    }
    
    showOrderConfirmation(total, itemCount) {
        const confirmation = document.createElement('div');
        confirmation.className = 'order-confirmation';
        confirmation.innerHTML = `
            <div class="confirmation-content">
                <div class="confirmation-header">
                    <i class="fas fa-check-circle"></i>
                    <h2>¡Pedido Confirmado!</h2>
                </div>
                <div class="confirmation-details">
                    <p><strong>Número de orden:</strong> #GK${Date.now()}</p>
                    <p><strong>Total pagado:</strong> $${total.toLocaleString('es-CL')}</p>
                    <p><strong>Productos:</strong> ${itemCount}</p>
                    <p><strong>Entrega estimada:</strong> 2-3 días hábiles</p>
                </div>
                <div class="confirmation-actions">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()">Cerrar</button>
                </div>
            </div>
        `;
        
        Object.assign(confirmation.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: '4000'
        });
        
        const style = document.createElement('style');
        style.textContent = `
            .confirmation-content {
                background: white;
                padding: 3rem;
                border-radius: var(--border-radius-large);
                text-align: center;
                max-width: 500px;
                margin: 2rem;
            }
            .confirmation-header i {
                font-size: 4rem;
                color: var(--success);
                margin-bottom: 1rem;
            }
            .confirmation-header h2 {
                color: var(--black);
                margin-bottom: 2rem;
            }
            .confirmation-details {
                text-align: left;
                margin-bottom: 2rem;
            }
            .confirmation-details p {
                margin-bottom: 0.5rem;
                color: var(--gray-medium);
            }
            .confirmation-actions button {
                background: var(--primary-color);
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: var(--border-radius);
                cursor: pointer;
                font-weight: 600;
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(confirmation);
        
        setTimeout(() => {
            confirmation.remove();
            style.remove();
        }, 10000);
    }

    subscribeNewsletter(email) {
        // Simulate newsletter subscription
        this.showNotification('¡Gracias por suscribirte! Revisa tu email para el descuento del 15%', 'success');
        document.getElementById('newsletter-modal').style.display = 'none';
        localStorage.setItem('newsletter-subscribed', 'true');
    }

    submitContactForm(form) {
        const formData = new FormData(form);
        // Simulate form submission
        this.showNotification('Mensaje enviado correctamente. Te responderemos pronto.', 'success');
        form.reset();
    }

    scheduleNewsletterPopup() {
        const isSubscribed = localStorage.getItem('newsletter-subscribed');
        const lastShown = localStorage.getItem('newsletter-last-shown');
        const now = Date.now();
        
        if (!isSubscribed && (!lastShown || now - parseInt(lastShown) > 24 * 60 * 60 * 1000)) {
            setTimeout(() => {
                const modal = document.getElementById('newsletter-modal');
                if (modal && !this.isNewsletterShown) {
                    modal.style.display = 'block';
                    this.isNewsletterShown = true;
                    localStorage.setItem('newsletter-last-shown', now.toString());
                }
            }, 30000); // Show after 30 seconds
        }
        
        // Newsletter close button
        const newsletterClose = document.querySelector('.newsletter-close');
        if (newsletterClose) {
            newsletterClose.addEventListener('click', () => {
                document.getElementById('newsletter-modal').style.display = 'none';
            });
        }
    }

    handleAnnouncementBar() {
        const isClosed = localStorage.getItem('announcement-closed');
        if (isClosed) {
            const announcementBar = document.querySelector('.announcement-bar');
            if (announcementBar) {
                announcementBar.style.display = 'none';
            }
        }
    }

    setupNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        let lastScrollY = window.scrollY;
        
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            // Hide/show navbar on scroll
            if (currentScrollY > lastScrollY && currentScrollY > 200) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollY = currentScrollY;
        });
        
        navbar.style.transition = 'transform 0.3s ease';
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                }
            });
        }, observerOptions);
    }

    observeProductCards() {
        setTimeout(() => {
            document.querySelectorAll('.product-card').forEach(card => {
                this.observer.observe(card);
            });
        }, 100);
    }

    animateCartButton() {
        const cartBtn = document.querySelector('.cart-btn');
        if (cartBtn) {
            cartBtn.style.transform = 'scale(1.1)';
            cartBtn.style.transition = 'transform 0.2s ease';
            setTimeout(() => {
                cartBtn.style.transform = 'scale(1)';
            }, 200);
        }
    }

    showQuickView(productId) {
        const product = products.find(p => p.id === productId);
        if (!product) return;
        
        // Create quick view modal
        const quickViewModal = document.createElement('div');
        quickViewModal.className = 'modal quick-view-modal';
        quickViewModal.innerHTML = `
            <div class="modal-content quick-view-content">
                <button class="close-btn">
                    <i class="fas fa-times"></i>
                </button>
                <div class="quick-view-grid">
                    <div class="quick-view-image">
                        ${product.emoji}
                    </div>
                    <div class="quick-view-details">
                        <h2>${product.name}</h2>
                        <div class="product-rating">
                            <span class="rating-stars">${'⭐'.repeat(Math.floor(product.rating))}</span>
                            <span class="rating-count">(${product.reviews} reseñas)</span>
                        </div>
                        <p class="description">${product.description}</p>
                        <div class="features">
                            ${product.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('')}
                        </div>
                        <div class="pricing">
                            <span class="price-current">$${product.price.toLocaleString('es-CL')}</span>
                            ${product.originalPrice > product.price ? `<span class="price-original">$${product.originalPrice.toLocaleString('es-CL')}</span>` : ''}
                        </div>
                        <div class="quick-view-actions">
                            <button class="add-to-cart-quick" onclick="app.addToCart(${product.id}); this.closest('.modal').remove();">
                                <i class="fas fa-shopping-cart"></i>
                                Agregar al Carrito
                            </button>
                            <button class="wishlist-quick" onclick="app.toggleWishlist(${product.id});">
                                <i class="far fa-heart"></i>
                                Favoritos
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(quickViewModal);
        quickViewModal.style.display = 'block';
        
        // Close functionality
        const closeBtn = quickViewModal.querySelector('.close-btn');
        closeBtn.addEventListener('click', () => {
            quickViewModal.remove();
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === quickViewModal) {
                quickViewModal.remove();
            }
        });
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new CookieShopApp();
    
    // Add custom styles for new features
    const additionalStyles = document.createElement('style');
    additionalStyles.textContent = `
        .notification {
            font-family: var(--font-primary);
        }
        
        .product-wishlist.active {
            background: var(--error) !important;
            color: var(--white) !important;
        }
        
        .stock-warning {
            background: var(--warning);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            text-align: center;
            margin-top: 0.5rem;
        }
        
        .quick-view-modal .modal-content {
            max-width: 800px;
            padding: 0;
        }
        
        .quick-view-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
        }
        
        .quick-view-image {
            background: var(--background-light);
            border-radius: var(--border-radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8rem;
            min-height: 300px;
        }
        
        .quick-view-details h2 {
            margin-bottom: 1rem;
            color: var(--black);
        }
        
        .quick-view-details .description {
            margin: 1rem 0;
            color: var(--gray-medium);
            line-height: 1.6;
        }
        
        .quick-view-details .features {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .quick-view-details .pricing {
            margin: 1.5rem 0;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .quick-view-actions {
            display: flex;
            gap: 1rem;
        }
        
        .add-to-cart-quick,
        .wishlist-quick {
            padding: 1rem 1.5rem;
            border: none;
            border-radius: var(--border-radius);
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: var(--transition-medium);
        }
        
        .add-to-cart-quick {
            background: var(--primary-color);
            color: var(--white);
            flex: 1;
        }
        
        .wishlist-quick {
            background: var(--white);
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
        }
        
        .add-to-cart-quick:hover {
            background: var(--primary-dark);
        }
        
        .wishlist-quick:hover {
            background: var(--primary-color);
            color: var(--white);
        }
        
        @media (max-width: 768px) {
            .quick-view-grid {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .quick-view-image {
                min-height: 200px;
                font-size: 6rem;
            }
        }
    `;
    document.head.appendChild(additionalStyles);
});

// Global functions for inline onclick handlers (maintaining backward compatibility)
function addToCart(productId) {
    app.addToCart(productId);
}

function removeFromCart(productId) {
    app.removeFromCart(productId);
}

function updateQuantity(productId, change) {
    app.updateQuantity(productId, change);
}
