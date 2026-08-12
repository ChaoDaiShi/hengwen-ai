from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


def test_alembic_upgrade_creates_core_tables(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'migration.sqlite').as_posix()}"
    project_root = Path(__file__).parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert {
        "alembic_version",
        "documents",
        "review_tasks",
        "review_issues",
        "task_events",
    } <= set(inspector.get_table_names())
    assert {"task_id", "status", "created_at"} <= {
        column_name
        for index in inspector.get_indexes("review_tasks")
        for column_name in index["column_names"]
    }
    engine.dispose()


def test_alembic_upgrade_and_downgrade_are_reversible(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'roundtrip.sqlite').as_posix()}"
    project_root = Path(__file__).parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")
    command.downgrade(config, "base")

    engine = create_engine(database_url)
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
    engine.dispose()
