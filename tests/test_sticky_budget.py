import asyncio
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from starlette.requests import Request

from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers import executions as execution_routes
from app.services.execution_service import complete_item, create_execution_from_template
from app.services.template_service import add_item_to_template, create_template


ROOT = Path(__file__).resolve().parents[1]


def make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
        }
    )


def render_items_fragment(db, user, group, execution) -> str:
    response = asyncio.run(
        execution_routes._get_items_fragment(
            make_request(), execution.id, db, user, group
        )
    )
    return response.body.decode()


def test_in_progress_budget_fragment_exposes_sticky_summary_contract(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(
        db, group, "Mensal", RecurrenceType.monthly, budget=100
    )
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 8, 3, tzinfo=timezone.utc), user
    )
    execution.status = ExecutionStatus.in_progress
    db.commit()
    complete_item(db, execution.items[0], 1, 80)

    body = render_items_fragment(db, user, group, execution)

    assert 'data-execution-budget-summary' in body
    assert 'data-budget-sticky="true"' in body
    assert 'data-budget="100' in body
    assert 'data-total-spent="80' in body
    assert 'data-budget-level="info"' in body
    assert 'data-budget-message=' in body
    assert 'data-budget-values' in body
    assert 'data-budget-progress' in body
    assert 'data-budget-percent' in body
    assert 'class="execution-budget-sticky' in body


def test_scheduled_budget_is_not_sticky_and_missing_budget_has_no_summary(
    db, make_user, make_group
):
    user = make_user("bia@example.com")
    group = make_group(owner=user)
    template = create_template(
        db, group, "Semanal", RecurrenceType.weekly, budget=100
    )
    execution = create_execution_from_template(
        db, template, datetime(2026, 8, 10, tzinfo=timezone.utc), user
    )

    scheduled_body = render_items_fragment(db, user, group, execution)
    assert 'data-execution-budget-summary' in scheduled_body
    assert 'data-budget-sticky="false"' in scheduled_body
    assert 'class="execution-budget-sticky' not in scheduled_body

    execution.budget = None
    db.commit()
    no_budget_body = render_items_fragment(db, user, group, execution)
    assert 'data-execution-budget-summary' not in no_budget_body


def test_budget_controller_classifies_thresholds_and_only_notifies_on_rise():
    script = """
const budget = require('./app/static/js/execution-budget.js');
const names = [79, 80, 95, 100, 120].map((spent) => budget.budgetBand(spent, 100).name);
const notifications = [
  budget.shouldNotify('normal', 'info'),
  budget.shouldNotify('info', 'info'),
  budget.shouldNotify('warning', 'info'),
  budget.shouldNotify('info', 'warning'),
  budget.shouldNotify('warning', 'danger'),
];
process.stdout.write(JSON.stringify({ names, notifications }));
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout) == {
        "names": ["normal", "info", "warning", "danger", "danger"],
        "notifications": [True, False, False, True, True],
    }


def test_budget_toast_is_deduplicated_across_controller_instances():
    script = r"""
class Element {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.dataset = {};
    this.listeners = {};
    this.style = { setProperty() {} };
    this.classList = { toggle() {} };
    this.parent = null;
    this.textContent = '';
  }
  appendChild(child) { child.parent = this; this.children.push(child); return child; }
  replaceChildren() { this.children = []; }
  setAttribute() {}
  addEventListener(name, callback) { this.listeners[name] = callback; }
  querySelector(selector) {
    if (selector === '.toast-body') {
      if (!this.toastBody) this.toastBody = new Element('div');
      return this.toastBody;
    }
    return null;
  }
  remove() {
    if (this.parent) this.parent.children = this.parent.children.filter((child) => child !== this);
  }
}

const body = new Element('body');
const summary = new Element('summary');
summary.dataset.budget = '100';
summary.dataset.totalSpent = '0';
summary.dataset.budgetLevel = 'normal';
summary.dataset.budgetMessage = '';
summary.dataset.budgetSticky = 'false';
const alerts = new Element('alerts');
let toastContainer = null;
const document = {
  readyState: 'complete',
  body,
  createElement(tag) { return new Element(tag); },
  querySelector(selector) {
    if (selector === '[data-execution-budget-summary]') return summary;
    if (selector === '[data-budget-alerts]') return alerts;
    if (selector === '[data-budget-toast-container]') return toastContainer;
    return null;
  },
};
const originalAppendChild = body.appendChild.bind(body);
body.appendChild = function (child) {
  if (Object.hasOwn(child.dataset, 'budgetToastContainer')) toastContainer = child;
  return originalAppendChild(child);
};

let shown = 0;
global.window = {
  document,
  addEventListener() {},
  bootstrap: { Toast: class { show() { shown += 1; } } },
};

const path = require.resolve('./app/static/js/execution-budget.js');
const first = require(path);
delete require.cache[path];
const second = require(path);
const alert = [{ level: 'info', message: 'Atenção ao orçamento' }];
first.handleRemoteAlerts(alert);
second.handleRemoteAlerts(alert);
process.stdout.write(String(shown));
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == "1"


def test_budget_controller_handles_dynamic_fragments_navbar_and_toasts():
    controller = Path("app/static/js/execution-budget.js").read_text()
    detail = Path("app/templates/pages/executions/in_progress.html").read_text()
    sync = Path("app/static/js/execution-sync.js").read_text()
    styles = Path("app/static/css/jaci-theme.css").read_text()

    assert "/static/js/execution-budget.js" in detail
    assert "htmx:afterSwap" in controller
    assert "ResizeObserver" in controller
    assert "--jaci-execution-budget-top" in controller
    assert "bootstrap.Toast" in controller
    assert "data-budget-toast-container" in controller
    assert "handleRemoteAlerts" in controller
    assert "window.JaciExecutionBudget.handleRemoteAlerts(data.alerts" in sync
    assert ".execution-budget-sticky" in styles
    assert "position: sticky" in styles
    assert "z-index: 1010" in styles
    assert "var(--jaci-execution-budget-top" in styles


def test_offline_item_mutations_recalculate_budget_from_local_snapshot():
    script = Path("app/static/js/offline-cache.js").read_text()

    assert "function calculateExecutionTotal" in script
    assert "function refreshLocalExecutionBudget" in script
    assert "window.JaciExecutionBudget.updateTotal" in script
    assert "await refreshLocalExecutionBudget(operation.execution_id)" in script
    assert "const hasPendingItems = snapshot.pending_operations.some" in script
    assert "if (!navigator.onLine || hasPendingItems)" in script
    assert "refreshLocalExecutionBudget(currentExecutionIdFromPage(), false)" in script


def test_budget_controller_is_cached_for_offline_execution():
    worker = Path("app/static/js/service-worker.js").read_text()

    assert "const CACHE_VERSION = 'v26'" in worker
    assert "'/static/js/execution-budget.js'" in worker
