import { ExternalLink, Navigation } from 'lucide-react'
import { SearchResult } from '../../types/search'
import { formatCoordinate, getScoreColor, getScoreBg } from '../../lib/utils'
import { useMapStore } from '../../stores/mapStore'

interface Props {
  result: SearchResult
  rank: number
}

const ResultCard = ({ result, rank }: Props) => {
  const { setCenter, setZoom } = useMapStore()

  const handleLocate = () => {
    setCenter([result.longitude, result.latitude])
    setZoom(18)
  }

  return (
    <div className="bg-secondary/30 border border-border rounded-md p-3 hover:bg-secondary/50 transition-colors group">
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold bg-muted px-1.5 py-0.5 rounded text-muted-foreground">#{rank}</span>
          <span className={`text-sm font-bold ${getScoreColor(result.similarity)}`}>
            {(result.similarity * 100).toFixed(1)}%
          </span>
        </div>
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onClick={handleLocate}
            className="p-1 hover:text-primary transition-colors"
            title="Locate on map"
          >
            <Navigation size={14} />
          </button>
          <a 
            href={result.google_maps_link} 
            target="_blank" 
            rel="noopener noreferrer"
            className="p-1 hover:text-primary transition-colors"
            title="Open in Google Maps"
          >
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
      
      <div className="text-[10px] font-mono text-muted-foreground space-y-0.5">
        <p>LAT: {formatCoordinate(result.latitude)}</p>
        <p>LON: {formatCoordinate(result.longitude)}</p>
      </div>
      
      <div className="mt-2 h-1 w-full bg-secondary rounded-full overflow-hidden">
        <div 
          className={`h-full ${getScoreBg(result.similarity)}`} 
          style={{ width: `${result.similarity * 100}%` }}
        />
      </div>
    </div>
  )
}

export default ResultCard
