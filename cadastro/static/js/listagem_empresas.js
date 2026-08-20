(function () {
    'use strict';

    const dashboard = document.querySelector('.vd-dashboard');
    if (!dashboard) return;

    const tabs = dashboard.querySelectorAll('.vd-tab');
    const panes = dashboard.querySelectorAll('.vd-tab-pane');
    const filterRazao = document.getElementById('le-filter-razao');
    const filterCnpj = document.getElementById('le-filter-cnpj');
    const filterUf = document.getElementById('le-filter-uf');
    const filterStatus = document.getElementById('le-filter-status');
    const btnAplicar = document.getElementById('le-btn-aplicar');
    const btnLimpar = document.getElementById('le-btn-limpar');
    const pageSizeSelect = document.getElementById('le-page-size');
    const pageInfo = document.getElementById('le-page-info');
    const pageBtns = document.getElementById('le-page-btns');

    let activeTab = 'todas';
    let currentPage = 1;
    let pageSize = 10;

    const STATUS_TAB = {
        pendente: 'pendentes',
        completa: 'completas',
        inativa: 'inativas'
    };

    function getActivePane() {
        return dashboard.querySelector('.vd-tab-pane.active');
    }

    function getVisibleRows(pane) {
        if (!pane) return [];
        return Array.from(pane.querySelectorAll('tbody tr[data-row]')).filter(
            (row) => !row.classList.contains('vd-filtered-out')
        );
    }

    function applyFilters() {
        const razao = filterRazao ? filterRazao.value.trim().toLowerCase() : '';
        const cnpj = filterCnpj ? filterCnpj.value.trim().toLowerCase() : '';
        const uf = filterUf ? filterUf.value : '';
        const status = filterStatus ? filterStatus.value : '';

        panes.forEach((pane) => {
            pane.querySelectorAll('tbody tr[data-row]').forEach((row) => {
                let visible = true;

                if (razao && !(row.dataset.razao || '').includes(razao)) visible = false;
                if (cnpj && !(row.dataset.cnpj || '').includes(cnpj)) visible = false;
                if (uf && row.dataset.uf !== uf) visible = false;
                if (status && row.dataset.status !== status) visible = false;

                row.classList.toggle('vd-filtered-out', !visible);
            });
        });

        if (status && STATUS_TAB[status]) {
            switchTab(STATUS_TAB[status]);
        } else {
            currentPage = 1;
            updatePagination();
        }
        updateResumoCounts();
    }

    function clearFilters() {
        if (filterRazao) filterRazao.value = '';
        if (filterCnpj) filterCnpj.value = '';
        if (filterUf) filterUf.value = '';
        if (filterStatus) filterStatus.value = '';

        panes.forEach((pane) => {
            pane.querySelectorAll('tbody tr[data-row]').forEach((row) => {
                row.classList.remove('vd-filtered-out');
            });
        });

        currentPage = 1;
        updatePagination();
        updateResumoCounts();
    }

    function updateResumoCounts() {
        const todasPane = dashboard.querySelector('.vd-tab-pane[data-tab="todas"]');
        if (!todasPane) return;

        let pendentes = 0;
        let completas = 0;

        todasPane.querySelectorAll('tbody tr[data-row]').forEach((row) => {
            if (row.classList.contains('vd-filtered-out')) return;
            if (row.dataset.status === 'pendente') pendentes += 1;
            else completas += 1;
        });

        const countPendentes = document.getElementById('le-count-pendentes');
        const countCompletas = document.getElementById('le-count-completas');
        const countTotal = document.getElementById('le-count-total');

        if (countPendentes) countPendentes.textContent = pendentes;
        if (countCompletas) countCompletas.textContent = completas;
        if (countTotal) countTotal.textContent = pendentes + completas;
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

    if (btnAplicar) btnAplicar.addEventListener('click', applyFilters);
    if (btnLimpar) btnLimpar.addEventListener('click', clearFilters);

    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', () => {
            pageSize = parseInt(pageSizeSelect.value, 10) || 10;
            currentPage = 1;
            updatePagination();
        });
    }

    updatePagination();

    // Modal cadastro empresa: accordion visual + upload SPED
    const ceAccordion = document.getElementById('ceAccordion');
    if (ceAccordion) {
        ceAccordion.querySelectorAll('.collapse').forEach((panel) => {
            panel.addEventListener('show.bs.collapse', () => {
                const item = panel.closest('[data-ce-item]');
                if (item) item.classList.add('is-open');
            });
            panel.addEventListener('hide.bs.collapse', () => {
                const item = panel.closest('[data-ce-item]');
                if (item) item.classList.remove('is-open');
            });
        });
    }

    const spedInput = document.getElementById('ce_sped_empresa');
    const spedZone = document.getElementById('ceSpedZone');
    const spedFileName = document.getElementById('ceSpedFileName');

    function updateSpedFileLabel() {
        if (!spedInput || !spedFileName) return;
        if (spedInput.files && spedInput.files.length > 0) {
            spedFileName.textContent = spedInput.files[0].name;
            spedFileName.classList.remove('d-none');
        } else {
            spedFileName.textContent = '';
            spedFileName.classList.add('d-none');
        }
    }

    if (spedInput) {
        spedInput.addEventListener('change', updateSpedFileLabel);
    }

    if (spedZone && spedInput) {
        ['dragenter', 'dragover'].forEach((evt) => {
            spedZone.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
                spedZone.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach((evt) => {
            spedZone.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
                spedZone.classList.remove('dragover');
            });
        });
        spedZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer && e.dataTransfer.files;
            if (!files || !files.length) return;
            const file = files[0];
            if (!file.name.toLowerCase().endsWith('.txt')) return;
            const dt = new DataTransfer();
            dt.items.add(file);
            spedInput.files = dt.files;
            updateSpedFileLabel();
        });
    }

    const modalCadastro = document.getElementById('modalCadastrarEmpresa');
    if (modalCadastro) {
        modalCadastro.addEventListener('hidden.bs.modal', () => {
            modalCadastro.querySelectorAll('.collapse.show').forEach((panel) => {
                const inst = bootstrap.Collapse.getInstance(panel);
                if (inst) inst.hide();
            });
            modalCadastro.querySelectorAll('[data-ce-item]').forEach((item) => {
                item.classList.remove('is-open');
            });
            if (spedInput) spedInput.value = '';
            updateSpedFileLabel();
        });
    }
})();
