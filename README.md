# Evolution API — Docker Setup

WhatsApp API based on [Baileys](https://github.com/WhiskeySockets/Baileys), configured with PostgreSQL and Redis.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2+

## Getting started

1. Copy and edit the environment file:
   ```bash
   cp .env .env.local
   # edit .env or use .env directly
   ```

2. **Change the secrets** before starting (see [Authentication](#authentication)):
   - `AUTHENTICATION_API_KEY`
   - `AUTHENTICATION_JWT_SECRET`

3. Start the stack:
   ```bash
   docker compose up -d
   ```

4. Access the API at `http://localhost:8080`

---

## Environment Variables

### Server

| Variable | Default | Description |
|---|---|---|
| `SERVER_TYPE` | `http` | Protocol used by the server. Use `https` when running behind a reverse proxy with TLS termination. |
| `SERVER_PORT` | `8080` | Port the API listens on inside the container. |
| `SERVER_URL` | `http://localhost:8080` | Public URL of the API. Used to build webhook and QR code callback URLs. Must be reachable from external services. |
| `CORS_ORIGIN` | `*` | Allowed origins for CORS. Use `*` to allow all, or a comma-separated list of origins (e.g. `https://myapp.com`). |
| `CORS_METHODS` | `POST,GET,PUT,DELETE` | HTTP methods allowed by CORS. |
| `CORS_CREDENTIALS` | `true` | Whether cookies and authorization headers are allowed in CORS requests. |

---

### Logs

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `ERROR,WARN,DEBUG,INFO,LOG,VERBOSE,DARK,WEBHOOKS` | Comma-separated list of log levels to output. Remove levels you don't need to reduce noise (e.g. `ERROR,WARN,INFO`). |
| `LOG_COLOR` | `true` | Enables colored output in the terminal. Set to `false` in environments that don't support ANSI colors. |
| `LOG_BAILEYS` | `error` | Log level forwarded from the Baileys library. Options: `fatal`, `error`, `warn`, `info`, `debug`, `trace`. |

---

### Instance Management

| Variable | Default | Description |
|---|---|---|
| `DEL_INSTANCE` | `false` | If `true`, automatically deletes an instance when it disconnects from WhatsApp. Useful for ephemeral setups. |
| `DEL_TEMP_INSTANCES` | `true` | Removes temporary instances on API startup, clearing stale sessions left from a previous run. |

---

### Provider

Used when running Evolution API in a clustered/distributed mode where a central provider coordinates instances.

| Variable | Default | Description |
|---|---|---|
| `PROVIDER_ENABLED` | `false` | Enables the external provider mode. Leave `false` for single-node setups. |
| `PROVIDER_HOST` | `127.0.0.1` | Hostname of the provider service. |
| `PROVIDER_PORT` | `5656` | Port of the provider service. |
| `PROVIDER_PREFIX` | `evolution` | Namespace prefix used to isolate this node's data within the provider. |

---

### Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_ENABLED` | `true` | Enables persistent storage via a relational database. Should always be `true` in production. |
| `DATABASE_PROVIDER` | `postgresql` | Database engine. Currently `postgresql` is the supported option. |
| `DATABASE_CONNECTION_URI` | `postgresql://evolution:evolution@postgres:5432/evolution` | Full connection string. The host `postgres` refers to the service name in `docker-compose.yml`. Change credentials if you customize the PostgreSQL service. |
| `DATABASE_CONNECTION_CLIENT_NAME` | `evolution_api` | Identifier for this client in database logs and connection pools. |

#### What gets saved to the database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_SAVE_DATA_INSTANCE` | `true` | Saves instance metadata (name, status, settings). |
| `DATABASE_SAVE_DATA_NEW_MESSAGE` | `true` | Persists every incoming and outgoing message. |
| `DATABASE_SAVE_MESSAGE_UPDATE` | `true` | Records message status updates (delivered, read, etc.). |
| `DATABASE_SAVE_DATA_CONTACTS` | `true` | Stores contact information synced from WhatsApp. |
| `DATABASE_SAVE_DATA_CHATS` | `true` | Persists chat/conversation metadata. |
| `DATABASE_SAVE_DATA_LABELS` | `true` | Saves WhatsApp labels assigned to chats. |
| `DATABASE_SAVE_DATA_HISTORIC` | `true` | Keeps the full message history. Disable to save storage space if history is not required. |

---

### RabbitMQ

Publishes WhatsApp events to a RabbitMQ exchange. Useful for decoupling event consumers (e.g. bots, CRMs) from the API.

| Variable | Default | Description |
|---|---|---|
| `RABBITMQ_ENABLED` | `false` | Master switch for RabbitMQ integration. |
| `RABBITMQ_URI` | `amqp://guest:guest@rabbitmq:5672` | AMQP connection string. |
| `RABBITMQ_EXCHANGE_NAME` | `evolution` | Name of the exchange where events are published. |
| `RABBITMQ_GLOBAL_ENABLED` | `false` | When `true`, applies the event configuration below to all instances globally. |

#### RabbitMQ Events

Each variable below enables (`true`) or disables (`false`) publishing of that specific WhatsApp event to RabbitMQ.

| Variable | Default | Description |
|---|---|---|
| `RABBITMQ_EVENTS_APPLICATION_STARTUP` | `false` | Fired when the API starts. |
| `RABBITMQ_EVENTS_INSTANCE_CREATE` | `false` | Fired when a new instance is created. |
| `RABBITMQ_EVENTS_INSTANCE_DELETE` | `false` | Fired when an instance is deleted. |
| `RABBITMQ_EVENTS_QRCODE_UPDATED` | `false` | Fired when the QR code is refreshed. |
| `RABBITMQ_EVENTS_MESSAGES_SET` | `false` | Fired when the initial message batch is loaded. |
| `RABBITMQ_EVENTS_MESSAGES_UPSERT` | `true` | Fired on every new message received or sent. |
| `RABBITMQ_EVENTS_MESSAGES_EDITED` | `false` | Fired when a message is edited. |
| `RABBITMQ_EVENTS_MESSAGES_UPDATE` | `false` | Fired on message status updates (e.g. read receipt). |
| `RABBITMQ_EVENTS_MESSAGES_DELETE` | `false` | Fired when a message is deleted. |
| `RABBITMQ_EVENTS_SEND_MESSAGE` | `false` | Fired when the API sends a message. |
| `RABBITMQ_EVENTS_CONTACTS_SET` | `false` | Fired on initial contact sync. |
| `RABBITMQ_EVENTS_CONTACTS_UPSERT` | `false` | Fired when contacts are added or updated. |
| `RABBITMQ_EVENTS_CONTACTS_UPDATE` | `false` | Fired on contact metadata changes. |
| `RABBITMQ_EVENTS_PRESENCE_UPDATE` | `false` | Fired when a contact's presence (online/typing) changes. |
| `RABBITMQ_EVENTS_CHATS_SET` | `false` | Fired on initial chat sync. |
| `RABBITMQ_EVENTS_CHATS_UPSERT` | `false` | Fired when chats are added. |
| `RABBITMQ_EVENTS_CHATS_UPDATE` | `false` | Fired when chat metadata changes. |
| `RABBITMQ_EVENTS_CHATS_DELETE` | `false` | Fired when a chat is deleted. |
| `RABBITMQ_EVENTS_GROUPS_UPSERT` | `false` | Fired when a group is created or joined. |
| `RABBITMQ_EVENTS_GROUPS_UPDATE` | `false` | Fired when group metadata changes (name, description, etc.). |
| `RABBITMQ_EVENTS_GROUP_PARTICIPANTS_UPDATE` | `false` | Fired when group participants change (join, leave, promote). |
| `RABBITMQ_EVENTS_CONNECTION_UPDATE` | `true` | Fired on connection state changes (connecting, open, close). |
| `RABBITMQ_EVENTS_LABELS_EDIT` | `false` | Fired when a label is created or edited. |
| `RABBITMQ_EVENTS_LABELS_ASSOCIATION` | `false` | Fired when a label is associated with a chat. |
| `RABBITMQ_EVENTS_CALL` | `false` | Fired on incoming call events. |
| `RABBITMQ_EVENTS_TYPEBOT_START` | `false` | Fired when a Typebot flow starts. |
| `RABBITMQ_EVENTS_TYPEBOT_CHANGE_STATUS` | `false` | Fired when a Typebot flow status changes. |

---

### SQS (AWS Simple Queue Service)

Alternative to RabbitMQ for publishing events using AWS infrastructure.

| Variable | Default | Description |
|---|---|---|
| `SQS_ENABLED` | `false` | Enables SQS integration. |
| `SQS_ACCESS_KEY_ID` | _(empty)_ | AWS access key with SQS permissions. |
| `SQS_SECRET_ACCESS_KEY` | _(empty)_ | AWS secret key. |
| `SQS_ACCOUNT_ID` | _(empty)_ | AWS account ID (12-digit number). |
| `SQS_REGION` | _(empty)_ | AWS region where the SQS queues are located (e.g. `us-east-1`). |

---

### WebSocket

Exposes WhatsApp events over a WebSocket connection, allowing real-time consumption without a message broker.

| Variable | Default | Description |
|---|---|---|
| `WEBSOCKET_ENABLED` | `false` | Enables the WebSocket server. |
| `WEBSOCKET_GLOBAL_EVENTS` | `false` | When `true`, broadcasts all instance events over a single global WebSocket channel instead of per-instance channels. |

---

### WhatsApp Business (Cloud API)

Settings for the official Meta WhatsApp Business Cloud API integration (distinct from the Baileys-based unofficial API).

| Variable | Default | Description |
|---|---|---|
| `WA_BUSINESS_TOKEN_WEBHOOK` | `evolution` | Verification token used by Meta to validate the webhook endpoint. |
| `WA_BUSINESS_URL` | `https://graph.facebook.com` | Base URL for the Meta Graph API. |
| `WA_BUSINESS_VERSION` | `v20.0` | Graph API version to use. |
| `WA_BUSINESS_LANGUAGE` | `pt_BR` | Default language for template messages sent via the Cloud API. |

---

### Global Webhook

Configures a single webhook URL that receives events from all instances. Per-instance webhooks can also be set via the API.

| Variable | Default | Description |
|---|---|---|
| `WEBHOOK_GLOBAL_URL` | _(empty)_ | URL that will receive the HTTP POST with the event payload. |
| `WEBHOOK_GLOBAL_ENABLED` | `false` | Enables the global webhook. |
| `WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS` | `false` | When `true`, appends the event name to the URL path (e.g. `.../messages-upsert`). Useful for routing events to different handlers. |

#### Webhook Events

Each variable controls whether that event is sent to the global webhook URL.

| Variable | Default | Description |
|---|---|---|
| `WEBHOOK_EVENTS_APPLICATION_STARTUP` | `false` | API startup event. |
| `WEBHOOK_EVENTS_QRCODE_UPDATED` | `true` | New QR code available for scanning. |
| `WEBHOOK_EVENTS_MESSAGES_SET` | `true` | Initial message batch loaded on connection. |
| `WEBHOOK_EVENTS_MESSAGES_UPSERT` | `true` | New message received or sent. |
| `WEBHOOK_EVENTS_MESSAGES_EDITED` | `false` | Message was edited by sender. |
| `WEBHOOK_EVENTS_MESSAGES_UPDATE` | `true` | Message status updated (sent, delivered, read). |
| `WEBHOOK_EVENTS_MESSAGES_DELETE` | `false` | Message was deleted. |
| `WEBHOOK_EVENTS_SEND_MESSAGE` | `false` | Triggered when the API itself sends a message. |
| `WEBHOOK_EVENTS_CONTACTS_SET` | `true` | Initial contact list loaded. |
| `WEBHOOK_EVENTS_CONTACTS_UPSERT` | `true` | New contact added or updated. |
| `WEBHOOK_EVENTS_CONTACTS_UPDATE` | `false` | Contact profile updated. |
| `WEBHOOK_EVENTS_PRESENCE_UPDATE` | `false` | Contact online/typing status. High volume — enable with care. |
| `WEBHOOK_EVENTS_CHATS_SET` | `true` | Initial chat list loaded. |
| `WEBHOOK_EVENTS_CHATS_UPSERT` | `true` | New chat appeared. |
| `WEBHOOK_EVENTS_CHATS_UPDATE` | `false` | Chat metadata updated (muted, pinned, etc.). |
| `WEBHOOK_EVENTS_CHATS_DELETE` | `false` | Chat was deleted. |
| `WEBHOOK_EVENTS_GROUPS_UPSERT` | `true` | Joined or created a group. |
| `WEBHOOK_EVENTS_GROUPS_UPDATE` | `true` | Group info updated. |
| `WEBHOOK_EVENTS_GROUP_PARTICIPANTS_UPDATE` | `true` | Group member joined, left, or was promoted/demoted. |
| `WEBHOOK_EVENTS_CONNECTION_UPDATE` | `true` | Instance connection state changed. |
| `WEBHOOK_EVENTS_LABELS_EDIT` | `true` | A label was created or edited. |
| `WEBHOOK_EVENTS_LABELS_ASSOCIATION` | `true` | A label was applied to or removed from a chat. |
| `WEBHOOK_EVENTS_CALL` | `true` | Incoming voice/video call detected. |
| `WEBHOOK_EVENTS_TYPEBOT_START` | `false` | A Typebot automation started. |
| `WEBHOOK_EVENTS_TYPEBOT_CHANGE_STATUS` | `false` | A Typebot automation status changed. |
| `WEBHOOK_EVENTS_ERRORS` | `false` | Internal API errors. Useful for monitoring. |
| `WEBHOOK_EVENTS_ERRORS_WEBHOOK` | _(empty)_ | Separate URL to receive error events. Overrides the global URL for errors only. |

---

### Session Phone Configuration

Controls how the WhatsApp session identifies itself to the WhatsApp servers.

| Variable | Default | Description |
|---|---|---|
| `CONFIG_SESSION_PHONE_CLIENT` | `Evolution API` | Display name shown in WhatsApp's "Linked Devices" list on the phone. |
| `CONFIG_SESSION_PHONE_NAME` | `Chrome` | Browser name sent in the session handshake. Affects how WhatsApp identifies the device type. |
| `CONFIG_SESSION_PHONE_VERSION` | `2.3000.1015901307` | WhatsApp Web version reported to the server. Keep this updated if WhatsApp starts rejecting connections. |

---

### QR Code

| Variable | Default | Description |
|---|---|---|
| `QRCODE_LIMIT` | `30` | Maximum number of QR code generation attempts before the instance is considered failed and stops trying. |
| `QRCODE_COLOR` | `#198754` | Color of the QR code image (hex). The default is a green tone matching Evolution API's branding. |

---

### Typebot

[Typebot](https://typebot.io) is a visual chatbot builder that can be integrated with Evolution API to automate conversations.

| Variable | Default | Description |
|---|---|---|
| `TYPEBOT_API_VERSION` | `latest` | Typebot API version to use. Use `latest` or pin to a specific version (e.g. `v2`) for stability. |
| `TYPEBOT_KEEP_OPEN` | `false` | When `true`, keeps the Typebot session open after the flow ends, allowing the user to restart it without re-triggering the integration. |

---

### Chatwoot

[Chatwoot](https://www.chatwoot.com) is an open-source customer support platform. This integration syncs WhatsApp messages to Chatwoot inboxes.

| Variable | Default | Description |
|---|---|---|
| `CHATWOOT_MESSAGE_READ` | `true` | Marks messages as read in Chatwoot when they are read on WhatsApp. |
| `CHATWOOT_MESSAGE_DELETE` | `true` | Deletes messages in Chatwoot when they are deleted on WhatsApp. |
| `CHATWOOT_IMPORT_DATABASE_CONNECTION_URI` | `postgresql://evolution:evolution@postgres:5432/evolution` | Database URI used to import historical messages into Chatwoot. Should point to the same PostgreSQL instance. |
| `CHATWOOT_IMPORT_PLACEHOLDER_MEDIA_MESSAGE` | `true` | When importing history, inserts a placeholder text for media messages that cannot be directly imported (images, audio, etc.). |

---

### AI Integrations

| Variable | Default | Description |
|---|---|---|
| `OPENAI_ENABLED` | `false` | Enables the OpenAI integration for AI-assisted automations (e.g. GPT-powered chatbots). Requires additional per-instance configuration via the API. |
| `DIFY_ENABLED` | `false` | Enables the [Dify](https://dify.ai) integration, an open-source LLM app platform. Requires additional per-instance configuration via the API. |

---

### Cache (Redis)

Redis is used to cache session data, reducing database load and improving response times.

| Variable | Default | Description |
|---|---|---|
| `CACHE_REDIS_ENABLED` | `true` | Enables Redis as the cache backend. Recommended for production. |
| `CACHE_REDIS_URI` | `redis://redis:6379/6` | Redis connection string. The host `redis` refers to the service in `docker-compose.yml`. The `/6` selects database index 6, isolating Evolution API data from other apps. |
| `CACHE_REDIS_PREFIX_KEY` | `evolution` | Prefix applied to all Redis keys. Change this if running multiple Evolution API instances against the same Redis server. |
| `CACHE_REDIS_SAVE_INSTANCES` | `false` | When `true`, stores instance state in Redis in addition to the database. Can improve startup time at the cost of higher Redis memory usage. |
| `CACHE_LOCAL_ENABLED` | `false` | Enables in-process memory cache as a fallback or alternative to Redis. Not recommended for multi-instance deployments. |

---

### S3 / MinIO (File Storage)

Used to store media files (images, audio, video, documents) received via WhatsApp.

| Variable | Default | Description |
|---|---|---|
| `S3_ENABLED` | `false` | Enables S3-compatible object storage. When disabled, media is handled in-memory or not persisted. |
| `S3_ACCESS_KEY` | _(empty)_ | Access key for the S3 bucket (or MinIO user). |
| `S3_SECRET_KEY` | _(empty)_ | Secret key for the S3 bucket (or MinIO user). |
| `S3_BUCKET` | `evolution` | Name of the bucket where media files will be stored. |
| `S3_PORT` | `9000` | Port of the S3-compatible service. Use `443` for AWS S3 with SSL. |
| `S3_ENDPOINT` | _(empty)_ | Hostname of the S3-compatible service (e.g. `minio`, `s3.amazonaws.com`). |
| `S3_USE_SSL` | `false` | Set to `true` to use HTTPS when connecting to the storage service. Always enable for AWS S3 or remote MinIO. |
| `S3_REGION` | _(empty)_ | Region of the S3 bucket (e.g. `us-east-1`). Required for AWS S3. |

---

### Authentication

> **These values must be changed before deploying to any non-local environment.**

| Variable | Default | Description |
|---|---|---|
| `AUTHENTICATION_TYPE` | `apikey` | Authentication method. `apikey` uses a static bearer token. `jwt` issues signed tokens per session. |
| `AUTHENTICATION_API_KEY` | `change-me-please` | Master API key required in the `apikey` header for all requests. Use a long random string (e.g. `openssl rand -hex 32`). |
| `AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES` | `true` | When `true`, the instance list endpoint returns each instance's individual API key. Set to `false` to hide keys from listing responses. |
| `AUTHENTICATION_JWT_EXPIRIN_IN` | `0` | JWT token expiration in seconds. `0` means tokens never expire. Set a value like `3600` (1 hour) for stricter security. |
| `AUTHENTICATION_JWT_SECRET` | _(random string)_ | Secret used to sign and verify JWT tokens. Must be a strong, unique random string. Generate with `openssl rand -hex 32`. |

---

## Generating secure secrets

```bash
# Generate a secure API key
openssl rand -hex 32

# Generate a secure JWT secret
openssl rand -hex 32
```

---

## Services

| Service | Internal host | Exposed port |
|---|---|---|
| Evolution API | `evolution-api:8080` | `8080` |
| PostgreSQL | `postgres:5432` | `5432` |
| Redis | `redis:6379` | `6379` |

> Remove the `ports` entry from `postgres` and `redis` in `docker-compose.yml` if you don't need direct access from the host machine.
