# Flask

## Flask — Cérebro

### 1. Criar Cientista

```
Route = /api/criar/cientista
HTTP = PUT
Request Body:
    {
        "nome": "string",
        "email": "string"
    }
Response 200:
    {
        "status": "sucesso",
        "cientista_id": 7,
        "_links": {
            "self": "/api/criar/cientista",
            "criar_agendamento": "/api/criar/agendamento"
        }
    }
```

### 2. Criar Agendamento

```
Route = /api/criar/agendamento
HTTP = POST
Request Body:
    {
        "cientista_id": 7,
        "horario_inicio_utc": "2025-12-01T03:00:00Z"
    }
Responses:
    200 OK → {
        "status": "agendamento_criado", "agendamento_id": 123,
        "_links": {
            "self": "/api/criar/agendamento", "detalhes": "/api/agendamento/123"
        }
    }

    409 Conflict → {
        "status": "falha", 
        "motivo": "horário_ocupado", 
        "_links": {
            "tentar_novamente": "/api/criar/agendamento"
        }
    }

```
### 3. Obter Tempo Sincronizado

```
Route: /api/time
HTTP: GET
Response 200:
    {
    "server_time_utc": "2025-10-26T18:00:05.123Z",
        "_links": {
            "self": "/api/time",
            "criar_agendamento": "/api/criar/agendamento"
        }
    }
```


## Node.js — Porteiro

### 1. Solicitar Lock de Recurso

```
Route: /api/request/agendamento
HTTP: POST
Request Body:
    {
        "resource_id": "Hubble-Acad_20  25-12-01T03:00:00Z"
    }
Responses:
    200 OK → {
        "status": "lock_concedido", 
        "_links": {"unlock": "/api/release/agendamento"}}

    409 Conflict → {"status": "recurso_ocupado", "_links": {"self": "/api/request/agendamento"}}
```

### 2. Liberar Recurso

Route: /api/release/agendamento
HTTP: POST
Request Body:
{
"resource_id": "Hubble-Acad_2025-12-01T03:00:00Z"
}
Response 200:
{
"status": "lock_liberado",
"_links": {
"self": "/api/release/agendamento",
"request_lock": "/api/request/agendamento"
}
}