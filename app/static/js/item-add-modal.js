/**
 * Item addition modal
 * Mantém o formulário canônico sobre a lista sem perder rolagem ou foco.
 */
(function (window) {
    'use strict';

    const TRIGGER_SELECTOR = '[data-item-add-trigger]';
    const MODAL_SELECTOR = '[data-item-add-modal]';
    const FORM_SELECTOR = '[data-item-add-form]';
    const DISMISS_SELECTOR = '[data-item-add-dismiss]';
    const FEEDBACK_SELECTOR = '[data-item-add-feedback]';
    const INITIAL_FOCUS_SELECTOR = '[data-item-add-initial-focus]';
    const FOCUSABLE_SELECTOR = [
        'a[href]',
        'button:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        '[tabindex]:not([tabindex="-1"])',
    ].join(',');
    const states = new WeakMap();

    function stateFor(modal) {
        if (!states.has(modal)) {
            states.set(modal, {
                trigger: null,
                scrollY: 0,
                resetOnClose: false,
            });
        }
        return states.get(modal);
    }

    function formFor(element) {
        return element && element.closest(FORM_SELECTOR);
    }

    function showFeedback(form, message) {
        const feedback = form?.querySelector(FEEDBACK_SELECTOR);
        if (!feedback) return;
        feedback.innerHTML = message
            ? `<div class="alert alert-danger alert-jaci mb-0" role="alert">${message}</div>`
            : '';
    }

    function escapeHtml(value) {
        const element = document.createElement('span');
        element.textContent = String(value || '');
        return element.innerHTML;
    }

    function showLocalModal(modal) {
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.dataset.jaciModalBackdrop = 'true';
        document.body.appendChild(backdrop);
        document.body.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
        modal.hidden = false;
        modal.removeAttribute('aria-hidden');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('role', 'dialog');
        modal.classList.add('show');
    }

    function hideLocalModal(modal) {
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
        modal.removeAttribute('aria-modal');
        modal.removeAttribute('role');
        document.querySelectorAll('[data-jaci-modal-backdrop]').forEach(function (backdrop) {
            backdrop.remove();
        });
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        modal.dispatchEvent(new Event('hidden.bs.modal'));
    }

    function openModal(trigger) {
        const modalId = trigger.getAttribute('aria-controls');
        const modal = modalId ? document.getElementById(modalId) : null;
        if (!modal || !modal.matches(MODAL_SELECTOR)) return;

        const state = stateFor(modal);
        state.trigger = trigger;
        state.scrollY = window.scrollY;
        state.resetOnClose = false;
        modal.hidden = false;

        if (window.JaciModal) {
            window.JaciModal.show(modal);
        } else {
            showLocalModal(modal);
        }

        window.requestAnimationFrame(function () {
            modal.querySelector(INITIAL_FOCUS_SELECTOR)?.focus();
        });
    }

    function hideModal(modal, resetForm) {
        if (!modal) return;
        stateFor(modal).resetOnClose = Boolean(resetForm);
        if (window.JaciModal) {
            window.JaciModal.hide(modal);
        } else {
            hideLocalModal(modal);
        }
    }

    function finishClose(modal) {
        const state = stateFor(modal);
        const form = modal.querySelector(FORM_SELECTOR);
        if (state.resetOnClose && form) {
            form.reset();
            showFeedback(form, '');
        }
        modal.hidden = true;
        window.scrollTo(0, state.scrollY);
        if (state.trigger && document.contains(state.trigger)) {
            state.trigger.focus();
        }
        state.resetOnClose = false;
    }

    function focusableElements(modal) {
        return Array.from(modal.querySelectorAll(FOCUSABLE_SELECTOR)).filter(function (element) {
            return !element.hidden && element.getAttribute('aria-hidden') !== 'true';
        });
    }

    function trapFocus(event, modal) {
        if (event.key !== 'Tab') return;
        const focusable = focusableElements(modal);
        if (focusable.length === 0) {
            event.preventDefault();
            return;
        }
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    function validateForm(event, form) {
        const name = form.querySelector('[name="name"]');
        if (name && !name.value.trim()) {
            event.preventDefault();
            event.stopImmediatePropagation();
            showFeedback(form, 'O nome do item é obrigatório.');
            name.focus();
            return false;
        }
        showFeedback(form, '');
        return true;
    }

    function completeSuccess(form) {
        const modal = form.closest(MODAL_SELECTOR);
        if (modal) hideModal(modal, true);
    }

    function refreshSidebarAfterOnlineSuccess(form) {
        const sidebarUrl = form.dataset.itemAddSidebarUrl;
        if (!sidebarUrl || !window.htmx) return;
        window.htmx.ajax('GET', sidebarUrl, {
            target: '#sidebar-container',
            swap: 'innerHTML',
        });
    }

    function initializeModal(modal) {
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        stateFor(modal);
        modal.addEventListener('hidden.bs.modal', function () {
            finishClose(modal);
        });
        modal.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                event.preventDefault();
                event.stopImmediatePropagation();
                hideModal(modal, false);
                return;
            }
            trapFocus(event, modal);
        });
    }

    function initialize() {
        document.querySelectorAll(MODAL_SELECTOR).forEach(initializeModal);

        document.addEventListener('click', function (event) {
            const trigger = event.target.closest(TRIGGER_SELECTOR);
            if (trigger) {
                event.preventDefault();
                openModal(trigger);
                return;
            }
            const dismiss = event.target.closest(DISMISS_SELECTOR);
            if (dismiss) {
                event.preventDefault();
                hideModal(dismiss.closest(MODAL_SELECTOR), false);
                return;
            }
            if (event.target.matches(MODAL_SELECTOR)) {
                hideModal(event.target, false);
            }
        });

        document.addEventListener('submit', function (event) {
            const form = formFor(event.target);
            if (form) validateForm(event, form);
        }, true);

        document.body.addEventListener('htmx:afterRequest', function (event) {
            const form = formFor(event.detail.elt);
            if (!form || !event.detail.successful) return;
            const serverError = event.detail.xhr?.getResponseHeader('X-Jaci-Item-Add-Error');
            if (serverError === 'true') return;
            refreshSidebarAfterOnlineSuccess(form);
            completeSuccess(form);
        });

        document.body.addEventListener('htmx:sendError', function (event) {
            const form = formFor(event.detail.elt);
            if (form) showFeedback(form, 'Não foi possível enviar o item. Tente novamente.');
        });
        document.body.addEventListener('htmx:responseError', function (event) {
            const form = formFor(event.detail.elt);
            if (form) showFeedback(form, 'Não foi possível adicionar o item. Revise os dados.');
        });
        document.addEventListener('jaci:item-add-success', function (event) {
            const form = formFor(event.target);
            if (form) completeSuccess(form);
        });
    }

    window.JaciItemAddModal = {
        open: openModal,
        hide: hideModal,
        showFeedback: function (form, message) {
            showFeedback(form, escapeHtml(message));
        },
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
})(window);
