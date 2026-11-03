# Control de Gastos Personales — Self Hosted

Aplicación web para registrar y analizar gastos personales. Los gastos se registran
escribiendo mensajes en un bot de **Telegram** (el procesamiento lo hace **n8n**), y se
consultan desde un **dashboard web** con gráficos, filtros, exportación a CSV y
administración de categorías y reglas.

Todo funciona dentro de la red local: **Docker Compose** levanta PostgreSQL, la API
FastAPI y el frontend (SPA servida por nginx). No depende de servicios externos.

```
Telegram ──► n8n (parseo) ──► POST /api/v1/gastos/telegram ──► FastAPI ──► PostgreSQL
                                      │                                │
                                      └──── respuesta con categoría ──┘
                                                       │
                                                       ▼
                                        Dashboard React (nginx) ──► /api/v1/*
```

---

## 1. Puesta en marcha

Requisitos: Docker y Docker Compose.

```bash
cd gastos
cp .env.example .env          # ajusta POSTGRES_PASSWORD y N8N_API_KEY
docker compose up -d --build
```

| Servicio | URL | Notas |
|---|---|---|
| Dashboard web | http://localhost:8080 | Puerto configurable con `FRONTEND_PORT` |
| API REST | http://localhost:8000/api/v1 | |
| Documentación Swagger | http://localhost:8080/docs (o :8000/docs) | OpenAPI en `/openapi.json` |
| PostgreSQL | red interna `gastos` | **No** se publica ningún puerto al host |

El arranque del backend ejecuta automáticamente:

1. `alembic upgrade head` (crea/actualiza el esquema),
2. `python -m app.db.seed` (categorías y reglas iniciales, **idempotente**),
3. `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

Comandos útiles:

```bash
docker compose ps           # estado y healthchecks
docker compose logs -f backend
docker compose down         # detener (conserva el volumen)
docker compose down -v      # detener y BORRAR los datos
```

---

## 2. Variables de entorno

Todas se definen en `.env` (ver `.env.example`).

| Variable | Por defecto | Descripción |
|---|---|---|
| `APP_TIMEZONE` | `America/La_Paz` | Zona horaria de referencia para los límites de mes/día |
| `DEFAULT_CURRENCY` | `BOB` | Moneda por defecto de los gastos |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `gastos` | Credenciales de PostgreSQL |
| `DATABASE_URL` | `postgresql+asyncpg://gastos:***@db:5432/gastos` | URL de conexión (host `db` dentro de Compose) |
| `N8N_API_KEY` | `change-me-...` | **API Key** que n8n envía en `X-API-Key` |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` | Orígenes permitidos (solo necesario en desarrollo) |
| `BACKEND_PORT` / `FRONTEND_PORT` | `8000` / `8080` | Puertos publicados en el host |
| `LOG_LEVEL` | `INFO` | Nivel de log del backend |

> La API Key se valida en modo **fail-closed**: si `N8N_API_KEY` está vacía, el endpoint
> de Telegram responde `503` en lugar de quedar abierto.

---

## 3. API REST

Prefijo: `/api/v1`. Todas las respuestas de escritura usan el envelope
`{"success": true, "message": "...", "data": {...}}`; los errores devuelven
`{"success": false, "message": "..."}` con el código HTTP correspondiente.

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado de la app y de la conexión con PostgreSQL |
| `POST` | `/gastos/telegram` | **Protegido con `X-API-Key`.** Registro desde Telegram |
| `GET` | `/gastos` | Listado con filtros y paginación |
| `GET` | `/gastos/{id}` | Obtener un gasto |
| `POST` | `/gastos` | Registro manual (origen `web`) |
| `PUT` | `/gastos/{id}` | Modificar un gasto (actualización parcial) |
| `DELETE` | `/gastos/{id}` | Eliminar un gasto |
| `GET` | `/gastos/export/csv` | Exportación CSV respetando los filtros |
| `GET` | `/categorias` | Listar categorías (con nº de gastos) |
| `POST` | `/categorias` | Crear categoría |
| `PUT` | `/categorias/{id}` | Editar / activar / desactivar |
| `DELETE` | `/categorias/{id}` | Eliminar (requiere `?reemplazar_por=` si tiene gastos o reglas) |
| `GET` | `/reglas` | Listar reglas |
| `POST` | `/reglas` | Crear regla |
| `PUT` | `/reglas/{id}` | Editar / activar / desactivar |
| `DELETE` | `/reglas/{id}` | Eliminar regla |
| `GET` | `/dashboard/resumen` | Métricas del dashboard |
| `GET` | `/metodos-pago` | Métodos de pago configurados |

### 3.1 Parámetros de `GET /gastos`

| Parámetro | Ejemplo | Descripción |
|---|---|---|
| `mes` + `anio` | `?mes=11&anio=2026` | Filtra por mes local (La Paz) |
| `fecha_desde` / `fecha_hasta` | `?fecha_desde=2026-11-01` | Rango de fechas (ISO; el día final es inclusivo) |
| `categoria_id` | `?categoria_id=1` | Categoría concreta |
| `metodo_pago` | `?metodo_pago=Efectivo` | Método de pago |
| `origen` | `?origen=telegram` | `telegram` o `web` |
| `q` | `?q=almuerzo` | Búsqueda parcial en la descripción |
| `orden` | `?orden=monto_desc` | `fecha_asc`, `fecha_desc`, `monto_asc`, `monto_desc`, `categoria_asc` |
| `pagina` / `limite` | `?pagina=1&limite=50` | Paginación (máx. 200 por página) |

### 3.2 Ejemplos de peticiones

Registro desde Telegram (lo que hace n8n):

```bash
curl -X POST http://localhost:8000/api/v1/gastos/telegram \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me-n8n-api-key" \
  -d '{
        "monto": 50.00,
        "descripcion": "Almuerzo en restaurante",
        "fecha": null,
        "metodo_pago": "Efectivo",
        "identificador_externo": "telegram_123456"
      }'
