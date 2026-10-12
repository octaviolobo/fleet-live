# Fleet Live

Simulador de frota de caminhões de mineração em tempo real. O backend em **FastAPI** roda vários caminhões ao mesmo tempo com `asyncio`, cada um percorrendo um ciclo de carga → transporte → descarga → retorno, e transmite o estado da frota a cada segundo via **WebSocket** para um painel em **React + TypeScript**.

![Fleet Live — visão geral](docs/screenshots/overview.png)

## Funcionalidades

- 🚚 **Múltiplos caminhões simultâneos**: cada caminhão é uma task `asyncio` independente
- 🔁 **Máquina de estados**: `traveling` → `loading` → `hauling` → `dumping` → `traveling` …
- 📡 **WebSocket em tempo real**: snapshot da frota enviado a todos os clientes a cada 1s
- 🗺️ **Mapa ao vivo em SVG** com a rota (Load, Dump, Return) e os caminhões coloridos por status
- 📋 **Tabela** com ID, status, carga (toneladas) e posição de cada caminhão
- 🔌 **Reconexão automática**: o frontend tenta reconectar a cada 2s se o backend cair

## O ciclo de transporte

| Status | Cor | O que acontece |
|---|---|---|
| `traveling` | 🔵 azul | Caminhão vazio indo até o próximo ponto da rota |
| `loading` | 🟠 laranja | No ponto **Load**, carrega 2 t/s até a capacidade máxima (10 t) |
| `hauling` | 🟢 verde | Carregado, transportando até o ponto **Dump** |
| `dumping` | 🔴 vermelho | No ponto **Dump**, descarrega 2 t/s até zerar |

Depois de descarregar, o caminhão passa pelo ponto **Return** e recomeça o ciclo.

| Carregando | Transportando |
|---|---|
| ![Loading](docs/screenshots/loading.png) | ![Hauling](docs/screenshots/hauling.png) |
| **Descarregando** | **Retornando** |
| ![Dumping](docs/screenshots/dumping.png) | ![Returning](docs/screenshots/returning.png) |

## Arquitetura

```
┌─────────────────────────────┐        WebSocket /ws/fleet        ┌──────────────────────┐
│  Backend (FastAPI)          │  ───── JSON a cada 1 segundo ───▶ │  Frontend (React)    │
│                             │                                   │                      │
│  simulador.py               │                                   │  useFleet.ts         │
│   └─ 1 task por caminhão    │                                   │   └─ estado + reconexão
│  main.py                    │                                   │  App.tsx             │
│   ├─ broadcast_fleet()      │                                   │   ├─ mapa SVG        │
│   └─ ConnectionManager      │                                   │   └─ tabela          │
└─────────────────────────────┘                                   └──────────────────────┘
```

O movimento é calculado a cada tick normalizando o vetor até o próximo waypoint e andando `speed * dt` (5 unidades/s), sem ultrapassar o destino. As coordenadas ficam num plano 0–100, que o frontend mapeia direto no `viewBox` do SVG.

## Stack

- **Backend:** Python, FastAPI, Uvicorn, asyncio, WebSockets
- **Frontend:** React 19, TypeScript, Vite
- **Infra:** Redis via Docker Compose (preparado para próximas etapas)

## Como rodar

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- Docker (opcional, para o Redis)

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

O servidor sobe em `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173` no navegador. O badge no topo mostra `connected` quando o WebSocket está ativo.

### Redis (opcional)

```bash
docker compose up -d
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Health check — `{"status": "ok"}` |
| `GET` | `/` | Snapshot atual da frota em JSON |
| `WS` | `/ws/fleet` | Stream do snapshot da frota a cada 1s |

Exemplo de snapshot:

```json
[
  { "id": 1, "x": 52.5, "y": 24.3, "status": "hauling", "payload_tons": 10, "target_index": 1 },
  { "id": 2, "x": 90.0, "y": 90.0, "status": "dumping", "payload_tons": 2, "target_index": 1 },
  { "id": 3, "x": 50.0, "y": 20.0, "status": "loading", "payload_tons": 6, "target_index": 0 }
]
```

## Estrutura do projeto

```
Fleet-Live/
├── backend/
│   ├── main.py            # App FastAPI, WebSocket e broadcast
│   ├── simulador.py       # Modelo Truck, rota e máquina de estados
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.tsx        # Mapa SVG + tabela
│       ├── App.css
│       └── useFleet.ts    # Hook do WebSocket com reconexão
├── docs/screenshots/
└── docker-compose.yml     # Redis
```
