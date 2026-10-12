import { useFleet, type TruckStatus } from './useFleet'
import './App.css'

// Route waypoints, same as ROUTE in backend/simulador.py
const ROUTE = [
  { x: 50, y: 20, label: 'Load' },
  { x: 90, y: 90, label: 'Dump' },
  { x: 70, y: 40, label: 'Return' },
]

const STATUS_COLORS: Record<TruckStatus, string> = {
  traveling: '#3b82f6',
  loading: '#f59e0b',
  hauling: '#10b981',
  dumping: '#ef4444',
}

function App() {
  const { trucks, status } = useFleet()

  return (
    <main className="app">
      <header>
        <h1>Fleet Live</h1>
        {/* Connection badge */}
        <span className={`badge badge-${status}`}>{status}</span>
      </header>

      <div className="layout">
        {/* Map: the 0-100 plane maps directly onto the SVG viewBox */}
        <svg className="map" viewBox="0 0 100 100">
          <polyline
            className="route"
            points={ROUTE.map((p) => `${p.x},${p.y}`).join(' ')}
          />
          {ROUTE.map((p) => (
            <g key={p.label}>
              <circle className="waypoint" cx={p.x} cy={p.y} r={1} />
              <text className="waypoint-label" x={p.x + 1.5} y={p.y - 1.5}>
                {p.label}
              </text>
            </g>
          ))}

          {/* One circle per truck, colored by status */}
          {trucks.map((t) => (
            <g key={t.id}>
              <circle cx={t.x} cy={t.y} r={2.5} fill={STATUS_COLORS[t.status]} />
              <text className="truck-label" x={t.x} y={t.y}>
                {t.id}
              </text>
            </g>
          ))}
        </svg>

        {/* Table with the same data in text form */}
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Status</th>
              <th>Payload (t)</th>
              <th>Position</th>
            </tr>
          </thead>
          <tbody>
            {trucks.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>
                  <span className="dot" style={{ background: STATUS_COLORS[t.status] }} />
                  {t.status}
                </td>
                <td>{t.payload_tons}</td>
                <td>
                  ({t.x.toFixed(1)}, {t.y.toFixed(1)})
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  )
}

export default App