```

```json
{
  "success": true,
  "message": "Gasto registrado correctamente",
  "duplicate": false,
  "data": {
    "id": 15,
    "monto": 50.0,
    "moneda": "BOB",
    "descripcion": "Almuerzo en restaurante",
    "categoria": "Alimentación",
    "metodo_pago": "Efectivo",
    "origen": "telegram",
    "fecha": "2026-11-02T12:30:00-04:00"
  }
}
```

Si el mismo `identificador_externo` llega otra vez, la API responde **HTTP 200** con
`"duplicate": true` y los datos del gasto original (no se crea un registro nuevo):

```json
{
  "success": true,
  "message": "El gasto ya estaba registrado (duplicado)",
  "duplicate": true,
  "data": { "id": 15, "...": "..." }
}
```

Registro manual y filtros:

```bash
curl -X POST http://localhost:8000/api/v1/gastos \
  -H "Content-Type: application/json" \
  -d '{"monto": "120.50", "descripcion": "Supermercado del mes", "metodo_pago": "Tarjeta de crédito"}'

curl "http://localhost:8000/api/v1/gastos?mes=11&anio=2026&categoria_id=1&q=almuerzo&pagina=1&limite=20"

curl "http://localhost:8000/api/v1/dashboard/resumen?anio=2026&mes=11"

curl -o gastos.csv "http://localhost:8000/api/v1/gastos/export/csv?mes=11&anio=2026"
```

### 3.3 Reglas de negocio

- **Monto**: mayor que cero, máximo 12 dígitos y 2 decimales (`Numeric(12,2)` + `Decimal`).
- **Descripción**: obligatoria, 1–255 caracteres.
- **Fecha**: opcional. Si no se envía se usa la fecha/hora actual de La Paz. Sin zona
  horaria explícita se interpreta en `APP_TIMEZONE`.
- **Origen**: `telegram` (fijo en el endpoint de integración) o `web`.
- **Duplicados**: índice único parcial sobre `identificador_externo` (no nulo) + control
  previo en la capa de servicio, dentro de la misma transacción.
- **Categorías**: no se puede eliminar una categoría con gastos o reglas asociados
  (`409`); hay que reasignarlos con `?reemplazar_por=<id>`.

---

## 4. Motor de categorización

Vive aislado en `backend/app/services/categorization_service.py` para poder mejorarlo
sin tocar los controladores HTTP. Funcionamiento:

1. **Normalización**: NFKD → eliminación de acentos → minúsculas → espacios colapsados.
   `"Almuerzo con Ñoño"` → `almuerzo con nono`.
2. **Coincidencia por palabra completa**: regex `(?<!\w)clave(?!\w)` sobre el texto
   normalizado. Así `"almuerzo"` **no** coincide con `"almuerzos"` ni con `"xalmuerzo"`.
3. **Prioridad**: se gana la regla con mayor `prioridad`; a igualdad, la palabra clave
   más larga (la más específica) y, si sigue el empate, la de menor `id`.
4. **Reglas ignoradas**: las desactivadas y las que apuntan a una categoría inactiva.
5. **Sin coincidencias**: se asigna la categoría **"Sin Categorizar"** (se crea o se
   reactiva automáticamente si no existe).

Ejemplos: `"Almuerzo en restaurante"` → Alimentación · `"pase en micros"` → Sin Categorizar
(no coincide con la regla `pasaje`) · `"Supermercado"` → Alimentación.

---

## 5. Integración con n8n (Telegram)

El backend **no** habla con Telegram: solo expone la API REST. El flujo es:

```
Telegram Trigger → Interpretar mensaje → (¿válido?) → POST /api/v1/gastos/telegram → Responder
                                                     └→ (no) → Responder error
