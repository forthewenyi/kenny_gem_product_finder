import { useEffect, useRef, useState, useCallback } from 'react'

interface ProgressEvent {
  type: string
  message: string
  data?: any
  timestamp?: number
}

interface UseSearchWebSocketReturn {
  isConnected: boolean
  progressMessage: string
  progressData: any
  currentAgent: string
  totalSearches: number
  sendSearch: (query: string, maxPrice?: number, context?: any, characteristics?: any) => void
  disconnect: () => void
}

export function useSearchWebSocket(onComplete?: (result: any) => void): UseSearchWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [progressMessage, setProgressMessage] = useState('')
  const [progressData, setProgressData] = useState<any>({})
  const [currentAgent, setCurrentAgent] = useState('')
  const [totalSearches, setTotalSearches] = useState(0)

  const wsRef = useRef<WebSocket | null>(null)
  const onCompleteRef = useRef(onComplete)

  // Keep onComplete ref updated
  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
    setProgressMessage('')
    setProgressData({})
    setCurrentAgent('')
    setTotalSearches(0)
  }, [])

  const sendSearch = useCallback((
    query: string,
    maxPrice?: number,
    context?: any,
    characteristics?: any
  ) => {
    // Close existing connection if any
    disconnect()

    // Determine WebSocket URL based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000'
    const wsUrl = `${protocol}//${host}/ws/search-progress`

    console.log('🔌 Connecting to WebSocket:', wsUrl)

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('✅ WebSocket connected')
      setIsConnected(true)
      setProgressMessage('Connecting to Kenny...')

      // Send search query
      ws.send(JSON.stringify({
        query,
        max_price: maxPrice,
        context,
        characteristics
      }))
    }

    ws.onmessage = (event) => {
      try {
        const data: ProgressEvent = JSON.parse(event.data)
        console.log('📨 WebSocket message:', data)

        // Update progress message
        setProgressMessage(data.message)
        setProgressData(data.data || {})

        // Handle different event types
        switch (data.type) {
          case 'search_started':
            setProgressMessage(`Starting search for: ${data.data?.query}`)
            break

          case 'agent_progress':
            setCurrentAgent(data.data?.agent || '')
            setProgressMessage(data.message)
            break

          case 'search_query':
            setTotalSearches(data.data?.total_searches || 0)
            setProgressMessage(data.message)
            break

          case 'search_complete':
            setProgressMessage(`Found ${data.data?.products_found || 0} products!`)
            // Note: The actual result data will come from the regular API call
            // This just signals completion
            setTimeout(() => {
              disconnect()
            }, 1000)
            break

          case 'error':
            console.error('❌ WebSocket error:', data.message)
            setProgressMessage(`Error: ${data.message}`)
            disconnect()
            break
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error)
      setProgressMessage('Connection error')
      setIsConnected(false)
    }

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected')
      setIsConnected(false)
    }
  }, [disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    isConnected,
    progressMessage,
    progressData,
    currentAgent,
    totalSearches,
    sendSearch,
    disconnect
  }
}
