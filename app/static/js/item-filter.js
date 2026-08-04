/**
 * Jaci item filter
 * Filtra localmente itens já renderizados e coordena os collapses dos grupos.
 */
(function (global) {
    'use strict';

    const ROOT_SELECTOR = '[data-item-filter-root]';
    const INPUT_SELECTOR = '[data-item-filter-input]';
    const CLEAR_SELECTOR = '[data-item-filter-clear]';
    const GROUP_SELECTOR = '[data-item-filter-group]';
    const ROW_SELECTOR = '[data-item-filter-row]';
    const COUNT_SELECTOR = '[data-item-filter-count]';
    const EMPTY_SELECTOR = '[data-item-filter-empty]';
    const COLLAPSE_SELECTOR = '[data-item-filter-collapse]';
    const COLLAPSE_ALL_SELECTOR = '[data-item-filter-collapse-all]';
    const ORIGINAL_COUNT_ATTRIBUTE = 'data-item-filter-original-count';
    const FORCED_EXPANDED_ATTRIBUTE = 'data-item-filter-forced-expanded';

    function normalize(value) {
        return String(value || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLocaleLowerCase('pt-BR')
            .trim();
    }

    function setText(element, value) {
        if (element && element.textContent !== value) {
            element.textContent = value;
        }
    }

    function setCollapseState(collapse, expanded) {
        const group = collapse.closest(GROUP_SELECTOR);
        const trigger = group ? group.querySelector('[data-bs-toggle="collapse"]') : null;

        if (global.bootstrap && global.bootstrap.Collapse) {
            const instance = global.bootstrap.Collapse.getOrCreateInstance(collapse, {
                toggle: false,
            });
            if (expanded) instance.show();
            else instance.hide();
        } else {
            collapse.classList.toggle('show', expanded);
        }

        if (trigger) {
            trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        }
    }

    function expandMatchingGroup(collapse) {
        if (!collapse || collapse.classList.contains('show')) return;
        collapse.setAttribute(FORCED_EXPANDED_ATTRIBUTE, 'true');
        setCollapseState(collapse, true);
    }

    function restoreForcedCollapse(collapse) {
        if (!collapse || !collapse.hasAttribute(FORCED_EXPANDED_ATTRIBUTE)) return;
        collapse.removeAttribute(FORCED_EXPANDED_ATTRIBUTE);
        setCollapseState(collapse, false);
    }

    function formatMoney(value) {
        return Number(value || 0).toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    function updateCount(count, rows, visibleRows, queryActive) {
        if (!count) return;
        if (!count.hasAttribute(ORIGINAL_COUNT_ATTRIBUTE)) {
            count.setAttribute(ORIGINAL_COUNT_ATTRIBUTE, count.textContent);
        }
        if (!queryActive) {
            setText(count, count.getAttribute(ORIGINAL_COUNT_ATTRIBUTE));
            return;
        }

        const mode = count.dataset.itemFilterCountMode || 'plain';
        const visible = visibleRows.length;
        if (mode === 'template') {
            setText(count, `(${visible} ${visible === 1 ? 'item' : 'itens'})`);
            return;
        }
        if (mode === 'execution') {
            const completed = visibleRows.filter(function (row) {
                return row.dataset.itemFilterCompleted === 'true';
            }).length;
            const total = visibleRows.reduce(function (sum, row) {
                return sum + Number(row.dataset.itemFilterTotalPrice || 0);
            }, 0);
            setText(count, `(${completed}/${visible} - R$ ${formatMoney(total)})`);
            return;
        }
        if (mode === 'completed') {
            setText(count, `(${visible} ${visible === 1 ? 'comprado' : 'comprados'})`);
            return;
        }
        setText(count, `(${visible})`);
    }

    function syncControls(root, query) {
        root.querySelectorAll(INPUT_SELECTOR).forEach(function (input) {
            if (input.value !== query) input.value = query;
        });
        root.querySelectorAll(CLEAR_SELECTOR).forEach(function (button) {
            button.hidden = query.length === 0;
        });
    }

    function apply(root) {
        const state = root._jaciItemFilterState;
        if (!state || state.applying) return;
        state.applying = true;

        const query = normalize(state.query);
        const queryActive = query.length > 0;
        let visibleTotal = 0;

        root.querySelectorAll(GROUP_SELECTOR).forEach(function (group) {
            const rows = Array.from(group.querySelectorAll(ROW_SELECTOR));
            const visibleRows = rows.filter(function (row) {
                const name = normalize(row.dataset.itemFilterName || '');
                const matches = !queryActive || name.includes(query);
                row.hidden = !matches;
                return matches;
            });

            visibleTotal += visibleRows.length;
            group.hidden = queryActive && visibleRows.length === 0;
            updateCount(
                group.querySelector(COUNT_SELECTOR),
                rows,
                visibleRows,
                queryActive
            );

            const collapse = group.querySelector(COLLAPSE_SELECTOR);
            if (queryActive && visibleRows.length > 0) {
                expandMatchingGroup(collapse);
            } else if (!queryActive) {
                restoreForcedCollapse(collapse);
            }
        });

        root.querySelectorAll(EMPTY_SELECTOR).forEach(function (empty) {
            empty.hidden = !queryActive || visibleTotal > 0;
        });
        syncControls(root, state.query);
        state.applying = false;
    }

    function scheduleApply(root) {
        const state = root._jaciItemFilterState;
        if (!state || state.scheduled) return;
        state.scheduled = true;
        global.requestAnimationFrame(function () {
            state.scheduled = false;
            apply(root);
        });
    }

    function toggleAll(root) {
        const collapses = Array.from(root.querySelectorAll(GROUP_SELECTOR))
            .filter(function (group) { return !group.hidden; })
            .map(function (group) { return group.querySelector(COLLAPSE_SELECTOR); })
            .filter(Boolean);
        if (collapses.length === 0) return;

        const expand = collapses.some(function (collapse) {
            return !collapse.classList.contains('show');
        });
        collapses.forEach(function (collapse) {
            collapse.removeAttribute(FORCED_EXPANDED_ATTRIBUTE);
            setCollapseState(collapse, expand);
        });
    }

    function initRoot(root) {
        if (root._jaciItemFilterState) return;
        root._jaciItemFilterState = {
            query: '',
            applying: false,
            scheduled: false,
        };

        root.addEventListener('input', function (event) {
            if (!event.target.matches(INPUT_SELECTOR)) return;
            root._jaciItemFilterState.query = event.target.value;
            apply(root);
        });
        root.addEventListener('click', function (event) {
            const clear = event.target.closest(CLEAR_SELECTOR);
            if (clear) {
                root._jaciItemFilterState.query = '';
                apply(root);
                const input = root.querySelector(INPUT_SELECTOR);
                if (input) input.focus();
                return;
            }
            if (event.target.closest(COLLAPSE_ALL_SELECTOR)) {
                toggleAll(root);
            }
        });

        const observer = new MutationObserver(function () {
            scheduleApply(root);
        });
        observer.observe(root, { childList: true, subtree: true });
        root._jaciItemFilterState.observer = observer;
        apply(root);
    }

    function initAll() {
        document.querySelectorAll(ROOT_SELECTOR).forEach(initRoot);
    }

    document.body.addEventListener('htmx:configRequest', function (event) {
        const target = event.detail.target;
        if (!target || target.id !== 'items-container') return;
        const root = target.closest(ROOT_SELECTOR);
        if (!root) return;

        const expandedIds = [];
        target.querySelectorAll(`${COLLAPSE_SELECTOR}.show`).forEach(function (collapse) {
            if (collapse.id && !collapse.hasAttribute(FORCED_EXPANDED_ATTRIBUTE)) {
                expandedIds.push(collapse.id);
            }
        });
        event.detail.headers['X-Collapse-State'] = expandedIds.join(',');
    });

    global.JaciItemFilter = { apply: apply, init: initAll, normalize: normalize };
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})(window);
