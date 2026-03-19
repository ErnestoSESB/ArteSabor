function formatMoney(value) {
        return value.toFixed(2);
    }

    function recalculatePendingOrderTotal() {
        const qtyInputs = document.querySelectorAll('.pending-item-qty');
        const subtotalElements = document.querySelectorAll('.pending-item-subtotal');
        const totalElement = document.getElementById('pending-order-total');

        if (!qtyInputs.length || !totalElement) {
            return;
        }

        let total = 0;
        qtyInputs.forEach((input, index) => {
            const unitPrice = Number(input.dataset.unitPrice || 0);
            const qty = Math.max(0, parseInt(input.value || '0', 10) || 0);
            const subtotal = unitPrice * qty;
            total += subtotal;

            if (subtotalElements[index]) {
                subtotalElements[index].textContent = formatMoney(subtotal);
            }
        });

        totalElement.textContent = formatMoney(total);
    }

    function updatePendingQty(button, delta) {
        const input = delta < 0 ? button.nextElementSibling : button.previousElementSibling;
        if (!input) {
            return;
        }

        const currentValue = Math.max(0, parseInt(input.value || '0', 10) || 0);
        input.value = Math.max(0, currentValue + delta);
        recalculatePendingOrderTotal();
    }

    function allPendingQuantitiesAreZero() {
        const qtyInputs = document.querySelectorAll('.pending-item-qty');
        if (!qtyInputs.length) {
            return false;
        }

        for (const input of qtyInputs) {
            const qty = Math.max(0, parseInt(input.value || '0', 10) || 0);
            if (qty > 0) {
                return false;
            }
        }

        return true;
    }

    document.addEventListener('DOMContentLoaded', () => {
        recalculatePendingOrderTotal();

        // Lógica de agendamento
        var scheduleCheckbox = document.getElementById('schedule-order-checkbox');
        var payBtn = document.getElementById('pay-btn');
        var scheduleBtn = document.getElementById('schedule-btn');
        var scheduleInfo = document.getElementById('schedule-info');
        if (scheduleCheckbox) {
            scheduleCheckbox.addEventListener('change', function() {
                if (scheduleCheckbox.checked) {
                    payBtn.style.display = 'none';
                    scheduleBtn.style.display = 'block';
                    scheduleInfo.style.display = 'block';
                } else {
                    payBtn.style.display = 'block';
                    scheduleBtn.style.display = 'none';
                    scheduleInfo.style.display = 'none';
                }
            });
        }

        const pendingForm = document.getElementById('pending-order-form');
        if (pendingForm) {
            pendingForm.addEventListener('submit', function(event) {
                const submitter = event.submitter;
                if (!submitter) {
                    return;
                }
                if (submitter.value === 'cancel') {
                    const shouldCancel = confirm('Tem certeza que deseja cancelar o seu pedido?');
                    if (!shouldCancel) {
                        event.preventDefault();
                    }
                    return;
                }
                if (submitter.value === 'pay' && allPendingQuantitiesAreZero()) {
                    const shouldCancel = confirm('Tem certeza que deseja cancelar o seu pedido?');
                    if (!shouldCancel) {
                        event.preventDefault();
                        return;
                    }
                    submitter.value = 'cancel';
                }
            });
        }
    });