import subprocess


def test_password_routes_bypass_worker_cache():
    subprocess.run(["node", "--test", "tests/js/password_cache.test.cjs"], check=True, timeout=20)
