(function (root, factory) {
    'use strict';

    const api = factory(root);
    if (typeof module === 'object' && module.exports) {
        module.exports = api;
    }
    if (root && root.document) {
        root.JaciExecutionBudget = api;
    }
})(typeof window !== 'undefined' ? window : globalThis, function (root) {
    'use strict';

    const BAND_RANK = {
        normal: 0,
        info: 1,
        warning: 2,
        danger: 3,
    };
    let currentLevel = null;
    let navbarObserver = null;

    function budgetBand(totalSpent, budget) {
        const total = Number(totalSpent) || 0;
        const limit = Number(budget) || 0;
        const percent = limit > 0 ? (total / limit) * 100 : 0;
        if (percent >= 100) return { name: 'danger', rank: 3, percent: percent };
        if (percent >= 95) return { name: 'warning', rank: 2, percent: percent };
        if (percent >= 80) return { name: 'info', rank: 1, percent: percent };
        return { name: 'normal', rank: 0, percent: percent };
    }

    function shouldNotify(previousLevel, nextLevel) {
        const previousRank = BAND_RANK[previousLevel] ?? 0;
        const nextRank = BAND_RANK[nextLevel] ?? 0;
        return nextRank > previousRank;
    }

    function formatMoney(value) {
        return `R$ ${Number(value || 0).toFixed(2)}`;
    }

    function alertMessage(level, totalSpent, budget, percent) {
        if (level === 'danger') {
            return `💸 Orçamento estourado em R$ ${(totalSpent - budget).toFixed(2)}!`;
        }
        if (level === 'warning') {
            return `🔴 Alerta: você está a R$ ${(budget - totalSpent).toFixed(2)} de estourar o orçamento!`;
        }
        if (level === 'info') {
            return `⚠️ Atenção: você atingiu ${percent.toFixed(0)}% do orçamento (${formatMoney(totalSpent)} de ${formatMoney(budget)})`;
        }
        return '';
    }

    function summaryElement() {
        if (!root.document) return null;
        return root.document.querySelector('[data-execution-budget-summary]');
    }

    function ensureToastContainer() {
        let container = root.document.querySelector('[data-budget-toast-container]');
        if (container) return container;

        container = root.document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.dataset.budgetToastContainer = '';
        root.document.body.appendChild(container);
        return container;
    }

    function showToast(level, message) {
        if (!message || !root.document || !root.bootstrap?.Toast) return;

        const container = ensureToastContainer();
        const toastElement = root.document.createElement('div');
        toastElement.className = `toast toast-jaci toast-${level}`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        toastElement.innerHTML = [
            '<div class="toast-header">',
            '<strong class="me-auto">Alerta de orçamento</strong>',
            '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fechar"></button>',
            '</div>',
            `<div class="toast-body"></div>`,
        ].join('');
        toastElement.querySelector('.toast-body').textContent = message;
        toastElement.addEventListener('hidden.bs.toast', function () {
            toastElement.remove();
        });
        container.appendChild(toastElement);
        new root.bootstrap.Toast(toastElement, { delay: 6000 }).show();
    }

    function renderAlertBanner(level, message) {
        const container = root.document?.querySelector('[data-budget-alerts]');
        if (!container) return;
        container.replaceChildren();
        if (level === 'normal' || !message) return;

        const alert = root.document.createElement('div');
        alert.className = `alert alert-${level} alert-jaci mb-3 d-flex align-items-center gap-2`;
        const text = root.document.createElement('span');
        text.textContent = message;
        alert.appendChild(text);
        container.appendChild(alert);
    }

    function applyVisualState(summary, totalSpent, band, message) {
        const budget = Number(summary.dataset.budget) || 0;
        const boundedWidth = Math.min(Math.max(band.percent, 0), 100);
        summary.dataset.totalSpent = String(totalSpent);
        summary.dataset.budgetLevel = band.name;
        summary.dataset.budgetMessage = message;

        const values = summary.querySelector('[data-budget-values]');
        const percent = summary.querySelector('[data-budget-percent]');
        const progress = summary.querySelector('[data-budget-progress]');
        if (values) values.textContent = `${formatMoney(totalSpent)} / ${formatMoney(budget)}`;
        if (percent) percent.textContent = `${band.percent.toFixed(0)}% utilizado`;
        if (progress) {
            progress.style.width = `${boundedWidth}%`;
            progress.setAttribute('aria-valuenow', String(band.percent));
            progress.classList.toggle('bg-warning-progress', band.name === 'info');
            progress.classList.toggle(
                'bg-danger-progress',
                band.name === 'warning' || band.name === 'danger'
            );
        }
        renderAlertBanner(band.name, message);
    }

    function transitionTo(level, message, notify) {
        const previousLevel = currentLevel;
        currentLevel = level;
        if (notify && previousLevel !== null && shouldNotify(previousLevel, level)) {
            showToast(level, message);
        }
    }

    function updateTotal(totalSpent, options) {
        const summary = summaryElement();
        if (!summary) return;

        const budget = Number(summary.dataset.budget) || 0;
        const total = Number(totalSpent) || 0;
        const band = budgetBand(total, budget);
        const message = options?.message || alertMessage(
            band.name, total, budget, band.percent
        );
        applyVisualState(summary, total, band, message);
        transitionTo(band.name, message, options?.notify !== false);
    }

    function syncNavbarOffset() {
        const summary = summaryElement();
        if (!summary || summary.dataset.budgetSticky !== 'true') return;
        const navbar = root.document.querySelector('.navbar-jaci');
        const navbarHeight = navbar ? navbar.getBoundingClientRect().height : 64;
        summary.style.setProperty(
            '--jaci-execution-budget-top',
            `${Math.ceil(navbarHeight) + 8}px`
        );
    }

    function refreshFromDocument(options) {
        const summary = summaryElement();
        if (!summary) {
            currentLevel = null;
            return;
        }
        const total = Number(summary.dataset.totalSpent) || 0;
        const level = summary.dataset.budgetLevel || budgetBand(
            total, summary.dataset.budget
        ).name;
        const message = summary.dataset.budgetMessage || alertMessage(
            level,
            total,
            Number(summary.dataset.budget) || 0,
            budgetBand(total, summary.dataset.budget).percent
        );
        transitionTo(level, message, options?.notify !== false);
        syncNavbarOffset();
    }

    function handleRemoteAlerts(alerts) {
        if (!Array.isArray(alerts) || alerts.length === 0) return;
        const alert = alerts[0];
        transitionTo(alert.level || 'normal', alert.message || '', true);
    }

    function init() {
        refreshFromDocument({ notify: false });
        const navbar = root.document.querySelector('.navbar-jaci');
        if (navbar && typeof root.ResizeObserver === 'function') {
            navbarObserver = new root.ResizeObserver(syncNavbarOffset);
            navbarObserver.observe(navbar);
        }
        root.addEventListener('resize', syncNavbarOffset);
        root.document.body.addEventListener('htmx:afterSwap', function (event) {
            if (event.detail?.target?.id === 'items-container') {
                refreshFromDocument({ notify: true });
            }
        });
    }

    if (root.document) {
        if (root.document.readyState === 'loading') {
            root.document.addEventListener('DOMContentLoaded', init, { once: true });
        } else {
            init();
        }
    }

    return {
        budgetBand: budgetBand,
        shouldNotify: shouldNotify,
        updateTotal: updateTotal,
        refreshFromDocument: refreshFromDocument,
        handleRemoteAlerts: handleRemoteAlerts,
    };
});
