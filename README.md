# 🔐 API de Validação de CPF e CNPJ

> Uma API simples, direta e **do mundo real**, feita pra validar CPF e CNPJ com segurança, controle de uso e mentalidade de produto.

Essa API não nasceu pra ser só um exercício. Ela foi pensada como **base de um SaaS**, com autenticação por API Key, limite diário, painel admin e tudo organizado do jeito certo.

---

## 🚀 O que essa API faz

* ✅ Valida **CPF**
* ✅ Valida **CNPJ**
* ✅ Detecta automaticamente se é CPF ou CNPJ
* 🔐 Protege endpoints com **API Key**
* 📊 Controla **uso diário por chave**
* 👮 Tem endpoints **admin** pra gerenciar chaves

Tudo isso com FastAPI, SQLite e boas práticas.

---

## 🧠 Por que esse projeto existe?

Porque muita gente aprende API só com CRUD genérico.
Aqui a ideia foi diferente:

> **pensar como produto**, não só como código.

Esse projeto simula uma API que poderia ser usada por:

* sistemas financeiros
* ERPs
* cadastros
* bots
* qualquer lugar que precise validar documento brasileiro

---

## 🧱 Tecnologias usadas

* **Python 3.11+**
* **FastAPI**
* **SQLite** (simples e suficiente pro caso)
* **Pydantic** (contratos de resposta)
* **Pytest** (testes)

---

## 📁 Estrutura do projeto

```text
.
├── core/
│   ├── auth.py        # autenticação por API Key + limite diário
│   ├── db.py          # banco de dados e schema
│   └── __init__.py
│
├── validators/
│   ├── cpf.py         # regras de CPF
│   ├── cnpj.py        # regras de CNPJ
│   └── document.py   # detecta CPF ou CNPJ
│
├── models/
│   └── validation_response.py  # modelo de resposta da API
│
├── main.py            # aplicação FastAPI
├── database.db        # banco SQLite
├── .env               # variáveis de ambiente (não versionar)
└── README.md
```

---

## 🔐 Autenticação (API Key)

Essa API **não funciona aberta**.
Tudo que valida documento exige uma **API Key**.

### Como funciona

* Um **admin** cria uma API Key
* A key tem:

  * plano (`free`, `pro`, etc)
  * limite diário
* Cada request conta no uso diário

---

## 👮 Endpoints de Admin

### Criar uma API Key

`POST /admin/create-key`

Header:

```
X-Admin-Key: SUA_CHAVE_DE_ADMIN
```

Resposta:

```json
{
  "api_key": "chave-gerada-aqui",
  "plan": "free",
  "daily_limit": 100
}
```

> ⚠️ Guarde essa key. Ela só aparece uma vez.

---

### Listar API Keys (mascaradas)

`GET /me/keys`

Mostra todas as chaves, mas **sem vazar tudo**:

```
AB12CD...9X8Y
```

---

### Atualizar plano ou limite

`PATCH /admin/update-limit`

Parâmetros:

* `key_prefix` (início da key)
* `plan`
* `daily_limit`

---

### Deletar (revogar) uma key

`DELETE /admin/delete-key`

Parâmetro:

* `key_prefix`

A key deixa de funcionar na hora.

---

## 📊 Conta / Uso

### Ver uso diário

`GET /me/usage`

Header:

```
X-API-Key: SUA_API_KEY
```

Resposta:

```json
{
  "plan": "free",
  "day": "2026-01-29",
  "used": 3,
  "daily_limit": 100,
  "remaining": 97
}
```

---

## ✅ Validação de documentos

### CPF

`GET /validate/cpf?number=12345678909`

### CNPJ

`GET /validate/cnpj?number=11222333000181`

### Automático

`GET /validate/document?number=...`

Resposta padrão:

```json
{
  "type": "CPF",
  "input": "12345678909",
  "formatted": "123.456.789-09",
  "valid": true,
  "message": "CPF válido"
}
```

---

## 🧪 Testes

Os testes são feitos com **pytest**.

Instalação:

```bash
pip install pytest
```

Rodar testes:

```bash
pytest
```

---

## ▶️ Como rodar o projeto

1. Clone o repositório
2. Crie o `.env`

```env
ADMIN_KEY=sua-chave-de-admin
```

3. Ative a venv
4. Rode:

```bash
uvicorn main:app --reload
```

5. Acesse:

```
http://127.0.0.1:8000/docs
```

---

## 🛣️ Próximos passos (roadmap)

* [ ] Hash de API keys no banco
* [ ] Rate limit por minuto
* [ ] Logs estruturados
* [ ] Deploy público
* [ ] Versionamento da API (`/v1`)

---

## 🧠 Filosofia do projeto

Código limpo.
Sem firula.
Pensado pra funcionar no mundo real.

> Feito por alguém que tá aprendendo, mas aprendendo **do jeito certo**.

---

## 🖤 Autoria

Feito por **Mali**.

Backend, API, mundo real e pé no chão.
