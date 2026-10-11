from pathlib import Path

from streamlit.testing.v1 import AppTest

from athletics_etl.build_db import build_database
from athletics_etl.import_eada import import_year


def test_app_shows_source_and_undefined_reason(tmp_path, monkeypatch):
    db = tmp_path / "eada.sqlite"
    fixture = Path(__file__).parent / "fixtures" / "eada_synthetic.csv"
    build_database(import_year(fixture, 2024), db)
    monkeypatch.setenv("EADA_DB_PATH", str(db))
    app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=10).run()
    assert not app.exception
    text = " ".join(str(element.value) for element in app.markdown)
    assert "Source" in text
    assert "game-day" in text
