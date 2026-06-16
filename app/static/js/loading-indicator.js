(function () {
    'use strict';

    const SHOW_DELAY_MS = 120;
    const indicator = document.getElementById('page-loading');
    if (!indicator) return;

    let timer = null;
    let activeRequests = 0;

    function show() {
        clearTimeout(timer);
        timer = window.setTimeout(function () {
            document.body.classList.add('is-loading');
            indicator.hidden = false;
            indicator.setAttribute('aria-hidden', 'false');
        }, SHOW_DELAY_MS);
    }

    function hide() {
        clearTimeout(timer);
        activeRequests = 0;
        document.body.classList.remove('is-loading');
        indicator.hidden = true;
        indicator.setAttribute('aria-hidden', 'true');
    }

    function beginRequest() {
        activeRequests += 1;
        show();
    }

    function endRequest() {
        activeRequests = Math.max(0, activeRequests - 1);
        if (activeRequests === 0) {
            hide();
        }
    }

    function isPlainLeftClick(event) {
        return event.button === 0 && !event.metaKey && !event.ctrlKey
            && !event.shiftKey && !event.altKey;
    }

    function shouldShowForLink(link, event) {
        if (!isPlainLeftClick(event)) return false;
        if (!link || link.dataset.noLoading !== undefined) return false;
        if (link.target && link.target !== '_self') return false;
        if (link.hasAttribute('download')) return false;
        if (link.getAttribute('href')?.startsWith('#')) return false;
        if (link.getAttribute('role') === 'button' && link.dataset.bsToggle) return false;
        if (link.dataset.bsToggle) return false;

        const url = new URL(link.href, window.location.href);
        return url.origin === window.location.origin && url.href !== window.location.href;
    }

    document.addEventListener('click', function (event) {
        const link = event.target.closest('a[href]');
        if (shouldShowForLink(link, event)) {
            window.setTimeout(function () {
                if (!event.defaultPrevented) {
                    show();
                }
            }, 0);
        }
    }, { capture: true });

    document.addEventListener('submit', function (event) {
        const form = event.target;
        if (form?.dataset?.noLoading !== undefined) return;

        window.setTimeout(function () {
            if (!event.defaultPrevented) {
                show();
            }
        }, 0);
    }, { capture: true });

    document.body.addEventListener('htmx:beforeRequest', function () {
        beginRequest();
    });
    document.body.addEventListener('htmx:afterRequest', function () {
        endRequest();
    });
    document.body.addEventListener('htmx:sendError', hide);
    document.body.addEventListener('htmx:responseError', hide);
    document.body.addEventListener('htmx:timeout', hide);

    window.addEventListener('pageshow', hide);
    window.addEventListener('pagehide', hide);
})();
