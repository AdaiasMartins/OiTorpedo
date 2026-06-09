# OiTorpedo

POC para usar a Evolution API localmente e enviar mensagens pelo WhatsApp, incluindo envio individual e envio em lote com Celery.

Este repositorio sobe uma stack completa com Docker:

- Evolution API, a API que conversa com o WhatsApp.
- PostgreSQL, usado pela Evolution API para persistir dados.
- Redis, usado pela Evolution API e tambem como fila do Celery.
- API Python da POC, feita com FastAPI.
- Worker Celery, responsavel por processar envios em lote.

## Requisitos

- Docker 24+
- Docker Compose v2+

## Estrutura do Projeto

```text
.
|-- docker-compose.yml
|-- .env
|-- .env-example
|-- README.md
`-- evolution-poc/
    |-- Dockerfile
    |-- README.md
    |-- requirements.txt
    `-- app/
        |-- api.py
        |-- celery_app.py
        |-- cli.py
        |-- config.py
        |-- evolution_client.py
        `-- tasks.py
```

## Servicos

| Servico | Para que serve | URL/porta |
|---|---|---|
| `evolution-api` | API principal do WhatsApp | `http://localhost:8080` |
| `poc-api` | API Python da POC | `http://localhost:8000/docs` |
| `worker-celery` | Envio em lote em segundo plano | sem porta HTTP |
| `postgres` | Banco da Evolution API | host `localhost:5433`, container `postgres:5432` |
| `redis` | Cache/fila | `localhost:6379` |

## Configuracao Inicial

O projeto usa o arquivo `.env` na raiz. Se ele ainda nao existir, crie a partir do exemplo:

```bash
cp .env-example .env
```

Antes de subir em qualquer ambiente que nao seja apenas local, troque pelo menos estas variaveis:

```env
AUTHENTICATION_API_KEY=troque-por-uma-chave-segura
AUTHENTICATION_JWT_SECRET=troque-por-um-segredo-seguro
```

Voce pode gerar valores seguros assim:

```bash
openssl rand -hex 32
```

Variaveis mais importantes para uso local:

| Variavel | Exemplo | Uso |
|---|---|---|
| `SERVER_URL` | `http://localhost:8080` | URL publica da Evolution API |
| `AUTHENTICATION_API_KEY` | `...` | Chave usada no header `apikey` |
| `AUTHENTICATION_JWT_SECRET` | `...` | Segredo de JWT da Evolution API |
| `DATABASE_CONNECTION_URI` | `postgresql://evolution:evolution@postgres:5432/evolution` | Conexao interna com PostgreSQL |
| `CONFIG_SESSION_PHONE_VERSION` | vazio | Deve ficar vazio para evitar problemas ao gerar QR Code |

Importante: dentro do Docker, o PostgreSQL deve usar a porta interna `5432`, nao a porta `5433` exposta no host.

## Subir o Projeto

Na raiz do projeto:

```bash
docker compose up -d --build
```

Verifique se os containers subiram:

```bash
docker compose ps
```

A documentacao interativa da POC fica em:

```text
http://localhost:8000/docs
```

A Evolution API fica em:

```text
http://localhost:8080
```

## Fluxo Basico de Uso

### 1. Criar uma instancia

Uma instancia representa uma sessao do WhatsApp. O exemplo abaixo cria uma instancia chamada `main`.

Via API HTTP da POC:

```bash
curl -X POST http://localhost:8000/instances \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","qrcode":true}'
```

Via CLI:

```bash
docker compose run --rm worker-celery \
  python -m app.cli create --instance main
```

### 2. Gerar o QR Code

Via API HTTP da POC:

```bash
curl -X POST http://localhost:8000/instances/qrcode \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","output_path":"/workspace/qrcode.png"}'
```

Via CLI:

```bash
docker compose run --rm worker-celery \
  python -m app.cli qr --instance main --output /workspace/qrcode.png
```

O arquivo sera salvo em:

```text
qrcode.png
```

Depois disso, abra a imagem e escaneie pelo WhatsApp em `Aparelhos conectados`.

