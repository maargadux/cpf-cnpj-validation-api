import os
import secrets
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Header, HTTPException

from validators.cpf import validar_cpf, formato_cpf
from validators.cnpj import validar_cnpj, formato_cnpj
from validators.document import validar_documento
from models.validation_response import ValidationResponse

from core.db import init_db, get_conn
from core.auth import require_api_key

# config inicial

load_dotenv()

ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    raise RuntimeError("ADMIN_KEY não definida no ambiente")

app = FastAPI(
    title="API de validação de CPF e CNPJ",
    version="0.0.2",
    description="Uma API para validação de CPF e CNPJ",
)

# cria as tabelas quando a API sobe
@app.on_event("startup")
def on_startup():
    init_db()

# fecha / limpa coisas quando a API desliga
@app.on_event("shutdown")
def on_shutdown():
    # aqui você poderia fechar conexões, flush de logs, etc.
    print("🔻 API está sendo desligada...")

# rotas públicas

@app.get("/", tags=["Health"], summary="Health check")
def home():
    return {"status": "ok", "message": "API de validação de CPF e CNPJ"}

def resolve_key_by_prefix(prefix: str):
    if len(prefix) < 4:
        raise HTTPException(status_code=400, detail="Prefixo muito curto")

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT key FROM api_keys WHERE key LIKE ?",
            (f"{prefix}%",),
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="Nenhuma API key encontrada com esse prefixo")

    if len(rows) > 1:
        raise HTTPException(
            status_code=409,
            detail="Prefixo ambíguo, mais de uma API key encontrada",
        )

    return rows[0]["key"]

# rotas admin


@app.post("/admin/create-key", tags=["Admin"], summary="Crie uma API Key (admin)")
def create_key(
    plan: str = "free",
    daily_limit: int = 100,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Chave de admin inválida")

    new_key = secrets.token_urlsafe(24)

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO api_keys (key, plan, daily_limit) VALUES (?, ?, ?)",
            (new_key, plan, daily_limit),
        )

    return {
        "api_key": new_key,
        "plan": plan,
        "daily_limit": daily_limit,
    }
    
#lista chaves p admin
@app.get(
    "/me/keys",
    tags=["Admin"],
    summary="Lista API keys cadastradas (admin)",
)
def list_keys(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Chave de admin inválida")

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT key, plan, daily_limit FROM api_keys ORDER BY rowid DESC"
        ).fetchall()

    # mascara a chave pra não vazar tudo no /docs
    def mask(k: str) -> str:
        return f"{k[:6]}...{k[-6:]}" if k and len(k) > 12 else "****"

    return {
        "total": len(rows),
        "keys": [
            {
                "key": mask(r["key"]),
                "plan": r["plan"],
                "daily_limit": int(r["daily_limit"]),
            }
            for r in rows
        ],
    }
    
#deleta chave p admin

@app.delete("/admin/delete-key", tags=["Admin"], summary="Deleta (revoga) uma API Key por prefixo (admin)")
def delete_key(
    key_prefix: str,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Chave de admin inválida")

    full_key = resolve_key_by_prefix(key_prefix)

    with get_conn() as conn:
        conn.execute("DELETE FROM api_keys WHERE key = ?", (full_key,))
        conn.execute("DELETE FROM usage_daily WHERE key = ?", (full_key,))

    return {"deleted": True, "key_prefix": key_prefix}

#update limite diario p admin

@app.patch("/admin/update-limit", tags=["Admin"], summary="Atualiza plano e limite diário por prefixo (admin)")
def update_limit(
    key_prefix: str,
    plan: str | None = None,
    daily_limit: int | None = None,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Chave de admin inválida")

    if plan is None and daily_limit is None:
        raise HTTPException(status_code=400, detail="Envie plan e/ou daily_limit")

    if daily_limit is not None and daily_limit <= 0:
        raise HTTPException(status_code=400, detail="daily_limit deve ser > 0")

    full_key = resolve_key_by_prefix(key_prefix)

    with get_conn() as conn:
        row = conn.execute(
            "SELECT plan, daily_limit FROM api_keys WHERE key = ?",
            (full_key,),
        ).fetchone()

        new_plan = plan if plan is not None else row["plan"]
        new_limit = daily_limit if daily_limit is not None else int(row["daily_limit"])

        conn.execute(
            "UPDATE api_keys SET plan = ?, daily_limit = ? WHERE key = ?",
            (new_plan, new_limit, full_key),
        )

    return {
        "updated": True,
        "key_prefix": key_prefix,
        "plan": new_plan,
        "daily_limit": new_limit,
    }

# conta / uso

@app.get(
    "/me/usage",
    tags=["Account"],
    summary="Mostra uso e limite do dia (requer API key)",
)
def me_usage(api_key: str = Depends(require_api_key)):
    today = date.today().isoformat()

    with get_conn() as conn:
        key_row = conn.execute(
            "SELECT plan, daily_limit FROM api_keys WHERE key = ?",
            (api_key,),
        ).fetchone()

        usage_row = conn.execute(
            "SELECT count FROM usage_daily WHERE key = ? AND day = ?",
            (api_key, today),
        ).fetchone()

    used = int(usage_row["count"]) if usage_row else 0
    limit = int(key_row["daily_limit"]) if key_row else 0

    return {
        "plan": key_row["plan"] if key_row else "unknown",
        "day": today,
        "used": used,
        "daily_limit": limit,
        "remaining": max(limit - used, 0),
    }


# rotas protegidas e de validação

@app.get(
    "/validate/cpf",
    response_model=ValidationResponse,
    tags=["Validation"],
    summary="Valida um CPF (requer API key)",
)
def validate_cpf(number: str, api_key: str = Depends(require_api_key)) -> ValidationResponse:
    valid = validar_cpf(number)
    return ValidationResponse(
        type="CPF",
        input=number,
        formatted=formato_cpf(number),
        valid=valid,
        message="CPF válido" if valid else "CPF inválido",
    )


@app.get(
    "/validate/cnpj",
    response_model=ValidationResponse,
    tags=["Validation"],
    summary="Valida um CNPJ (requer API key)",
)
def validate_cnpj(number: str, api_key: str = Depends(require_api_key)) -> ValidationResponse:
    valid = validar_cnpj(number)
    return ValidationResponse(
        type="CNPJ",
        input=number,
        formatted=formato_cnpj(number),
        valid=valid,
        message="CNPJ válido" if valid else "CNPJ inválido",
    )


@app.get(
    "/validate/document",
    response_model=ValidationResponse,
    tags=["Validation"],
    summary="Valida CPF ou CNPJ automaticamente (requer API key)",
)
def validate_document(number: str, api_key: str = Depends(require_api_key)) -> ValidationResponse:
    return ValidationResponse(**validar_documento(number))
