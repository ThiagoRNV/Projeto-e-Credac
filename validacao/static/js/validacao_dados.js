(function () {
    'use strict';

    const dashboard = document.querySelector('.vd-dashboard');
    if (!dashboard) return;

    const tabs = dashboard.querySelectorAll('.vd-tab');
    const panes = dashboard.querySelectorAll('.vd-tab-pane');
    const filterEmpresa = document.getElementById('vd-filter-empresa');
    const filterStatus = document.getElementById('vd-filter-status');
    const filterDataInicio = document.getElementById('vd-filter-data-inicio');
    const filterDataFim = document.getElementById('vd-filter-data-fim');
    const btnAplicar = document.getElementById('vd-btn-aplicar');
    const btnLimpar = document.getElementById('vd-btn-limpar');
    const pageSizeSelect = document.getElementById('vd-page-size');
    const pageInfo = document.getElementById('vd-page-info');
    const pageBtns = document.getElementById('vd-page-btns');

    let activeTab = 'andamento';
    let currentPage = 1;
    let pageSize = 10;

    function getActivePane() {
        return dashboard.querySelector('.vd-tab-pane.active');
    }

    function getVisibleRows(pane) {
        if (!pane) return [];
        return Array.from(pane.querySelectorAll('tbody tr[data-row]')).filter(
            (row) => !row.classList.contains('vd-filtered-out')
        );
    }

    const STATUS_TAB = {
        em_andamento: 'andamento',
        concluido: 'concluidas',
    };

    function applyFilters() {
        const empresaId = filterEmpresa ? filterEmpresa.value : '';
        const status = filterStatus ? filterStatus.value : '';
        const dataInicio = filterDataInicio ? filterDataInicio.value : '';
        const dataFim = filterDataFim ? filterDataFim.value : '';

        if (status && STATUS_TAB[status]) {
            switchTab(STATUS_TAB[status]);
        }

        panes.forEach((pane) => {
            pane.querySelectorAll('tbody tr[data-row]').forEach((row) => {
                let visible = true;

                if (empresaId && row.dataset.empresaId !== empresaId) {
                    visible = false;
                }

                if (status && row.dataset.status !== status) {
                    visible = false;
                }

                const rowDate = row.dataset.dataSped || '';
                if (dataInicio && rowDate && rowDate < dataInicio) visible = false;
                if (dataFim && rowDate && rowDate > dataFim) visible = false;

                row.classList.toggle('vd-filtered-out', !visible);
            });
        });

        currentPage = 1;
        updatePagination();
    }

    function clearFilters() {
        if (filterEmpresa) filterEmpresa.value = '';
        if (filterStatus) filterStatus.value = '';
        if (filterDataInicio) filterDataInicio.value = '';
        if (filterDataFim) filterDataFim.value = '';

        panes.forEach((pane) => {
            pane.querySelectorAll('tbody tr[data-row]').forEach((row) => {
                row.classList.remove('vd-filtered-out');
            });
        });

        currentPage = 1;
        updatePagination();
    }

    function updatePagination() {
        const pane = getActivePane();
        const rows = getVisibleRows(pane);
        const total = rows.length;
        const totalPages = Math.max(1, Math.ceil(total / pageSize));

        if (currentPage > totalPages) currentPage = totalPages;

        const start = (currentPage - 1) * pageSize;
        const end = Math.min(start + pageSize, total);

        rows.forEach((row, i) => {
            row.classList.toggle('vd-hidden', i < start || i >= end);
        });

        if (pageInfo) {
            if (total === 0) {
                pageInfo.textContent = 'Nenhum registro encontrado';
            } else {
                pageInfo.textContent = `Exibindo ${start + 1} a ${end} de ${total} registros`;
            }
        }

        renderPageButtons(totalPages);
    }

    function renderPageButtons(totalPages) {
        if (!pageBtns) return;
        pageBtns.innerHTML = '';

        const prev = document.createElement('button');
        prev.type = 'button';
        prev.className = 'vd-page-btn';
        prev.innerHTML = '<i class="bi bi-chevron-left"></i>';
        prev.disabled = currentPage <= 1;
        prev.addEventListener('click', () => {
            currentPage -= 1;
            updatePagination();
        });
        pageBtns.appendChild(prev);

        for (let p = 1; p <= totalPages; p++) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'vd-page-btn' + (p === currentPage ? ' active' : '');
            btn.textContent = String(p);
            btn.addEventListener('click', () => {
                currentPage = p;
                updatePagination();
            });
            pageBtns.appendChild(btn);
        }

        const next = document.createElement('button');
        next.type = 'button';
        next.className = 'vd-page-btn';
        next.innerHTML = '<i class="bi bi-chevron-right"></i>';
        next.disabled = currentPage >= totalPages;
        next.addEventListener('click', () => {
            currentPage += 1;
            updatePagination();
        });
        pageBtns.appendChild(next);
    }

    function switchTab(tabName) {
        activeTab = tabName;
        tabs.forEach((tab) => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        panes.forEach((pane) => {
            pane.classList.toggle('active', pane.dataset.tab === tabName);
        });
        currentPage = 1;
        updatePagination();
    }

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Ao finalizar, marca para abrir a aba Concluídas após o redirect.
    // A chave é por módulo (nfe / outros_modelos) para não vazar entre telas.
    const modulo = dashboard.dataset.modulo || window.location.pathname;
    const TAB_STORAGE_KEY = 'vd-active-tab:' + modulo;
    dashboard.querySelectorAll('form').forEach((form) => {
        if (!form.querySelector('.vd-acao-finalizar')) return;
        form.addEventListener('submit', () => {
            sessionStorage.setItem(TAB_STORAGE_KEY, 'concluidas');
        });
    });

    if (btnAplicar) btnAplicar.addEventListener('click', applyFilters);
    if (btnLimpar) btnLimpar.addEventListener('click', clearFilters);

    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', () => {
            pageSize = parseInt(pageSizeSelect.value, 10) || 10;
            currentPage = 1;
            updatePagination();
        });
    }

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach((el) => new bootstrap.Tooltip(el));

    const tabSalva = sessionStorage.getItem(TAB_STORAGE_KEY);
    if (tabSalva) {
        sessionStorage.removeItem(TAB_STORAGE_KEY);
        switchTab(tabSalva);
    } else {
        updatePagination();
    }
})();
