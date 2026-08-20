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
        params.delete('page_energia');
        params.delete('page_comunicacao');
        const qs = params.toString();
        // Preserva a aba ativa ao recarregar com filtros
        const abaAtiva = document.querySelector('.vd-tab-btn.active');
        const hash = abaAtiva && abaAtiva.dataset.bsTarget !== '#tab-transportes' ? abaAtiva.dataset.bsTarget : '';
        window.location.assign((qs ? `${window.location.pathname}?${qs}` : window.location.pathname) + hash);
    }

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
            return paraValorBackend(atual) !== paraValorBackend(inicial);
        }
        return atual !== inicial;
    }

    function houveModificacoes() {
        return Array.from(document.querySelectorAll('.input_cells')).some(inputModificado);
    }

    // Ordem dos .input_cells na linha do documento D100
    const MAPA_INPUTS_D100 = [
        ['tipo', 0], ['cnpj_cpf', 1], ['nome', 2], ['num_doc', 3],
        ['chv_cte', 4], ['ser', 5], ['dt_doc', 6], ['vl_doc', 7], ['vl_serv', 8],
    ];

    // Ordem dos .input_cells na linha analítica D190
    const MAPA_INPUTS_D190 = [
        ['cfop', 0], ['cst_icms', 1], ['aliq_icms', 2], ['vl_opr', 3],
        ['vl_bc_icms', 4], ['vl_icms', 5], ['vl_red_bc', 6], ['cod_obs', 7],
    ];

    // Ordem dos .input_cells na linha do documento C500 (Energia)
    const MAPA_INPUTS_C500 = [
        ['tipo', 0], ['cnpj_cpf', 1], ['nome', 2], ['num_doc', 3],
        ['chv_doce', 4], ['ser', 5], ['dt_doc', 6], ['vl_doc', 7], ['vl_forn', 8],
    ];

    // Ordem dos .input_cells na linha analítica C590 (Energia)
    const MAPA_INPUTS_C590 = [
        ['cfop', 0], ['cst_icms', 1], ['aliq_icms', 2], ['vl_opr', 3],
        ['vl_bc_icms', 4], ['vl_icms', 5], ['vl_bc_icms_st', 6], ['vl_icms_st', 7],
        ['vl_red_bc', 8], ['cod_obs', 9],
    ];

    // Ordem dos .input_cells na linha do documento D500 (Comunicação)
    const MAPA_INPUTS_D500 = [
        ['tipo', 0], ['cnpj_cpf', 1], ['nome', 2], ['num_doc', 3],
        ['ser', 4], ['dt_doc', 5], ['vl_doc', 6], ['vl_serv', 7],
    ];

    // Ordem dos .input_cells na linha analítica D590 (Comunicação)
    const MAPA_INPUTS_D590 = MAPA_INPUTS_C590;

    function coletarLinhas(items, seletor, idDataset, idCampo, mapa, incluirCodPart) {
        document.querySelectorAll(seletor).forEach((row) => {
            const inputs = row.querySelectorAll('.input_cells');
            if (!inputs.length) return;
            const item = {};
            if (incluirCodPart) item.cod_part = row.dataset.codPart;
            if (row.dataset.nome) item.nome = row.dataset.nome;
            item[idCampo] = row.dataset[idDataset];
            mapa.forEach(([campo, indice]) => {
                const input = inputs[indice];
                if (!input) return;
                const bruto = input.value.trim();
                item[campo] = input.classList.contains('input-num')
                    ? paraValorBackend(bruto)
                    : bruto;
            });
            items.push(item);
        });
    }

    function coletarDadosTabela() {
        const items = [];

        // Transportes (D100/D190)
        coletarLinhas(items, 'tr[data-d100-id]', 'd100Id', 'd100_id', MAPA_INPUTS_D100, true);
        coletarLinhas(items, 'tr[data-d190-id]', 'd190Id', 'd190_id', MAPA_INPUTS_D190, false);

        // Energia (C500/C590)
        coletarLinhas(items, 'tr[data-c500-id]', 'c500Id', 'c500_id', MAPA_INPUTS_C500, true);
        coletarLinhas(items, 'tr[data-c590-id]', 'c590Id', 'c590_id', MAPA_INPUTS_C590, false);

        // Comunicação (D500/D590)
        coletarLinhas(items, 'tr[data-d500-id]', 'd500Id', 'd500_id', MAPA_INPUTS_D500, true);
        coletarLinhas(items, 'tr[data-d590-id]', 'd590Id', 'd590_id', MAPA_INPUTS_D590, false);

        return items;
    }

    // Garante que a chave "opcs" será sempre salva (bac)
    window.salvarAlteracoes = function () {
        const empresaId = holder.dataset.empresaId;
        const urlSalvar = holder.dataset.urlSalvar;
        if (!empresaId || !urlSalvar) {
            showToast('Dados incompletos para salvar', 'error');
            return;
        }
        if (!houveModificacoes()) {
            showToast('Sem alteração feita', 'warning');
            return;
        }
        const items = coletarDadosTabela();
        if (!items.length) {
            showToast('Nenhum dado para salvar', 'warning');
            return;
        }
        showToast('Salvando alterações...', 'info');
        // Sempre enviar "opcs": "salvar"
        fetch(urlSalvar, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ empresa_id: empresaId, items, opcs: "salvar" }) // NUNCA retirar "opcs", obrigatório para o back
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
                    showToast(data.message || 'Erro ao salvar alterações', 'error');
                }
            })
            .catch(() => showToast('Erro na requisição', 'error'));
    };

    // Garante que a chave "opcs" será sempre enviada como "exportar" para o bac
    window.exportarRelatorio = function () {
        const empresaId = holder.dataset.empresaId;
        const urlExportar = holder.dataset.urlExportar;
        const params = new URLSearchParams(currentQuery);
        const dataSped = params.get('data_sped');
        const opcs = 'exportar'; // sempre enviar ao bac

        if (!empresaId || !urlExportar) {
            showToast('Dados incompletos para exportar', 'error');
            return;
        }
        if (!dataSped) {
            showToast('Data SPED é obrigatória', 'error');
            return;
        }
        showToast('Gerando relatório...', 'info');
        fetch(urlExportar, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ empresa_id: empresaId, data_sped: dataSped, opcs }) // "opcs" sempre
        })
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                const contentType = r.headers.get('Content-Type') || '';
                if (contentType.includes('application/json')) {
                    return r.json().then((data) => {
                        throw new Error(data.message || 'Erro ao exportar relatório');
                    });
                }
                const disposition = r.headers.get('Content-Disposition') || '';
                const match = disposition.match(/filename="?([^"]+)"?/);
                const filename = match ? match[1] : 'relatorio_servicos.xlsx';
                return r.blob().then((blob) => ({ blob, filename }));
            })
            .then(({ blob, filename }) => {
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                link.remove();
                URL.revokeObjectURL(url);
                showToast('Relatório exportado com sucesso!');
            })
            .catch((err) => showToast(err.message || 'Erro na requisição', 'error'));
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

    // Reabre a aba indicada no hash da URL (usado pela paginação de Energia/Comunicação)
    function abrirAbaDoHash() {
        const hash = window.location.hash;
        if (!hash) return;
        const btn = document.querySelector(`.vd-tab-btn[data-bs-target="${hash}"]`);
        if (btn && window.bootstrap?.Tab) {
            window.bootstrap.Tab.getOrCreateInstance(btn).show();
        }
    }

    initMascarasNumericas();
    registrarEstadoInicial();
    abrirAbaDoHash();
    setTimeout(initColumnResizer, 150);
})();
