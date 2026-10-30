"""Contratos futuros BL-0011 para guardas do runner de navegador."""
import os
from pathlib import Path
import subprocess

import pytest

ROOT=Path(__file__).resolve().parents[1]


def test_ui_runner_refuses_production_environment(tmp_path):
    env_file=tmp_path/'.env.production'
    env_file.write_text('KEEP=original\n')
    result=subprocess.run(['bash','scripts/run_ui_tests.sh'],cwd=ROOT,
        env={**os.environ,'ENV_FILE':str(env_file)},capture_output=True,text=True,timeout=10)
    assert result.returncode!=0
    assert 'ambiente' in result.stderr.lower()
    assert env_file.read_text()=='KEEP=original\n'


def test_ui_runner_refuses_parallel_workers_without_starting_server(tmp_path):
    result=subprocess.run(['bash','scripts/run_ui_tests.sh'],cwd=ROOT,
        env={**os.environ,'ENV_FILE':str(tmp_path/'.env.test'),'UI_TEST_WORKERS':'4'},
        capture_output=True,text=True,timeout=10)
    assert result.returncode!=0
    assert 'UI_TEST_WORKERS' in result.stderr
    assert not list(tmp_path.iterdir())


def test_ui_summary_is_written_when_playwright_removes_empty_output(tmp_path):
    from scripts.ui_test_runner import write_result
    import json
    artifacts=tmp_path/'missing-output'
    write_result(artifacts,'synthetic-run','passed')
    assert json.loads((artifacts/'result.json').read_text())['status']=='passed'
