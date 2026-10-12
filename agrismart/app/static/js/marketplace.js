/* =========================================
   AGRISMART - MARKETPLACE & REALISTIC PAYMENT JS
   ========================================= */

class AgriCart {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('agrismart_cart') || '[]');
        this.cartDrawer = document.getElementById('cartDrawer');
        this.cartOverlay = document.getElementById('cartOverlay');
        this.cartCountBadge = document.getElementById('floatingCartCount');
        this.cartItemsList = document.getElementById('cartItemsList');
        this.cartTotalVal = document.getElementById('cartTotalVal');
        this.cartSubtotalVal = document.getElementById('cartSubtotalVal');
        this.cartDeliveryVal = document.getElementById('cartDeliveryVal');
        this.freeDeliveryText = document.getElementById('freeDeliveryText');
        this.freeDeliveryBadge = document.getElementById('freeDeliveryBadge');
        this.freeDeliveryProgress = document.getElementById('freeDeliveryProgress');
        this.floatingCartBtn = document.getElementById('floatingCartBtn');
        this.activePaymentTab = 'upi';

        this.init();
    }

    init() {
        this.updateBadge();
        this.renderDrawer();

        // Cart Drawer Toggles
        if (this.floatingCartBtn) {
            this.floatingCartBtn.addEventListener('click', () => this.openDrawer());
        }

        const closeBtn = document.getElementById('closeCartDrawer');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeDrawer());
        }

        if (this.cartOverlay) {
            this.cartOverlay.addEventListener('click', () => this.closeDrawer());
        }

        // Add to Cart Buttons on Cards
        document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const card = btn.closest('.product-card');
                const product = {
                    id: parseInt(card.dataset.id),
                    name: card.dataset.name,
                    price: parseFloat(card.dataset.price),
                    image: card.dataset.image,
                    stock: parseInt(card.dataset.stock) || 50
                };

                this.flyToCart(btn);
                this.addItem(product);
            });
        });

        // Checkout Button in Drawer
        const checkoutBtn = document.getElementById('checkoutBtn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                window.location.href = '/cart';
            });
        }

        this.initPaymentTabs();
    }

    initPaymentTabs() {
        const tabBtns = document.querySelectorAll('.pay-tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                this.activePaymentTab = tab;

                // Update buttons
                tabBtns.forEach(b => {
                    b.classList.remove('active');
                    b.style.background = 'transparent';
                    b.style.color = 'var(--text-secondary)';
                });
                btn.classList.add('active');
                btn.style.background = 'var(--bg-secondary)';
                btn.style.color = 'var(--color-emerald)';

                // Update tab contents
                document.querySelectorAll('.pay-tab-content').forEach(c => c.style.display = 'none');
                const activeContent = document.getElementById(`tabContent-${tab}`);
                if (activeContent) activeContent.style.display = 'block';

                this.updatePayButtonLabel();
            });
        });

        // Card number auto-spacing format
        const cardInput = document.getElementById('cardNumberInput');
        if (cardInput) {
            cardInput.addEventListener('input', (e) => {
                let val = e.target.value.replace(/\D/g, '').substring(0, 16);
                let formatted = val.match(/.{1,4}/g)?.join(' ') || val;
                e.target.value = formatted;
            });
        }
    }

    save() {
        localStorage.setItem('agrismart_cart', JSON.stringify(this.cart));
        this.updateBadge();
        this.renderDrawer();
    }

    addItem(product) {
        const existing = this.cart.find(item => item.id === product.id);
        if (existing) {
            existing.qty += 1;
        } else {
            this.cart.push({
                id: product.id,
                name: product.name,
                price: product.price,
                image: product.image,
                qty: 1
            });
        }
        this.save();
        window.AgriApp?.showToast(`Added "${product.name}" to cart!`, 'success');
    }

    updateQty(productId, delta) {
        const item = this.cart.find(i => i.id === productId);
        if (!item) return;

        item.qty += delta;
        if (item.qty <= 0) {
            this.cart = this.cart.filter(i => i.id !== productId);
        }
        this.save();
    }

    removeItem(productId) {
        this.cart = this.cart.filter(i => i.id !== productId);
        this.save();
    }

    clear() {
        this.cart = [];
        this.save();
    }

    getSubtotal() {
        return this.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
    }

    getDeliveryFee() {
        const sub = this.getSubtotal();
        if (sub === 0) return 0;
        return sub >= 500.0 ? 0.0 : 50.0;
    }

    getTotal() {
        const sub = this.getSubtotal();
        if (sub === 0) return 0;
        return sub + this.getDeliveryFee();
    }

    updateBadge() {
        const count = this.cart.reduce((sum, item) => sum + item.qty, 0);
        if (this.cartCountBadge) {
            this.cartCountBadge.textContent = count;
            this.cartCountBadge.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    openDrawer() {
        this.renderDrawer();
        if (this.cartDrawer) this.cartDrawer.classList.add('open');
        if (this.cartOverlay) this.cartOverlay.classList.add('open');
    }

    closeDrawer() {
        if (this.cartDrawer) this.cartDrawer.classList.remove('open');
        if (this.cartOverlay) this.cartOverlay.classList.remove('open');
    }

    renderDrawer() {
        if (!this.cartItemsList) return;

        const subtotal = this.getSubtotal();
        const deliveryFee = this.getDeliveryFee();
        const grandTotal = this.getTotal();

        // Update Free Delivery Progress Tracker (>= ₹500 is Free Delivery)
        if (this.freeDeliveryProgress && this.freeDeliveryText && this.freeDeliveryBadge) {
            if (subtotal >= 500.0) {
                this.freeDeliveryProgress.style.width = '100%';
                this.freeDeliveryProgress.style.background = '#10b981';
                this.freeDeliveryText.innerHTML = '🎉 <strong style="color:#10b981;">FREE Delivery Unlocked!</strong>';
                this.freeDeliveryBadge.className = 'badge badge-emerald';
                this.freeDeliveryBadge.textContent = 'FREE Delivery';
            } else if (subtotal > 0) {
                const pct = Math.min((subtotal / 500.0) * 100, 100);
                const needed = (500.0 - subtotal).toFixed(2);
                this.freeDeliveryProgress.style.width = `${pct}%`;
                this.freeDeliveryProgress.style.background = 'linear-gradient(90deg, #f59e0b, #10b981)';
                this.freeDeliveryText.innerHTML = `Add <strong>₹${needed}</strong> more for <span style="color:#10b981;font-weight:700;">FREE Delivery</span>`;
                this.freeDeliveryBadge.className = 'badge badge-amber';
                this.freeDeliveryBadge.textContent = '₹50 Fee';
            } else {
                this.freeDeliveryProgress.style.width = '0%';
                this.freeDeliveryText.textContent = 'Free Delivery on orders ₹500 and above';
                this.freeDeliveryBadge.className = 'badge badge-gray';
                this.freeDeliveryBadge.textContent = '₹50 Fee';
            }
        }

        if (this.cart.length === 0) {
            this.cartItemsList.innerHTML = `
                <div class="empty-state" style="padding: 3rem 1rem;">
                    <div class="empty-state-icon" style="width:50px;height:50px;">
                        <i data-lucide="shopping-cart" style="width:24px;height:24px;"></i>
                    </div>
                    <h4 style="font-size:1.1rem;">Your Cart is Empty</h4>
                    <p style="font-size:0.85rem;color:var(--text-tertiary);margin-top:0.25rem;">Browse our certified seeds and fertilizers.</p>
                </div>
            `;
            if (this.cartSubtotalVal) this.cartSubtotalVal.textContent = '₹0.00';
            if (this.cartDeliveryVal) this.cartDeliveryVal.textContent = '₹0.00';
            if (this.cartTotalVal) this.cartTotalVal.textContent = '₹0.00';
            if (window.lucide) lucide.createIcons();
            return;
        }

        let html = '';
        this.cart.forEach(item => {
            const itemSub = (item.price * item.qty).toFixed(2);
            html += `
                <div class="cart-item-row" data-id="${item.id}">
                    <img src="${item.image}" alt="${item.name}" class="cart-item-img" onerror="this.onerror=null; this.src='/static/images/products/fallback_product.jpg';">
                    <div class="cart-item-info">
                        <div class="cart-item-title">${item.name}</div>
                        <div class="cart-item-price">₹${item.price.toFixed(2)}</div>
                    </div>
                    <div class="qty-stepper">
                        <button type="button" class="qty-btn" onclick="window.agriCart.updateQty(${item.id}, -1)">-</button>
                        <span style="font-size:0.85rem;font-weight:700;padding:0 4px;">${item.qty}</span>
                        <button type="button" class="qty-btn" onclick="window.agriCart.updateQty(${item.id}, 1)">+</button>
                    </div>
                    <button type="button" class="btn-icon" style="color:var(--color-error);width:28px;height:28px;" onclick="window.agriCart.removeItem(${item.id})">
                        <i data-lucide="trash-2" style="width:16px;height:16px;"></i>
                    </button>
                </div>
            `;
        });

        this.cartItemsList.innerHTML = html;
        if (this.cartSubtotalVal) this.cartSubtotalVal.textContent = `₹${subtotal.toFixed(2)}`;
        if (this.cartDeliveryVal) {
            this.cartDeliveryVal.innerHTML = deliveryFee === 0 
                ? `<span style="color:#10b981;font-weight:700;">FREE (₹0.00)</span>` 
                : `₹${deliveryFee.toFixed(2)}`;
        }
        if (this.cartTotalVal) {
            this.cartTotalVal.textContent = `₹${grandTotal.toFixed(2)}`;
        }
        if (window.lucide) lucide.createIcons();
    }

    flyToCart(sourceBtn) {
        const dest = this.floatingCartBtn;
        if (!dest || !sourceBtn) return;

        const srcRect = sourceBtn.getBoundingClientRect();
        const destRect = dest.getBoundingClientRect();

        const flyer = document.createElement('div');
        flyer.className = 'flying-cart-item';
        flyer.innerHTML = `<i data-lucide="package" style="width:18px;height:18px;"></i>`;
        flyer.style.top = `${srcRect.top + window.scrollY}px`;
        flyer.style.left = `${srcRect.left}px`;
        document.body.appendChild(flyer);
        if (window.lucide) lucide.createIcons();

        // Animate
        setTimeout(() => {
            flyer.style.top = `${destRect.top + window.scrollY}px`;
            flyer.style.left = `${destRect.left}px`;
            flyer.style.transform = 'scale(0.3) rotate(360deg)';
            flyer.style.opacity = '0.5';
        }, 20);

        setTimeout(() => {
            flyer.remove();
            dest.style.transform = 'scale(1.25)';
            setTimeout(() => dest.style.transform = '', 200);
        }, 750);
    }

    updatePayButtonLabel() {
        const total = this.getTotal().toFixed(2);
        const payBtnLabel = document.getElementById('payBtnLabel');
        if (!payBtnLabel) return;

        if (this.activePaymentTab === 'upi') {
            payBtnLabel.textContent = `Pay ₹${total} via UPI Instant`;
        } else if (this.activePaymentTab === 'card') {
            payBtnLabel.textContent = `Pay ₹${total} via Debit/Credit Card`;
        } else if (this.activePaymentTab === 'netbanking') {
            payBtnLabel.textContent = `Pay ₹${total} via Net Banking`;
        } else {
            payBtnLabel.textContent = `Confirm Farm Order ₹${total} (COD)`;
        }
    }

    openCheckoutModal() {
        if (this.cart.length === 0) {
            window.AgriApp?.showToast('Cart is empty! Add products first.', 'error');
            return;
        }

        const modal = document.getElementById('checkoutModal');
        if (modal) {
            const subtotal = this.getSubtotal();
            const delivery = this.getDeliveryFee();
            const total = this.getTotal();

            const subDisplay = document.getElementById('checkoutSubtotalDisplay');
            const delDisplay = document.getElementById('checkoutDeliveryDisplay');
            const totalDisplay = document.getElementById('checkoutModalTotal');
            const qrImg = document.getElementById('upiDynamicQr');

            if (subDisplay) subDisplay.textContent = `₹${subtotal.toFixed(2)}`;
            if (delDisplay) {
                delDisplay.innerHTML = delivery === 0 
                    ? `<span style="color:#10b981;font-weight:700;">FREE (₹0.00)</span>` 
                    : `₹${delivery.toFixed(2)}`;
            }
            if (totalDisplay) totalDisplay.textContent = `₹${total.toFixed(2)}`;

            if (qrImg) {
                qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=upi://pay?pa=agrismart@icici&pn=AgriSmart%20Precision&am=${total.toFixed(2)}&cu=INR`;
            }

            this.updatePayButtonLabel();
            modal.style.display = 'flex';
        }
    }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
    window.agriCart = new AgriCart();

    // Checkout Form Handler
    const checkoutForm = document.getElementById('mockCheckoutForm');
    const checkoutModal = document.getElementById('checkoutModal');
    const closeCheckoutBtn = document.getElementById('closeCheckoutModal');

    if (closeCheckoutBtn) {
        closeCheckoutBtn.addEventListener('click', () => {
            if (checkoutModal) checkoutModal.style.display = 'none';
        });
    }

    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const items = window.agriCart.cart;
            const shipping = {
                name: document.getElementById('shipName')?.value || '',
                address: document.getElementById('shipAddress')?.value || '',
                city: document.getElementById('shipCity')?.value || '',
                phone: document.getElementById('shipPhone')?.value || ''
            };

            const tab = window.agriCart.activePaymentTab;
            let paymentMethodName = 'UPI (Google Pay / PhonePe)';
            if (tab === 'card') {
                const cardNum = document.getElementById('cardNumberInput')?.value || '4532 •••• •••• 8842';
                const last4 = cardNum.replace(/\s+/g, '').slice(-4) || '8842';
                paymentMethodName = `Card (Ending in ${last4})`;
            } else if (tab === 'netbanking') {
                const bank = document.querySelector('input[name="bankSelect"]:checked')?.value || 'SBI';
                paymentMethodName = `Net Banking (${bank})`;
            } else if (tab === 'cod') {
                paymentMethodName = 'Cash on Delivery';
            }

            const payment = {
                method: paymentMethodName,
                transaction_id: `TXN-${Date.now().toString(36).toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`
            };

            const submitBtn = document.getElementById('confirmPayBtn');
            const originalHtml = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;gap:0.6rem;">
                        <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle><path d="M12 2a10 10 0 0 1 10 10"></path></svg>
                        <span>Verifying with Payment Gateway...</span>
                    </div>
                `;
            }

            try {
                // Short realistic gateway animation
                await new Promise(r => setTimeout(r, 900));

                const res = await fetch('/marketplace/api/checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ items, shipping, payment })
                });

                const data = await res.json();

                if (data.success) {
                    // Trigger Confetti Burst
                    if (window.confetti) {
                        confetti({
                            particleCount: 120,
                            spread: 80,
                            origin: { y: 0.6 }
                        });
                    }

                    window.agriCart.clear();
                    if (checkoutModal) checkoutModal.style.display = 'none';
                    window.agriCart.closeDrawer();

                    window.AgriApp?.showToast('Payment Authorized & Order Confirmed! 🎉 Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/marketplace/orders';
                    }, 1400);
                } else {
                    window.AgriApp?.showToast(data.message || 'Payment failed.', 'error');
                }
            } catch (err) {
                window.AgriApp?.showToast('Network error during payment verification.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalHtml;
                }
            }
        });
    }
});
