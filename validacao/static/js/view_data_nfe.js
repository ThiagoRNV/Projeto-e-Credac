(function () {
    'use strict';

    const holder = document.getElementById('data-holder');
    if (!holder) return;

    const currentQuery = holder.dataset.currentQuery || '';
    const somenteVisualizacao = holder.dataset.somenteVisualizacao === 'true';

    const debounce = (fn, delay = 400) => {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(null, args), delay);
        };
    };

    function getCookie(name) {
        if (!document.cookie) return null;
        for (const cookie of document.cookie.split(';')) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                return decodeURIComponent(trimmed.substring(name.length + 1));
            }
        }
        return null;
    }

    function showToast(message, type = 'success') {
        const old = document.querySelector('.toast-success');
        if (old) old.remove();

        const colors = { success: '#28a745', error: '#dc3545', warning: '#ffc107', info: '#17a2b8' };
        const icons = {
            success: 'bi-check-circle',
            error: 'bi-x-circle',
            warning: 'bi-exclamation-triangle',
            info: 'bi-info-circle',
        };

        const toast = document.createElement('div');
        toast.className = 'toast-success';
        toast.style.backgroundColor = colors[type] || colors.success;
        toast.style.color = type === 'warning' ? '#000' : '#fff';
        toast.innerHTML = `<i class="bi ${icons[type] || icons.success}"></i> ${message}<div class="toast-progress"></div>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function getPageParams() {
        return new URLSearchParams(window.location.search);
    }

    function applyServerFilters() {
        const params = getPageParams();
        document.querySelectorAll('.filter-input').forEach((inp) => {
            if (!inp.name) return;
            const val = inp.value.trim();
            if (val) params.set(inp.name, val);
            else params.delete(inp.name);
        });
        const busca = document.getElementById('vd-global-search');
        if (busca) {
            const val = busca.value.trim();
            if (val) params.set('busca', val);
            else params.delete('busca');
        }
        const pageSizeSelect = document.getElementById('vd-page-size');
        if (pageSizeSelect) {
            const perPage = pageSizeSelect.value;
            if (perPage) params.set('per_page', perPage);
        }
        params.delete('page');
        const qs = params.toString();
        window.location.assign(qs ? `${window.location.pathname}?${qs}` : window.location.pathname);
    }

    const CAMPOS_NUMERICOS = new Set([
        'quantidade_prod', 'valor_unitario', 'base_icms', 'aliquota_icms',
        'valor_icms', 'valor_total', 'valor_ipi',
    ]);

    /** Converte string (pt-BR ou en) em número. */
    function parseNumeroBR(valor) {
        if (valor === null || valor === undefined) return null;
        const str = String(valor).trim();
        if (!str) return null;
        let normalizado = str;
        if (str.includes(',') && str.includes('.')) {
            normalizado = str.replace(/\./g, '').replace(',', '.');
        } else if (str.includes(',')) {
            normalizado = str.replace(',', '.');
        }
        const n = Number(normalizado);
        return Number.isFinite(n) ? n : null;
    }

    /** Formata número no padrão pt-BR: 1.000,00 / 2.000.000,00 */
    function formatarNumeroBR(valor) {
        const n = typeof valor === 'number' ? valor : parseNumeroBR(valor);
        if (n === null) return '';
        return n.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    /** Máscara enquanto digita: digitos → 0,01 / 1.000,00 */
    function formatarDigitosBR(digits) {
        let d = String(digits || '').replace(/\D/g, '');
        if (!d) return '';
        d = d.replace(/^0+/, '') || '0';
        while (d.length < 3) d = '0' + d;
        const cents = d.slice(-2);
        let intPart = d.slice(0, -2).replace(/^0+/, '') || '0';
        intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return `${intPart},${cents}`;
    }

    /** Valor limpo para o backend: 1000.00 */
    function paraValorBackend(valorFormatado) {
        const n = parseNumeroBR(valorFormatado);
        if (n === null) return '';
        return n.toFixed(2);
    }

    function aplicarMascaraNumerica(input) {
        const digits = input.value.replace(/\D/g, '');
        input.value = formatarDigitosBR(digits);
    }

    function initMascarasNumericas() {
        document.querySelectorAll('.input_cells.input-num').forEach((input) => {
            if (input.value.trim()) {
                input.value = formatarNumeroBR(input.value);
            }

            input.addEventListener('input', () => {
                aplicarMascaraNumerica(input);
            });

            input.addEventListener('blur', () => {
                if (!input.value.trim()) return;
                input.value = formatarNumeroBR(input.value);
            });

            input.addEventListener('focus', () => {
                if (!input.value.trim()) return;
                // mantém formatado; seleção facilita sobrescrever
                input.select();
            });
        });
    }

    function registrarEstadoInicial() {
        document.querySelectorAll('.input_cells').forEach((input) => {
            input.dataset.initialValue = input.value.trim();
        });
    }

    function inputModificado(input) {
        const atual = input.value.trim();
        const inicial = (input.dataset.initialValue ?? input.value).trim();
        if (input.classList.contains('input-num')) {
            const a = paraValorBackend(atual);
            const i = paraValorBackend(inicial);
            return a !== i;
        }
        return atual !== inicial;
    }

    function linhaModificada(row) {
        return Array.from(row.querySelectorAll('.input_cells')).some(inputModificado);
    }

    function obterLinhasModificadas() {
        return Array.from(document.querySelectorAll('tr[data-cod-part]')).filter(linhaModificada);
    }

    function houveModificacoes() {
        return obterLinhasModificadas().length > 0;
    }

    // Ordem das colunas da tabela (mesma ordem dos <td> de cada linha)
    const CAMPOS_LINHA = [
        'tipo', 'cnpj_cpf', 'numero_nota', 'chave_nota', 'nome', 'codigo_uf',
        'codigo_prod', 'descricao_prod', 'cfop_prod', 'ncm', 'quantidade_prod',
        'valor_unitario', 'base_icms', 'aliquota_icms', 'valor_icms', 'valor_total',
        'cst', 'cest', 'valor_ipi', 'tipo_operacao', 'numero_documento',
    ];

    function coletarDadosTabela() {
        return obterLinhasModificadas().map((row) => {
            const item = {
                cod_part: row.dataset.codPart || '',
                numero_nota_old: row.dataset.numeroNotaOld || '',
                codigo_prod_old: row.dataset.codigoProdOld || '',
                chave_nota_old: row.dataset.chaveNotaOld || '',
                data_inicio_sped: row.dataset.dataInicioSped || '',
            };
            Array.from(row.cells).forEach((td, indice) => {
                const campo = CAMPOS_LINHA[indice];
                if (!campo) return;
                const input = td.querySelector('.input_cells');
                if (!input) return;
                const bruto = input.value.trim();
                item[campo] = CAMPOS_NUMERICOS.has(campo) ? paraValorBackend(bruto) : bruto;
            });
            return item;
        });
    }

    window.salvarAlteracoes = function () {
        const empresaId = holder.dataset.empresaId;
        const urlSalvar = holder.dataset.urlSalvar;
        const dataSped = new URLSearchParams(currentQuery).get('data_sped') || '';
        if (!empresaId || !urlSalvar) {
            showToast('Dados incompletos para salvar', 'error');
            return;
        }
        const items = coletarDadosTabela();
        if (!items.length) {
            showToast('Sem alteração feita', 'warning');
            return;
        }
        showToast('Salvando alterações...', 'info');
        fetch(urlSalvar, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                opcs: 'salvar',
                empresa_id: empresaId,
                data_sped: dataSped,
                items,
            }),
        })
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then((data) => {
                if (data.status === 'ok') {
                    registrarEstadoInicial();
                    showToast('Alterações salvas com sucesso!');
                } else {
                    showToast('Erro ao salvar alterações', 'error');
                }
            })
            .catch(() => showToast('Erro na requisição', 'error'));
    };

    window.exportarRelatorio = function () {
        const empresaId = holder.dataset.empresaId;
        const urlExportar = holder.dataset.urlExportar;
        const params = new URLSearchParams(currentQuery);
        const dataSped = params.get('data_sped');
        if (!empresaId) {
            showToast('Empresa ID é obrigatório', 'error');
            return;
        }
        if (!dataSped) {
            showToast('Data SPED é obrigatória', 'error');
            return;
        }
        window.location.href = `${urlExportar}?empresa_id=${empresaId}&data_sped=${dataSped}`;
    };

    window.atualizarDados = function () {
        window.location.reload();
    };

    // Filtros por coluna
    document.querySelectorAll('.filter-input').forEach((input) => {
        input.addEventListener('input', debounce(applyServerFilters, 500));
    });

    const globalSearch = document.getElementById('vd-global-search');
    if (globalSearch) {
        globalSearch.addEventListener('input', debounce(applyServerFilters, 500));
        globalSearch.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') applyServerFilters();
        });
    }

    // Toggle filtros de coluna
    const btnToggleFilters = document.getElementById('vd-toggle-filters');
    const filterRow = document.querySelector('.filter-row');
    if (btnToggleFilters && filterRow) {
        btnToggleFilters.addEventListener('click', () => {
            filterRow.classList.toggle('filters-hidden');
            btnToggleFilters.classList.toggle('active');
        });
    }
    // Linhas por página: submit via form GET (onchange no template)

    // Redimensionamento de colunas
    function initColumnResizer() {
        document.querySelectorAll('.vd-data-table').forEach((table) => {
            const headers = table.querySelectorAll('thead tr:first-child th');
            headers.forEach((header, index) => {
                if (header.querySelector('.column-resizer')) return;
                const resizer = document.createElement('div');
                resizer.className = 'column-resizer';
                header.appendChild(resizer);

                let startX, startWidth, isResizing = false;

                const doResize = (e) => {
                    if (!isResizing) return;
                    const currentX = e.pageX || e.touches?.[0]?.pageX;
                    const newWidth = Math.max(60, startWidth + (currentX - startX));
                    header.style.width = `${newWidth}px`;
                    header.style.minWidth = `${newWidth}px`;
                    table.querySelectorAll('tr').forEach((row) => {
                        const cell = row.children[index];
                        if (cell) {
                            cell.style.width = `${newWidth}px`;
                            cell.style.minWidth = `${newWidth}px`;
                        }
                    });
                };

                const stopResize = () => {
                    isResizing = false;
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                };

                resizer.addEventListener('mousedown', (e) => {
                    isResizing = true;
                    startX = e.pageX;
                    startWidth = header.offsetWidth;
                    document.body.style.cursor = 'col-resize';
                    document.body.style.userSelect = 'none';
                    e.preventDefault();
                });
                document.addEventListener('mousemove', doResize);
                document.addEventListener('mouseup', stopResize);
            });
        });
    }

    initMascarasNumericas();
    registrarEstadoInicial();
    setTimeout(initColumnResizer, 150);
})();
