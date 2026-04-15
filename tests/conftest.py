import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


@pytest.fixture(scope="function", autouse=True)
def reset_config():
    from bbss.config import Config
    Config.reset()
    yield
    Config.reset()


@pytest.fixture(scope="function")
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CONSOLE_LOGGING", "false")
    monkeypatch.setenv("ML_ENABLED", "false")
    
    from bbss.config import Config
    Config._instance = None
    config = Config()
    Config.set_instance(config)
    
    from bbss.database.db import init_db
    init_db()
    
    yield str(db_path)


@pytest.fixture
def sample_user(test_db):
    from bbss.auth.signup import signup
    result = signup("testuser", "TestPassword123!")
    assert result["success"] is True
    return result


@pytest.fixture
def auth_token(test_db, sample_user):
    from bbss.auth.login import login
    result = login("testuser", "TestPassword123!")
    assert result["success"] is True
    return result["session_token"]
