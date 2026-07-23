(function () {
    'use strict';

    const SHOW_DELAY_MS = 120;
    const HIDE_GRACE_MS = 160;
    const indicator = document.getElementById('page-loading');
    if (!indicator) return;

    let showTimer = null;
    let hideTimer = null;
    let anonymousRequests = 0;
    const activeRequests = new Set();

    function show() {
        clearTimeout(hideTimer);
        hideTimer = null;

        if (!indicator.hidden || showTimer !== null) return;

        showTimer = window.setTimeout(function () {
            showTimer = null;
            document.body.classList.add('is-loading');
            indicator.hidden = false;
            indicator.setAttribute('aria-hidden', 'false');
        }, SHOW_DELAY_MS);
    }

    function hide() {
        clearTimeout(showTimer);
        clearTimeout(hideTimer);
        showTimer = null;
        hideTimer = null;
        activeRequests.clear();
        anonymousRequests = 0;
        document.body.classList.remove('is-loading');
        indicator.hidden = true;
        indicator.setAttribute('aria-hidden', 'true');
    }

    function requestCount() {
        return activeRequests.size + anonymousRequests;
    }

    function beginRequest(event) {
        const xhr = event.detail?.xhr;
        if (xhr) {
            activeRequests.add(xhr);
        } else {
            anonymousRequests += 1;
        }
        show();
    }

    function scheduleHide() {
        if (requestCount() !== 0) return;

        clearTimeout(showTimer);
        showTimer = null;

        if (indicator.hidden) return;

        clearTimeout(hideTimer);
        hideTimer = window.setTimeout(function () {
            hideTimer = null;
            if (requestCount() === 0) {
                document.body.classList.remove('is-loading');
                indicator.hidden = true;
                indicator.setAttribute('aria-hidden', 'true');
            }
        }, HIDE_GRACE_MS);
    }

    function endRequest(event) {
        const xhr = event.detail?.xhr;
        if (xhr) {
            activeRequests.delete(xhr);
        } else {
            anonymousRequests = Math.max(0, anonymousRequests - 1);
        }
        scheduleHide();
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

    document.body.addEventListener('htmx:beforeRequest', beginRequest);
    document.body.addEventListener('htmx:afterRequest', endRequest);
    document.body.addEventListener('htmx:sendError', endRequest);
    document.body.addEventListener('htmx:responseError', endRequest);
    document.body.addEventListener('htmx:timeout', endRequest);

    window.addEventListener('pageshow', hide);
    window.addEventListener('pagehide', hide);
})();
