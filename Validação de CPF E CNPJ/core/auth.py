from datetime import date
from fastapi import Header, HTTPException
from core.db import get_conn


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key")

    today = date.today().isoformat()

    with get_conn() as conn:
        key_row = conn.execute(
            "SELECT key, plan, daily_limit FROM api_keys WHERE key = ?",
            (x_api_key,),
        ).fetchone()

        if not key_row:
            raise HTTPException(status_code=401, detail="Invalid API key")

        usage_row = conn.execute(
            "SELECT count FROM usage_daily WHERE key = ? AND day = ?",
            (x_api_key, today),
        ).fetchone()

        current = int(usage_row["count"]) if usage_row else 0
        limit = int(key_row["daily_limit"])

        if current >= limit:
            raise HTTPException(status_code=429, detail=f"Daily limit reached ({limit}/day)")

        # incrementa uso
        if usage_row:
            conn.execute(
                "UPDATE usage_daily SET count = count + 1 WHERE key = ? AND day = ?",
                (x_api_key, today),
            )
        else:
            conn.execute(
                "INSERT INTO usage_daily (key, day, count) VALUES (?, ?, 1)",
                (x_api_key, today),
            )

    return x_api_key
