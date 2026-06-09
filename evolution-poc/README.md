# Evolution POC

POC minimo em Python para usar a Evolution API local e enviar mensagens em lote com Celery.

## Subir tudo

```bash
docker compose up -d --build
```

A API HTTP do POC fica em:

```text
http://localhost:8000/docs
```

## Rotas do POC

- `GET /health`
- `POST /instances`
- `POST /instances/qrcode`
- `POST /messages/text`
- `POST /messages/bulk`

## Criar instancia e gerar QR Code

```bash
docker compose run --rm worker-celery python -m app.cli create --instance main
docker compose run --rm worker-celery python -m app.cli qr --instance main --output /workspace/qrcode.png
```

Ou por HTTP:

```bash
curl -X POST http://localhost:8000/instances \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","qrcode":true}'

curl -X POST http://localhost:8000/instances/qrcode \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","output_path":"/workspace/qrcode.png"}'
```

## Enviar uma mensagem

```bash
docker compose run --rm worker-celery python -m app.cli send --instance main --number 5585999999999 --text "Teste"
```

Ou por HTTP:

```bash
curl -X POST http://localhost:8000/messages/text \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","number":"5585999999999","text":"Teste"}'
```

## Enviar em lote via Celery

Com o worker rodando pelo `docker compose up -d --build`:

```bash
docker compose run --rm worker-celery python -m app.cli bulk --instance main --numbers 5585999999999,5585888888888 --text "Teste em lote" --delay 3
```

Cada destinatario vira uma task Celery independente, com retry e limite de duracao. O lote apenas agenda as tasks e retorna os `task_ids`.

Ou por HTTP:

```bash
curl -X POST http://localhost:8000/messages/bulk \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","recipients":["5585999999999","5585888888888"],"message":"Teste em lote","delay_seconds":3}'
```

Resposta esperada:

```json
{
  "instance": "main",
  "total": 2,
  "delay_seconds": 3,
  "task_ids": [
    "id-da-primeira-task",
    "id-da-segunda-task"
  ]
}
```

Os logs estruturados aparecem no worker:

```bash
docker logs -f evolution-celery-worker
```
