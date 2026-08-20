function applyServerFilters() {
    const params = new URLSearchParams(window.location.search);
    document.querySelectorAll('.filter-input').forEach(inp => {
        if (inp.name && inp.value.trim()) {
            params.set(inp.name, inp.value.trim());
        } else if (inp.name) {
            params.delete(inp.name);
        }
    });
    params.delete('page');
    window.location.search = params.toString();
}

function clearServerFilters() {
    window.location.search = '';
}

const btnAplicar = document.getElementById('lp-btn-aplicar');
const btnLimpar = document.getElementById('lp-btn-limpar');

if (btnAplicar) btnAplicar.addEventListener('click', applyServerFilters);
if (btnLimpar) btnLimpar.addEventListener('click', clearServerFilters);

document.querySelectorAll('.filter-input').forEach(input => {
    input.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') {
            ev.preventDefault();
            applyServerFilters();
        }
    });
});

function formatarSaldo(input) {
    let valor = input.value;
    valor = valor.replace(/\D/g, '');
    if (valor.length) {
        valor = (Number(valor) / 100).toFixed(2);
        valor = valor.replace('.', ',');
        valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        input.value = valor;
    } else {
        input.value = '';
    }
}

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('show.bs.modal', function() {
        const form = this.querySelector('.form-produto-sped');
        if (form) {
            const saldoInputs = form.querySelectorAll('.saldo-inicial');
            saldoInputs.forEach(saldoInput => {
                if (saldoInput && saldoInput.value) {
                    formatarSaldo(saldoInput);
                }
            });
            const generoSelect = form.querySelector('select[name="genero"]');
            if (generoSelect && form.dataset.genero) {
                generoSelect.value = form.dataset.genero;
            }
        }
    });
});

document.addEventListener('input', function(ev) {
    if (ev.target.matches('.saldo-inicial')) {
        formatarSaldo(ev.target);
    }
});

document.querySelectorAll('.form-produto-sped').forEach(form => {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const modalElement = form.closest('.modal');
        const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Erro ao salvar produto.');
            }

            const mensagem = data.message;
            modal.hide();

            modalElement.addEventListener('hidden.bs.modal', () => {
                if (mensagem) {
                    const toast = document.createElement('div');
                    toast.className = 'toast align-items-center text-bg-success border-0 position-fixed top-0 end-0 m-3';
                    toast.setAttribute('role', 'alert');
                    toast.style.zIndex = '9999';
                    toast.innerHTML = `
                        <div class="d-flex">
                            <div class="toast-body"><i class="bi bi-check-circle-fill me-2"></i>${mensagem}</div>
                            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                        </div>
                    `;
                    document.body.appendChild(toast);
                    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
                    bsToast.show();
                    toast.addEventListener('hidden.bs.toast', () => toast.remove());
                }
            }, { once: true });
        } catch (error) {
            alert(error.message || 'Erro inesperado ao salvar produto.');
        }
    });
});
