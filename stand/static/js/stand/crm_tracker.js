document.addEventListener('DOMContentLoaded', () => {
    // Inject CSRF token meta dynamically if it doesn't exist
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = cookie.substring(10);
                    break;
                }
            }
        }
        return cookieValue;
    }

    const clickElements = document.querySelectorAll('.js-add-to-cart');
    
    clickElements.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const productId = btn.getAttribute('data-product-id');
            if (!productId) return;
            
            fetch('/crm/track_click/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(res => res.json())
            .then(data => console.log('CRM Tracked:', data))
            .catch(err => console.error('CRM Check:', err));
        });
    });
});