'use client'

import * as React from 'react'
import { io, Socket } from 'socket.io-client'

interface SocketContextType {
  socket: Socket | null
  isConnected: boolean
  lastPong: Date | null
}

const SocketContext = React.createContext<SocketContextType>({
  socket: null,
  isConnected: false,
  lastPong: null,
})

export function useSocket() {
  return React.useContext(SocketContext)
}

interface SocketProviderProps {
  children: React.ReactNode
  url?: string
}

export function SocketProvider({ 
  children, 
  url = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3001' 
}: SocketProviderProps) {
  const [socket, setSocket] = React.useState<Socket | null>(null)
  const [isConnected, setIsConnected] = React.useState(false)
  const [lastPong, setLastPong] = React.useState<Date | null>(null)

  React.useEffect(() => {
    const socketInstance = io(url, {
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 20000,
    })

    socketInstance.on('connect', () => {
      console.log('Socket connected:', socketInstance.id)
      setIsConnected(true)
    })

    socketInstance.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason)
      setIsConnected(false)
    })

    socketInstance.on('pong', () => {
      setLastPong(new Date())
    })

    socketInstance.on('connect_error', (error) => {
      console.error('Socket connection error:', error)
      setIsConnected(false)
    })

    setSocket(socketInstance)

    return () => {
      socketInstance.disconnect()
    }
  }, [url])

  // Ping the server every 30 seconds to keep connection alive
  React.useEffect(() => {
    if (!socket || !isConnected) return

    const pingInterval = setInterval(() => {
      socket.emit('ping')
    }, 30000)

    return () => clearInterval(pingInterval)
  }, [socket, isConnected])

  const value = React.useMemo(
    () => ({
      socket,
      isConnected,
      lastPong,
    }),
    [socket, isConnected, lastPong]
  )

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}