```

### 5.1 Importar el flujo

1. Abre n8n → **Workflows → Import from File** → `n8n/workflows/telegram-gasto.json`.
2. Edita el nodo **Registrar gasto**:
   - URL: `http://backend:8000/api/v1/gastos/telegram` (si n8n corre en otro host:
     `http://<IP-del-servidor>:8000/api/v1/gastos/telegram`).
   - Cabecera `X-API-Key`: el mismo valor que `N8N_API_KEY` del `.env`.
3. Edita el nodo **Telegram Trigger** y selecciona tu bot (credencial de Telegram).
4. Activa el workflow (botón *Active*) y comprueba que Telegram Trigger registre el webhook.

El código de los nodos *Code* está en `n8n/codigo-*.js` por si prefieres pegarlo a mano
(el JSON del workflow se regenera con `python n8n/generar-workflow.py`).

### 5.2 Qué interpreta el flujo

| Ejemplo de mensaje | Monto | Descripción | Fecha | Método de pago |
|---|---|---|---|---|
| `almuerzo 50 bs` | 50 | almuerzo | hoy | — |
| `gasté 25,50 en supermercado con tarjeta de crédito` | 25.50 | … | — | Tarjeta de crédito |
| `pasaje 10 efectivo` | 10 | … | — | Efectivo |
| `desayuno 8.5 qr` | 8.5 | … | — | QR |
| `internet 120 por transferencia` | 120 | … | — | Transferencia |
| `almuerzo 50 bs 05/10` | 50 | … | 05/10 del año actual | — |
| `cafe 5 ayer` | 5 | … | ayer | — |

Si no hay monto (o es `<= 0`), el bot responde `⚠️ No pude registrar el gasto: …` y no
se llama a la API.

### 5.3 Pruebas manuales de la integración

```bash
# 1. Sin API Key -> 401
curl -i -X POST http://localhost:8000/api/v1/gastos/telegram \
  -H "Content-Type: application/json" \
  -d '{"monto": 50, "descripcion": "Almuerzo"}'

# 2. Con API Key -> 200 y categoría asignada
curl -X POST http://localhost:8000/api/v1/gastos/telegram \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $N8N_API_KEY" \
  -d '{"monto": 50, "descripcion": "Almuerzo en restaurante", "identificador_externo": "telegram_123456"}'

# 3. Repetir -> duplicate: true y no se crea otro gasto
```

En el dashboard, el gasto aparece en **Gastos** con origen `telegram`.

---

## 6. Dashboard web

- **Resumen**: total gastado del mes, nº de transacciones, promedio por transacción y
  categoría con mayor gasto.
- **Gráficos** (Chart.js): donut de distribución por categoría (con los colores de cada
  categoría), barras de gasto diario y comparativa mes actual vs. mes anterior.
- **Historial**: tabla responsive (tarjetas en móvil), filtros por mes/año/categoría/método
  de pago, búsqueda por descripción, paginación, editar y eliminar.
- **Formulario**: monto, descripción, categoría (manual o automática por reglas), fecha y
  método de pago.
- **Categorías**: alta/edición, color, activar/desactivar, nº de gastos y borrado con
  reasignación.
- **Reglas**: alta/edición de palabra clave, categoría destino, prioridad, activar/desactivar
  y borrado.

---

## 7. Datos iniciales (seeds)

Se aplican en cada arranque y son **idempotentes** (no duplican nada).

| Categoría | Color | Reglas iniciales |
|---|---|---|
| Alimentación | `#F59E0B` | `almuerzo`, `desayuno`, `supermercado` |
| Transporte | `#3B82F6` | `pasaje`, `gasolina` |
| Servicios | `#8B5CF6` | `internet`, `electricidad` |
| Entretenimiento | `#EC4899` | |
| Compras | `#14B8A6` | |
| Salud | `#EF4444` | |
| Sin Categorizar | `#6B7280` | |

---

## 8. Pruebas

Las pruebas de integración usan PostgreSQL real (para validar `Numeric`, `TIMESTAMPTZ`,
índices y claves foráneas).

