import httpx
from app.config import settings


async def get_user_profile(user_id: str, token: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{settings.backend_url}/users/{user_id}", headers=headers)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None
