import json
from pathlib import Path

from folkverse.config import Settings
from folkverse.main import create_app

root = Path(__file__).resolve().parents[1]
# Non-secret offline configuration; generation never connects to the database.
settings = Settings(
    _env_file=None,
    database_url="postgresql+psycopg://offline@localhost/offline",
    session_secret="offline-schema-generation-value-only-0000",
)
app = create_app(settings)
target = root / "packages/contracts/openapi.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(
    json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
)
app.state.engine.dispose()
print("Exported packages/contracts/openapi.json")