```bash
# 1. Tests unitarios (no necesitan base de datos)
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/unit -q

# 2. Levantar la base de datos de pruebas (puerto 5433) y ejecutar la suite completa
cd ..
docker compose -f docker-compose.test.yml up -d
cd backend
python -m pytest tests -q

# 3. Lint
ruff check .
```

Cobertura actual: **88 pruebas** (38 unitarias del motor de categorización, zona horaria y
validaciones; 50 de integración sobre la API: registro por Telegram, duplicados, validación
de montos, edición/borrado, filtros, CRUD de categorías y reglas, cálculos del dashboard,
exportación CSV e idempotencia de los seeds).

---

## 9. Desarrollo local (sin Docker)

```bash
# Backend
cd backend
python -m venv .venv && . .venv/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
$env:DATABASE_URL = "postgresql+asyncpg://gastos:gastos@localhost:5432/gastos"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev        # http://localhost:5173, con proxy /api -> localhost:8000
```

Scripts disponibles en el frontend: `npm run dev`, `npm run build`, `npm run typecheck`,
`npm run lint`.

---

## 10. Copias de seguridad y restauración

```bash
# Copia (desde el host)
docker compose exec -T db pg_dump -U gastos -d gastos -Fc > gastos_$(date +%F).dump

# Restaurar
docker compose exec -T db pg_dropdb -U postgres --if-exists gastos
docker compose exec -T db pg_restore -U gastos -d gastos --no-owner < gastos_2026-11-02.dump
```

También puedes copiar el volumen mientras la base está detenida:

```bash
docker compose down
docker run --rm -v control-gastos_postgres_data:/datos -v ${PWD}:/respaldo alpine \
  tar czf /respaldo/gastos-postgres.tar.gz -C /datos .
docker compose up -d
```

---

## 11. Estructura del proyecto

```
gastos/
├── backend/
│   ├── alembic/                 migración 0001_initial
│   ├── app/
│   │   ├── api/v1/              routers (gastos, categorias, reglas, dashboard, salud)
│   │   ├── core/                configuración, seguridad, zona horaria, errores
│   │   ├── db/                  motor, sesión, seeds
│   │   ├── models/              modelos SQLAlchemy
│   │   ├── repositories/        acceso a datos
│   │   ├── schemas/             esquemas Pydantic
│   │   ├── services/            lógica de negocio (incl. motor de categorización)
│   │   └── main.py
│   ├── tests/                   pytest (unit + integration)
│   └── Dockerfile
├── frontend/
│   ├── src/components/          UI, gráficos, formularios
│   ├── src/hooks/  src/layouts/  src/pages/  src/services/  src/types/
│   ├── nginx.conf               SPA + proxy /api
│   └── Dockerfile
├── n8n/
│   ├── workflows/telegram-gasto.json   flujo importable
│   ├── codigo-*.js                     código de los nodos Code
│   └── generar-workflow.py             regenera el JSON
├── docker-compose.yml
├── docker-compose.test.yml
└── .env.example
```

---

## 12. Decisiones técnicas

| Decisión | Motivo |
|---|---|
| SQLAlchemy 2.0 **async** + asyncpg | La API es I/O-bound; coherente con el resto de proyectos del entorno |
| `Numeric(12,2)` + `Decimal` en Python | Los importes no pierden precisión; el JSON se serializa como número |
| `TIMESTAMPTZ` + límites calculados en La Paz | Un mes local no coincide con un mes UTC (offset −04:00) |
| Índice único **parcial** en `identificador_externo` | Idempotencia real garantizada por la base de datos |
| nginx sirve la SPA y hace proxy de `/api` | Una sola URL, sin CORS en producción y con fallback de SPA |
| Motor de categorización aislado en un servicio | Se puede evolucionar (sinónimos, fuzzy, ML) sin tocar la API |
| Envoltura `{success, message, data}` | Respuesta uniforme y fácil de consumir desde n8n y el frontend |
| Solo el endpoint de Telegram exige API Key | La app es local; el diseño deja un punto de extensión para autenticar todo |
| Sin usuarios ni roles (por ahora) | Requisito del proyecto; la separación routers/servicios permite añadirlo después |

### Preparado para presupuestos

El modelo ya está preparado: los gastos tienen `categoria_id` y `moneda`, y las métricas se
calculan por categoría y por mes. Añadir `presupuestos` (global y por categoría) solo
requiere una tabla nueva, un servicio y un endpoint; el dashboard puede consumirlo como
hizo con `/dashboard/resumen`, sin romper lo existente.