### 3. Enviar uma mensagem individual

Use numeros com codigo do pais e DDD. Exemplo para Brasil:

```text
5585999999999
```

Via API HTTP da POC:

```bash
curl -X POST http://localhost:8000/messages/text \
  -H 'Content-Type: application/json' \
  -d '{"instance":"main","number":"5585999999999","text":"Teste da Evolution API"}'
```

Via CLI:

```bash
docker compose run --rm worker-celery \
  python -m app.cli send --instance main --number 5585999999999 --text "Teste da Evolution API"
```

### 4. Enviar mensagens em lote

O envio em lote cria uma tarefa no Celery. O worker envia uma mensagem por vez e pode esperar alguns segundos entre os destinatarios.

Via API HTTP da POC:

```bash
curl -X POST http://localhost:8000/messages/bulk \
  -H 'Content-Type: application/json' \
  -d '{
    "instance":"main",
    "recipients":["5585999999999","5585888888888"],
    "message":"Teste em lote via Celery",
    "delay_seconds":3
  }'
```

Resposta esperada:

```json
{
  "task_id": "id-da-tarefa"
}
```

Via CLI:

```bash
docker compose run --rm worker-celery \
  python -m app.cli bulk \
  --instance main \
  --numbers 5585999999999,5585888888888 \
  --text "Teste em lote via Celery" \
  --delay 3
```

## Rotas da API Python

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/health` | Verifica se a API da POC esta online |
| `POST` | `/instances` | Cria uma instancia na Evolution API |
| `POST` | `/instances/qrcode` | Gera/salva o QR Code da instancia |
| `POST` | `/messages/text` | Envia uma mensagem individual |
| `POST` | `/messages/bulk` | Agenda envio em lote pelo Celery |

Para testar as rotas pelo navegador, acesse:

```text
http://localhost:8000/docs
```

## Comandos Uteis

Subir tudo:

```bash
docker compose up -d --build
```

Parar tudo:

```bash
docker compose down
```

Ver status:

```bash
docker compose ps
```

Ver logs da Evolution API:

```bash
docker logs -f evolution-api
```

Ver logs da API Python:

```bash
docker logs -f evolution-poc-api
```

Ver logs do worker Celery:

```bash
docker logs -f evolution-celery-worker
```

Recriar somente a Evolution API depois de mudar `.env`:

```bash
docker compose up -d --force-recreate evolution-api
```

## Como o Codigo Funciona

O arquivo `evolution-poc/app/evolution_client.py` centraliza as chamadas HTTP para a Evolution API. Ele cria instancia, conecta, salva QR Code e envia mensagem de texto.

O arquivo `evolution-poc/app/api.py` expoe essas operacoes como rotas FastAPI.

O arquivo `evolution-poc/app/tasks.py` define a tarefa `send_bulk_messages`, que recebe uma lista de numeros e envia as mensagens uma por uma usando o Celery.

O arquivo `evolution-poc/app/cli.py` permite executar as mesmas acoes pelo terminal.

## Problemas Comuns

### QR Code nao aparece

Confira se `CONFIG_SESSION_PHONE_VERSION` esta vazio no `.env`:

```env
CONFIG_SESSION_PHONE_VERSION=
```

Tambem evite criar a instancia com campo `number`, porque isso pode ativar pareamento por numero em vez de QR Code.

### Erro de autenticacao

Confira se `AUTHENTICATION_API_KEY` no `.env` esta preenchido. A POC usa essa chave para chamar a Evolution API pelo header `apikey`.

### Erro ao conectar no banco

Dentro do Docker, a URL do banco deve apontar para `postgres:5432`:

```env
DATABASE_CONNECTION_URI=postgresql://evolution:evolution@postgres:5432/evolution
```

A porta `5433` e apenas para acessar o PostgreSQL a partir da sua maquina.

### Mensagem em lote nao envia

Confira se o worker esta rodando:

```bash
docker compose ps worker-celery
```

E acompanhe os logs:

```bash
docker logs -f evolution-celery-worker
```
