"""Contratos BL-0011: relatórios úteis e piso de cobertura realmente aplicado."""
import json
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_coverage(tmp_path, floor, *, failing=False):
    config = tmp_path/'coverage.ini'
    config.write_text(f'[run]\nbranch = True\nsource = app\n[report]\nfail_under = {floor}\n')
    test = tmp_path/'test_selected.py'
    test.write_text('from app.config import Settings\ndef test_selected():\n'
                    '    assert Settings(_env_file=None).app_version\n'
                    + ('    assert False\n' if failing else ''))
    reports = tmp_path/'reports'
    result = subprocess.run(
        ['bash','scripts/run_tests.sh','--coverage',f'--cov-config={config}','-q',str(test)],
        cwd=ROOT,env={**os.environ,'COVERAGE_REPORT_DIR':str(reports)},
        capture_output=True,text=True,timeout=30,
    )
    return result,reports


def test_coverage_reports_are_created_for_selected_tests(tmp_path):
    result,reports=run_coverage(tmp_path,0)
    assert result.returncode==0,result.stdout+result.stderr
    assert (reports/'coverage.xml').is_file()
    assert (reports/'html/index.html').is_file()
    summary=json.loads((reports/'coverage.json').read_text())
    assert summary['meta']['branch_coverage']
    assert 0 < summary['totals']['percent_covered'] < 100


def test_coverage_floor_fails_a_passing_selection(tmp_path):
    result,_=run_coverage(tmp_path,100)
    assert result.returncode!=0
    assert '1 passed' in result.stdout
    assert 'Required test coverage' in result.stdout


def test_test_failure_is_not_hidden_by_coverage(tmp_path):
    result,_=run_coverage(tmp_path,0,failing=True)
    assert result.returncode==1,result.stdout+result.stderr
    assert '1 failed' in result.stdout
