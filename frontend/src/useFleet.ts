import { useEffect, useState } from 'react'

// Shape of each truck in the JSON the backend sends every tick
export type TruckStatus = 'traveling' | 'loading' | 'hauling' | 'dumping'

export type Truck = {
  id: number
  x: number
  y: number
  status: TruckStatus
  payload_tons: number
  target_index: number
}

export type ConnectionStatus = 'connected' | 'reconnecting'

const WS_URL = 'ws://127.0.0.1:8000/ws/fleet'
const RECONNECT_DELAY_MS = 2000

// Opens the fleet WebSocket and keeps the latest snapshot in state.
// If the socket closes, it tries again after RECONNECT_DELAY_MS.
export function useFleet() {
  const [trucks, setTrucks] = useState<Truck[]>([])
  const [status, setStatus] = useState<ConnectionStatus>('reconnecting')

  useEffect(() => {
    let socket: WebSocket
    let retryTimer: number | undefined
    // Set on unmount so the onclose handler doesn't schedule a reconnect
    let stopped = false

    function connect() {
      socket = new WebSocket(WS_URL)
      socket.onopen = () => setStatus('connected')
      socket.onmessage = (event) => setTrucks(JSON.parse(event.data) as Truck[])
      // onclose also fires after a failed attempt, so this covers errors too
      socket.onclose = () => {
        if (stopped) return
        setStatus('reconnecting')
        retryTimer = window.setTimeout(connect, RECONNECT_DELAY_MS)
      }
    }

    connect()

    // Cleanup on unmount: stop retrying and close the socket
    return () => {
      stopped = true
      window.clearTimeout(retryTimer)
      socket.close()
    }
  }, [])

  return { trucks, status }
}
