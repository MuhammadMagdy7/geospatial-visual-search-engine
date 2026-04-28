import { useSearchStore } from '../../stores/searchStore'
import { useQuery } from '@tanstack/react-query'
import { searchAPI } from '../../services/api'

const StatusBar = () => {
  const { results, searchTime } = useSearchStore()
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: searchAPI.getHealth,
    refetchInterval: 10000,
  })

  const isConnected = health?.status === 'online'

  return (
    <footer className="h-8 border-t bg-card px-4 flex items-center justify-between text-xs text-muted-foreground shrink-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-primary' : 'bg-destructive'}`} />
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
        {isConnected && <span>API v{health?.version}</span>}
      </div>
      
      <div className="flex items-center gap-4">
        {results.length > 0 && (
          <>
            <span>Results: {results.length}</span>
            <span>Search time: {searchTime}ms</span>
          </>
        )}
      </div>
    </footer>
  )
}

export default StatusBar
