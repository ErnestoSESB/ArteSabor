document.addEventListener('DOMContentLoaded', () => {
    const track = document.querySelector('.carousel-track');
    const items = track ? track.querySelectorAll('.carousel-item') : [];
    const nextBtn = document.querySelector('.nav-next');
    const prevBtn = document.querySelector('.nav-prev');
    const addToCartButtons = document.querySelectorAll('.js-add-to-cart');

    let index = 0;
    let autoPlayInterval = null;
    const gap = 20;
    const autoplayDelay = 3000;

    function getMetrics() {
        const itemWidth = items.length > 0 ? items[0].offsetWidth : 0;
        const containerWidth = track && track.parentElement ? track.parentElement.clientWidth : 0;
        const visibleItems = itemWidth > 0 ? Math.max(1, Math.floor((containerWidth + gap) / (itemWidth + gap))) : 1;
        const maxIndex = Math.max(items.length - visibleItems, 0);
        return { itemWidth, maxIndex };
    }

    function moveCarousel() {
        if (!track || items.length === 0) {
            return;
        }

        const { itemWidth, maxIndex } = getMetrics();
        if (itemWidth === 0) {
            return;
        }

        if (index > maxIndex) {
            index = 0;
        }

        const offset = index * (itemWidth + gap);
        track.style.transform = `translateX(-${offset}px)`;
    }

    function nextSlide() {
        if (items.length <= 1) {
            return;
        }

        const { maxIndex } = getMetrics();
        index = index >= maxIndex ? 0 : index + 1;
        moveCarousel();
    }

    function prevSlide() {
        if (items.length <= 1) {
            return;
        }

        const { maxIndex } = getMetrics();
        index = index <= 0 ? maxIndex : index - 1;
        moveCarousel();
    }

    function stopAutoplay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
        }
    }

    function startAutoplay() {
        stopAutoplay();

        if (items.length > 1) {
            autoPlayInterval = setInterval(nextSlide, autoplayDelay);
        }
    }

    if (track && items.length > 0) {
        moveCarousel();
        startAutoplay();

        track.addEventListener('mouseenter', stopAutoplay);
        track.addEventListener('mouseleave', startAutoplay);

        window.addEventListener('resize', moveCarousel);
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            nextSlide();
            startAutoplay();
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            prevSlide();
            startAutoplay();
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }

    const csrfToken = getCookie('csrftoken');

    async function postAddToCart(button, quantity = 1) {
        const normalizedQuantity = parseInt(quantity, 10);
        if (!Number.isFinite(normalizedQuantity) || normalizedQuantity <= 0) {
            closeModal();
            return;
        }
        closeModal();
        const url = button.dataset.addUrl;
        if (!url) {
            return;
        }

        button.disabled = true;
        const originalLabel = button.textContent;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quantity: normalizedQuantity })
            });

            if (!response.ok) {
                throw new Error('Falha ao adicionar item no carrinho.');
            }

            button.textContent = '✓';
            setTimeout(() => {
                button.textContent = originalLabel;
                button.disabled = false;
            }, 700);
        } catch (error) {
            button.textContent = '!';
            setTimeout(() => {
                button.textContent = originalLabel;
                button.disabled = false;
            }, 1000);
        }
    }

    
    const modal = document.getElementById('quantity-modal');
    const modalClose = modal ? modal.querySelector('.close-modal') : null;
    const modalMinus = document.getElementById('modal-qty-minus');
    const modalPlus = document.getElementById('modal-qty-plus');
    const modalInput = document.getElementById('modal-qty-input');
    const modalConfirm = document.getElementById('modal-confirm-add');
    const modalProductName = document.getElementById('modal-product-name');
    const modalProductImage = document.getElementById('modal-product-image');
    
    let currentButton = null;
    let closeModalTimer = null;
    const modalTransitionDurationMs = 220;

    function openModal() {
        if (!modal) {
            return;
        }

        if (closeModalTimer) {
            clearTimeout(closeModalTimer);
            closeModalTimer = null;
        }

        modal.style.display = "flex";
        modal.classList.remove('is-closing');
        requestAnimationFrame(() => {
            modal.classList.add('is-open');
        });
    }

    function closeModal() {
        if (modal) {
            if (closeModalTimer) {
                clearTimeout(closeModalTimer);
            }

            modal.classList.remove('is-open');
            modal.classList.add('is-closing');

            closeModalTimer = setTimeout(() => {
                modal.classList.remove('is-closing');
                modal.style.display = "none";
                closeModalTimer = null;
            }, modalTransitionDurationMs);
        }
    }

    const customModal = document.getElementById('custom-hundred-modal');
    const customOpenBtn = document.getElementById('open-custom-hundred-modal');
    const customCloseBtn = document.getElementById('close-custom-hundred-modal');
    const customAddThirdFlavorBtn = document.getElementById('custom-add-third-flavor');
    const customRemoveThirdFlavorBtn = document.getElementById('custom-remove-third-flavor');
    const customThirdFlavorRow = document.getElementById('custom-third-flavor-row');
    const customFlavorSelects = customModal ? customModal.querySelectorAll('.custom-flavor-select') : [];
    const customTotalUnitsEl = document.getElementById('custom-total-units');
    const customTotalPriceEl = document.getElementById('custom-total-price');
    const customDistributionEl = document.getElementById('custom-distribution-text');
    const customMessageEl = document.getElementById('custom-hundred-message');
    const customAddBtn = document.getElementById('custom-hundred-add-btn');
    const customAddUrlInput = document.getElementById('custom-hundred-add-url');
    let closeCustomModalTimer = null;
    function getAutoDistribution(count) {
        if (count === 2) {
            return [50, 50];
        }
        if (count === 3) {
            return [33, 33, 34];
        }
        return [];
    }
    function openCustomModal() {
        if (!customModal) {
            return;
        }
        if (closeCustomModalTimer) {
            clearTimeout(closeCustomModalTimer);
            closeCustomModalTimer = null;
        }
        customModal.style.display = 'flex';
        customModal.classList.remove('is-closing');
        requestAnimationFrame(() => {
            customModal.classList.add('is-open');
        });
    }

    function resetCustomHundredForm() {
        customFlavorSelects.forEach((select) => {
            select.value = '';
        });

        if (customThirdFlavorRow) {
            customThirdFlavorRow.classList.add('is-hidden');
        }
        if (customAddThirdFlavorBtn) {
            customAddThirdFlavorBtn.style.display = 'inline-block';
        }
        if (customRemoveThirdFlavorBtn) {
            customRemoveThirdFlavorBtn.classList.add('is-hidden');
        }
        if (customAddBtn) {
            customAddBtn.disabled = true;
        }
    }

    function closeCustomModal() {
        if (!customModal) {
            return;
        }

        if (closeCustomModalTimer) {
            clearTimeout(closeCustomModalTimer);
        }

        customModal.classList.remove('is-open');
        customModal.classList.add('is-closing');

        closeCustomModalTimer = setTimeout(() => {
            customModal.classList.remove('is-closing');
            customModal.style.display = 'none';
            closeCustomModalTimer = null;
        }, modalTransitionDurationMs);
    }

    function setCustomMessage(message, isError = true) {
        if (!customMessageEl) {
            return;
        }

        customMessageEl.textContent = message || '';
        if (isError) {
            customMessageEl.classList.remove('success');
        } else {
            customMessageEl.classList.add('success');
        }
    }

    function readCustomHundredSelection() {
        const selectedProducts = [];
        const usedProductIds = new Set();
        let hasDuplicateFlavor = false;

        customFlavorSelects.forEach((select) => {
            const productId = select ? String(select.value || '').trim() : '';

            if (!productId) {
                return;
            }

            if (usedProductIds.has(productId)) {
                hasDuplicateFlavor = true;
                return;
            }

            usedProductIds.add(productId);
            const selectedOption = select.options[select.selectedIndex];
            const unitPrice = Number(selectedOption ? selectedOption.dataset.price : 0) || 0;
            selectedProducts.push({ product_id: productId, unit_price: unitPrice });
        });

        const distribution = getAutoDistribution(selectedProducts.length);
        const selectedItems = selectedProducts.map((item, index) => ({
            product_id: item.product_id,
            quantity: distribution[index] || 0,
        }));

        let totalUnits = 0;
        let totalPrice = 0;
        selectedItems.forEach((item, index) => {
            totalUnits += item.quantity;
            totalPrice += selectedProducts[index].unit_price * item.quantity;
        });

        let distributionLabel = 'Selecione 2 ou 3 sabores';
        if (selectedProducts.length === 2) {
            distributionLabel = '2 sabores: 50 + 50 unidades';
        } else if (selectedProducts.length === 3) {
            distributionLabel = '3 sabores: 33 + 33 + 34 unidades';
        }

        return {
            selectedItems,
            selectedCount: selectedProducts.length,
            distribution,
            distributionLabel,
            totalUnits,
            totalPrice,
            hasDuplicateFlavor,
        };
    }

    function updateCustomHundredTotals() {
        if (!customModal) {
            return;
        }

        const result = readCustomHundredSelection();
        if (customTotalUnitsEl) {
            customTotalUnitsEl.textContent = String(result.totalUnits);
        }
        if (customTotalPriceEl) {
            customTotalPriceEl.textContent = result.totalPrice.toFixed(2);
        }
        if (customDistributionEl) {
            customDistributionEl.textContent = result.distributionLabel;
        }

        if (customAddBtn) {
            customAddBtn.disabled = result.hasDuplicateFlavor || result.selectedCount < 2 || result.selectedCount > 3;
        }
    }

    function closeModalIfZero() {
        const currentValue = parseInt(modalInput.value, 10);
        if (Number.isFinite(currentValue) && currentValue <= 0) {
            modalInput.value = 0;
            closeModal();
        }
    }

    if (modal) {
        if (modalClose) {
            modalClose.onclick = () => closeModal();
        }
        
        modalMinus.onclick = () => {
            const currentValue = parseInt(modalInput.value, 10);
            if (Number.isFinite(currentValue) && currentValue > 0) {
                modalInput.value = currentValue - 1;
            }
            closeModalIfZero();
        }
        modalPlus.onclick = () => { modalInput.value++; }

        modalInput.addEventListener('input', () => {
            closeModalIfZero();
        });

        modalConfirm.onclick = () => {
            if (currentButton) {
                postAddToCart(currentButton, modalInput.value);
            }
        };
    }

    if (customModal) {
        if (customOpenBtn) {
            customOpenBtn.addEventListener('click', () => {
                setCustomMessage('');
                resetCustomHundredForm();
                updateCustomHundredTotals();
                openCustomModal();
            });
        }

        if (customCloseBtn) {
            customCloseBtn.addEventListener('click', () => closeCustomModal());
        }

        customFlavorSelects.forEach((select) => {
            select.addEventListener('change', updateCustomHundredTotals);
        });

        if (customAddThirdFlavorBtn) {
            customAddThirdFlavorBtn.addEventListener('click', () => {
                if (customThirdFlavorRow) {
                    customThirdFlavorRow.classList.remove('is-hidden');
                }
                customAddThirdFlavorBtn.style.display = 'none';
                if (customRemoveThirdFlavorBtn) {
                    customRemoveThirdFlavorBtn.classList.remove('is-hidden');
                }
                updateCustomHundredTotals();
            });
        }

        if (customRemoveThirdFlavorBtn) {
            customRemoveThirdFlavorBtn.addEventListener('click', () => {
                if (customThirdFlavorRow) {
                    customThirdFlavorRow.classList.add('is-hidden');
                }

                if (customFlavorSelects.length >= 3) {
                    customFlavorSelects[2].value = '';
                }

                if (customAddThirdFlavorBtn) {
                    customAddThirdFlavorBtn.style.display = 'inline-block';
                }

                customRemoveThirdFlavorBtn.classList.add('is-hidden');
                updateCustomHundredTotals();
            });
        }

        if (customAddBtn && customAddUrlInput) {
            customAddBtn.addEventListener('click', async () => {
                setCustomMessage('');
                const result = readCustomHundredSelection();

                if (result.hasDuplicateFlavor) {
                    setCustomMessage('Escolha sabores diferentes em cada linha.');
                    return;
                }

                if (result.selectedCount < 2 || result.selectedCount > 3) {
                    setCustomMessage('Escolha 2 ou 3 sabores de brigadeiro.');
                    return;
                }

                if (result.totalUnits !== 100) {
                    setCustomMessage('O cento precisa totalizar exatamente 100 unidades.');
                    return;
                }

                const originalLabel = customAddBtn.textContent;
                customAddBtn.disabled = true;

                try {
                    const response = await fetch(customAddUrlInput.value, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest',
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ product_ids: result.selectedItems.map((item) => item.product_id) }),
                    });

                    const data = await response.json();

                    if (!response.ok || !data.ok) {
                        throw new Error(data && data.error ? data.error : 'Erro ao adicionar o cento ao carrinho.');
                    }

                    setCustomMessage('Cento personalizado adicionado ao carrinho com sucesso.', false);
                    customAddBtn.textContent = '✓';

                    setTimeout(() => {
                        customAddBtn.textContent = originalLabel;
                        customAddBtn.disabled = false;
                        closeCustomModal();
                    }, 700);
                } catch (error) {
                    setCustomMessage(error.message || 'Erro ao adicionar o cento ao carrinho.');
                    customAddBtn.textContent = '!';
                    setTimeout(() => {
                        customAddBtn.textContent = originalLabel;
                        customAddBtn.disabled = false;
                    }, 900);
                }
            });
        }
    }

    window.addEventListener('click', (event) => {
        if (modal && event.target === modal) {
            closeModal();
        }
        if (customModal && event.target === customModal) {
            closeCustomModal();
        }
    });

    addToCartButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (modal) {
                currentButton = button;
                const productName = button.dataset.name || "Produto";
                const productImage = button.dataset.image || '';

                modalProductName.textContent = productName;
                if (modalProductImage) {
                    modalProductImage.src = productImage;
                    modalProductImage.alt = `Imagem de ${productName}`;
                }
                modalInput.value = 1;
                openModal();
            } else {
                postAddToCart(button, 1);
            }
        });
    });

    updateCustomHundredTotals();

    window.changeSlide = function changeSlide(carouselId, dir) {
        const carousel = document.getElementById(carouselId);
        if (!carousel) {
            return;
        }

        const slides = carousel.querySelectorAll('.carousel-slide');
        if (slides.length <= 1) {
            return;
        }

        let active = Array.from(slides).findIndex((slide) => slide.classList.contains('active'));
        if (active < 0) {
            active = 0;
        }

        slides[active].classList.remove('active');
        active = (active + dir + slides.length) % slides.length;
        slides[active].classList.add('active');
    };
});

