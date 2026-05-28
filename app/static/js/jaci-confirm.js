/**
 * Jaci Confirm — Modal de confirmação global
 * 
 * Uso automático:
 *   Qualquer elemento com hx-confirm dispara o modal em vez do confirm() nativo.
 *
 * Uso programático:
 *   JaciConfirm.show({
 *       title: 'Excluir grupo?',
 *       message: 'Todos os dados do grupo serão perdidos.',
 *       okLabel: 'Sim, excluir',
 *       okClass: 'btn-danger',
 *       onConfirm: function() { ... }
 *   });
 */
(function () {
    'use strict';

    console.log("Iniciando Jaci Confirm...");

    window.JaciConfirm = {
        _pendingCallback: null,
        _pendingHtmxEvent: null,

        /**
         * Exibe o modal de confirmação.
         * @param {Object} options
         * @param {string} options.title - Título do modal
         * @param {string} options.message - Mensagem do corpo
         * @param {string} [options.okLabel] - Texto do botão confirmar
         * @param {string} [options.okClass] - Classes extras do botão confirmar
         * @param {string} [options.cancelLabel] - Texto do botão cancelar
         * @param {Function} options.onConfirm - Callback ao confirmar
         * @param {Function} [options.onCancel] - Callback ao cancelar
         */
        show: function (options) {
            const modalEl = document.getElementById('jaciConfirmModal');
            if (!modalEl) return;

            const titleEl = document.getElementById('jaciConfirmModalTitle');
            const bodyEl = document.getElementById('jaciConfirmModalBody');
            const okBtn = document.getElementById('jaciConfirmModalOk');
            const cancelBtn = document.getElementById('jaciConfirmModalCancel');

            // Define conteúdo
            if (titleEl) titleEl.textContent = options.title || 'Confirmar';
            if (bodyEl) bodyEl.textContent = options.message || 'Tem certeza?';
            if (okBtn) {
                okBtn.textContent = options.okLabel || 'Confirmar';
                okBtn.className = 'btn btn-sm ' + (options.okClass || 'btn-primary');
            }
            if (cancelBtn && options.cancelLabel) {
                cancelBtn.textContent = options.cancelLabel;
            }

            // Salva callbacks
            this._pendingCallback = options.onConfirm || null;
            this._onCancel = options.onCancel || null;

            // Abre o modal
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        },

        /**
         * Fecha o modal sem confirmar.
         */
        hide: function () {
            const modalEl = document.getElementById('jaciConfirmModal');
            if (modalEl) {
                bootstrap.Modal.getInstance(modalEl).hide();
            }
        },

        /**
         * Processa a confirmação.
         */
        _handleConfirm: function () {
            const callback = this._pendingCallback;
            const htmxEvent = this._pendingHtmxEvent;

            this._pendingCallback = null;
            this._pendingHtmxEvent = null;
            this.hide();

            // Se veio de um evento HTMX (hx-confirm), dispara a requisição
            if (htmxEvent) {
                htmxEvent.detail.issueRequest(true);
                return;
            }

            // Se veio de chamada programática, executa o callback
            if (typeof callback === 'function') {
                callback();
            }
        },

        /**
         * Processa o cancelamento.
         */
        _handleCancel: function () {
            const onCancel = this._onCancel;
            this._pendingCallback = null;
            this._pendingHtmxEvent = null;
            this._onCancel = null;

            if (typeof onCancel === 'function') {
                onCancel();
            }
        }
    };

    // ── Event Listeners ──

    // Intercepta hx-confirm do HTMX
    document.body.addEventListener('htmx:confirm', function (event) {
        const message = event.detail.elt.getAttribute('hx-confirm');
        if (!message) return;

        // Cancela o confirm nativo
        event.preventDefault();

        // Salva o evento HTMX para disparar depois
        window.JaciConfirm._pendingHtmxEvent = event;

        const okLabel = event.detail.elt.getAttribute('data-jaci-confirm-ok-label');
        const okClass = event.detail.elt.getAttribute('data-jaci-confirm-ok-class');

        // Mostra o modal
        window.JaciConfirm.show({
            title: 'Confirmar',
            message: message,
            okLabel: okLabel || 'Confirmar',
            okClass: okClass || null,
        });
    });

    // Botão Confirmar do modal
    document.addEventListener('click', function (event) {
        if (event.target.id === 'jaciConfirmModalOk') {
            window.JaciConfirm._handleConfirm();
        }
    });

    // Limpeza ao fechar o modal
    document.addEventListener('hidden.bs.modal', function (event) {
        if (event.target.id === 'jaciConfirmModal') {
            window.JaciConfirm._handleCancel();
        }
    });
    console.log("Jaci Confirm iniciado!");
})();