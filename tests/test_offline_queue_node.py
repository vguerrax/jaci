"""Contratos FL-09 executam a fila JavaScript efetiva, sem serviço Python paralelo."""

from pathlib import Path
import shutil
import subprocess

import pytest


def test_fl09_real_indexeddb_queue_contracts():
    root = Path(__file__).resolve().parents[1]
    node = shutil.which("node")
    if not node:
        pytest.fail("Instale Node.js 22+ e execute npm ci --ignore-scripts.")
    if not (root / "node_modules/fake-indexeddb/package.json").is_file():
        pytest.fail("Dependência FL-09 ausente; execute npm ci --ignore-scripts.")
    result = subprocess.run(
        [node, "--test", "tests/js/offline_queue.test.cjs"],
        cwd=root, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
