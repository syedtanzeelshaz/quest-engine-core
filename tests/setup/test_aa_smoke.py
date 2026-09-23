def test_app_imports_cleanly():
    """Smoke test ensuring all modules, route schemas, and dependencies load cleanly."""
    import app.main

    assert app.main.app is not None

