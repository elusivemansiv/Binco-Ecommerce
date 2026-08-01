document.addEventListener('DOMContentLoaded', function() {
    
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    function updateHeaderUI(data) {
        // Update cart badge and total
        const cartBadge = document.getElementById('cart-badge-count');
        const cartTotal = document.getElementById('cart-total-price');
        const cartDropdown = document.getElementById('cart-dropdown-container');
        
        if (data.cart_count !== undefined && cartBadge) cartBadge.innerText = data.cart_count;
        if (data.cart_total !== undefined && cartTotal) cartTotal.innerText = '৳' + data.cart_total;
        if (data.cart_dropdown_html !== undefined && cartDropdown) cartDropdown.innerHTML = data.cart_dropdown_html;

        // Update wishlist badge
        const wishlistBadge = document.getElementById('wishlist-badge-count');
        const wishlistDropdown = document.getElementById('wishlist-dropdown-container');
        
        if (data.wishlist_count !== undefined && wishlistBadge) wishlistBadge.innerText = data.wishlist_count;
        if (data.wishlist_dropdown_html !== undefined && wishlistDropdown) wishlistDropdown.innerHTML = data.wishlist_dropdown_html;
    }

    // Intercept Add to Cart (simple link clicks — NOT form submissions)
    document.body.addEventListener('click', function(e) {
        let el = e.target.closest('a[href*="/cart/add/"]');
        if (el) {
            e.preventDefault();
            e.stopImmediatePropagation();
            
            // Prevent double-clicks
            if (el.dataset.loading === 'true') return;
            el.dataset.loading = 'true';
            
            const url = el.getAttribute('href');
            
            // Use GET — the original links are <a> tags which are GET requests.
            // The view handles GET for simple add (no color/size needed).
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateHeaderUI(data);
                } else if (data.status === 'error') {
                    alert(data.message);
                }
            })
            .catch(err => console.error('Add to cart error:', err))
            .finally(() => {
                el.dataset.loading = 'false';
            });
        }
    });

    // Intercept Add to Wishlist (simple link clicks)
    document.body.addEventListener('click', function(e) {
        let el = e.target.closest('a[href*="/wishlist/add/"]');
        if (el) {
            e.preventDefault();
            e.stopImmediatePropagation();
            
            if (el.dataset.loading === 'true') return;
            el.dataset.loading = 'true';
            
            const url = el.getAttribute('href');
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateHeaderUI(data);
                }
            })
            .catch(err => console.error('Add to wishlist error:', err))
            .finally(() => {
                el.dataset.loading = 'false';
            });
        }
    });

    // Intercept Add to Cart Form (product detail page with color/size)
    // Only intercept if triggered by the "Add to Cart" button, NOT "Buy Now"
    document.body.addEventListener('submit', function(e) {
        let form = e.target.closest('#add-to-cart-form');
        if (form) {
            // If "Buy Now" was clicked, let the form submit normally (redirects to cart)
            if (form.dataset.buyNow === 'true') {
                form.dataset.buyNow = 'false';
                return; // Don't intercept — let the browser submit normally
            }
            
            e.preventDefault();
            e.stopImmediatePropagation();
            
            const url = form.getAttribute('action');
            const formData = new FormData(form);
            formData.append('ajax', 'true');

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateHeaderUI(data);
                } else if (data.status === 'error') {
                    alert(data.message);
                }
            })
            .catch(err => console.error('Form add to cart error:', err));
        }
    });

    // Intercept Remove from Cart (Dropdown)
    document.body.addEventListener('click', function(e) {
        let btn = e.target.closest('.ajax-remove-cart');
        if (btn) {
            e.preventDefault();
            e.stopPropagation();
            
            const itemId = btn.getAttribute('data-item-id');
            const url = '/cart/remove/' + itemId + '/';
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateHeaderUI(data);
                }
            });
        }
    });

    // Intercept Remove from Wishlist (Dropdown)
    document.body.addEventListener('click', function(e) {
        let btn = e.target.closest('.ajax-remove-wishlist');
        if (btn) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = btn.getAttribute('data-product-id');
            const url = '/wishlist/remove/' + productId + '/';
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateHeaderUI(data);
                }
            });
        }
    });
});
