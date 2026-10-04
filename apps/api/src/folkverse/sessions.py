from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from itsdangerous import BadData, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from folkverse.config import Settings
from folkverse.database import AnonymousSession
from folkverse.errors import ApiError

COOKIE_NAME = "folkverse_session"


class SessionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.signer = URLSafeTimedSerializer(
            settings.session_secret.get_secret_value(),
            salt=f"folkverse-session-{settings.app_mode}-v1",
        )

    def encode(self, session_id: str) -> str:
        return str(self.signer.dumps(session_id))

    def require(self, token: str | None, db: Session) -> AnonymousSession:
        try:
            if token is None:
                raise BadData("Missing cookie")
            session_id = self.signer.loads(token, max_age=self.settings.session_ttl_seconds)
            if not isinstance(session_id, str):
                raise BadData("Malformed session")
            UUID(session_id)
        except (BadData, ValueError, TypeError) as exc:
            raise ApiError(
                401, "session_required", "Start an anonymous session to continue."
            ) from exc
        session = db.get(AnonymousSession, session_id)
        if session is None or session.expires_at <= datetime.now(UTC):
            raise ApiError(401, "session_expired", "Your anonymous session has expired.")
        return session

    def create(self, db: Session) -> AnonymousSession:
        now = datetime.now(UTC)
        session = AnonymousSession(
            id=str(uuid4()),
            created_at=now,
            expires_at=now + timedelta(seconds=self.settings.session_ttl_seconds),
        )
        db.add(session)
        db.commit()
        return session


def require_owner(owner_session: str, session: AnonymousSession) -> None:
    if owner_session != session.id:
        raise ApiError(403, "ownership_denied", "This record belongs to another session.")
