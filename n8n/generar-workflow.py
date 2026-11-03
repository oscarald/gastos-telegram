"""Genera n8n/workflows/telegram-gasto.json a partir de los codigos JS sueltos."""

from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
N8N_DIR = BASE / "n8n"

interpretar = (N8N_DIR / "codigo-interpretar-mensaje.js").read_text(encoding="utf-8")
confirmacion = (N8N_DIR / "codigo-preparar-confirmacion.js").read_text(encoding="utf-8")
error = (N8N_DIR / "codigo-preparar-error.js").read_text(encoding="utf-8")

workflow = {
    "name": "Telegram - Registrar gasto",
    "nodes": [
        {
            "parameters": {
                "updates": ["message"],
                "additionalFields": {},
            },
            "id": "a1000000-0000-4000-8000-000000000001",
            "name": "Telegram Trigger",
            "type": "n8n-nodes-base.telegramTrigger",
            "typeVersion": 1.1,
            "position": [-360, 0],
            "webhookId": "gastos-telegram-trigger",
        },
        {
            "parameters": {"jsCode": interpretar},
            "id": "a1000000-0000-4000-8000-000000000002",
            "name": "Interpretar mensaje",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [-120, 0],
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "version": 2},
                    "conditions": [
                        {
                            "id": "cond-ok",
                            "leftValue": "={{ $json.ok }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                        }
                    ],
                    "combinator": "and",
                },
                "options": {},
            },
            "id": "a1000000-0000-4000-8000-000000000003",
            "name": "Es gasto valido",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [120, 0],
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://backend:8000/api/v1/gastos/telegram",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "X-API-Key",
                            "value": "change-me-n8n-api-key",
                        }
                    ]
                },
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": (
                    "={{ JSON.stringify({"
                    " monto: $json.monto,"
                    " descripcion: $json.descripcion,"
                    " fecha: $json.fecha,"
                    " metodo_pago: $json.metodo_pago,"
                    " identificador_externo: 'telegram_' + $json.chatId + '_' + $json.messageId"
                    " }) }}"
                ),
                "options": {"timeout": 20000},
            },
            "id": "a1000000-0000-4000-8000-000000000004",
            "name": "Registrar gasto",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [380, -120],
            "onError": "continueRegularOutput",
        },
        {
            "parameters": {"jsCode": confirmacion},
            "id": "a1000000-0000-4000-8000-000000000005",
            "name": "Preparar confirmacion",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [640, -120],
        },
        {
            "parameters": {
                "resource": "message",
                "operation": "sendMessage",
                "chatId": "={{ $json.chatId }}",
                "text": "={{ $json.texto }}",
                "additionalFields": {},
            },
            "id": "a1000000-0000-4000-8000-000000000006",
            "name": "Responder",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [900, -120],
        },
        {
            "parameters": {"jsCode": error},
            "id": "a1000000-0000-4000-8000-000000000007",
            "name": "Preparar error",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [380, 140],
        },
        {
            "parameters": {
                "resource": "message",
                "operation": "sendMessage",
                "chatId": "={{ $json.chatId }}",
                "text": "={{ $json.texto }}",
                "additionalFields": {},
            },
            "id": "a1000000-0000-4000-8000-000000000008",
            "name": "Responder error",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [640, 140],
        },
    ],
    "connections": {
        "Telegram Trigger": {
            "main": [[{"node": "Interpretar mensaje", "type": "main", "index": 0}]]
        },
        "Interpretar mensaje": {
            "main": [[{"node": "Es gasto valido", "type": "main", "index": 0}]]
        },
        "Es gasto valido": {
            "main": [
                [{"node": "Registrar gasto", "type": "main", "index": 0}],
                [{"node": "Preparar error", "type": "main", "index": 0}],
            ]
        },
        "Registrar gasto": {
            "main": [[{"node": "Preparar confirmacion", "type": "main", "index": 0}]]
        },
        "Preparar confirmacion": {
            "main": [[{"node": "Responder", "type": "main", "index": 0}]]
        },
        "Preparar error": {
            "main": [[{"node": "Responder error", "type": "main", "index": 0}]]
        },
    },
    "settings": {"executionOrder": "v1"},
    "pinData": {},
    "active": False,
    "versionId": "7f3c1d2a-0b6e-4c91-9d0e-2b7a5c8f4e10",
    "meta": {"instanceId": "control-gastos"},
    "tags": [],
}

destino = N8N_DIR / "workflows" / "telegram-gasto.json"
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Workflow generado: {destino}")
