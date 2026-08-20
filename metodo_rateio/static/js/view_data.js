const debounce = (fn, delay = 400) => { 
    let t; 
    return (...args) => { 
        clearTimeout(t); 
        t = setTimeout(() => fn.apply(this, args), delay); 
    }; 
};

function applyServerFilters() {
    const params = new URLSearchParams(window.location.search);
    
    // Identificar qual aba está ativa
    const activeTab = document.querySelector('.nav-link.active');
    const activeTabId = activeTab ? activeTab.getAttribute('aria-controls') : null;
    
    if (activeTabId === 'producao-propria') {
        // Remover todos os filtros de terceiros quando estiver na aba de produção própria
        params.delete('tf0');
        params.delete('tf1');
        params.delete('tf2');
        params.delete('tf3');
        params.delete('tf4');
        params.delete('tf5');
        params.delete('tf6');
        
        // Aplicar filtros da aba de produção própria (que começam com 'f')
        document.querySelectorAll('#producao-propria .filter-input').forEach(inp => {
            if (inp.name && inp.name.startsWith('f')) {
                if (inp.value.trim()) {
                    params.set(inp.name, inp.value.trim());
                } else {
                    params.delete(inp.name);
                }
            }
        });
        params.delete('page');
        params.delete('page_terceiros');
    } else if (activeTabId === 'terceiros') {
        // Remover todos os filtros de produção própria quando estiver na aba de terceiros
        params.delete('f0');
        params.delete('f1');
        params.delete('f2');
        params.delete('f3');
        params.delete('f4');
        params.delete('f5');
        params.delete('f6');
        params.delete('f7');
        params.delete('f8');
        params.delete('f9');
        params.delete('f10');
        params.delete('f11');
        
        // Aplicar filtros da aba de terceiros (que começam com 'tf')
        document.querySelectorAll('#terceiros .filter-input').forEach(inp => {
            if (inp.name && inp.name.startsWith('tf')) {
                if (inp.value.trim()) {
                    // Manter os nomes originais 'tf0', 'tf1', etc.
                    params.set(inp.name, inp.value.trim());
                } else {
                    params.delete(inp.name);
                }
            }
        });
        params.delete('page_terceiros');
        params.delete('page');
    } else {
        // Fallback: aplicar todos os filtros sem remover nenhum
        document.querySelectorAll('.filter-input').forEach(inp => {
            if (inp.name && inp.value.trim()) {
                params.set(inp.name, inp.value.trim());
            } else if (inp.name) {
                params.delete(inp.name);
            }
        });
        params.delete('page');
        params.delete('page_terceiros');
    }
    
    window.location.search = params.toString();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showSuccessToast(message, isError = false) {
    const oldToast = document.querySelector(".toast-success");
    if (oldToast) oldToast.remove();

    const toast = document.createElement("div");
    toast.className = "toast-success";
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${isError ? "#dc3545" : "#28a745"};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
        animation: fadeIn 0.3s ease-in;
    `;
    toast.innerHTML = `<i class="bi ${isError ? 'bi-x-circle' : 'bi-check-circle'}"></i> ${message}`;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "fadeOut 0.3s ease-in forwards";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function salvarAlteracoes() {
    const holder = document.getElementById("data-holder");
    if (!holder) {
        showSuccessToast("❌ Erro: elemento data-holder não encontrado!", true);
        return;
    }
    
    const empresaId = holder.dataset.empresaId;
    const urlSalvar = holder.dataset.urlSalvar;
    
    if (!urlSalvar) {
        showSuccessToast("⚠️ URL de salvamento não configurada!", true);
        return;
    }

    // Coletar dados dos inputs editáveis
    const items = [];
    document.querySelectorAll('tr').forEach(row => {
        const inputs = row.querySelectorAll('.input_cells');
        if (inputs.length > 0) {
            const item = {};
            inputs.forEach((input, index) => {
                item[`field_${index}`] = input.value.trim();
            });
            if (Object.keys(item).length > 0) {
                items.push(item);
            }
        }
    });

    showSuccessToast("💾 Salvando alterações...");

    fetch(urlSalvar, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ empresa_id: empresaId, items: items })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            showSuccessToast("✅ Alterações salvas com sucesso!");
        } else {
            showSuccessToast("⚠️ Erro ao salvar alterações!", true);
        }
    })
    .catch(err => {
        console.error(err);
        showSuccessToast("❌ Erro na requisição!", true);
    });
}

// Adicionar event listeners aos filtros quando a página carregar
function setupFilterListeners() {
    document.querySelectorAll('.filter-input').forEach(input => {
        // Remover listeners antigos se existirem
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);
        // Adicionar novo listener
        newInput.addEventListener('input', debounce(applyServerFilters, 500));
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() {
        setupFilterListeners();
    });
} else {
    setupFilterListeners();
}

// Reconfigurar listeners quando mudar de aba (caso os elementos sejam recriados)
document.addEventListener('shown.bs.tab', function() {
    setTimeout(setupFilterListeners, 100);
});

