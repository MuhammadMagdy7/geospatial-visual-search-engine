import { useSearchStore } from '../../stores/searchStore'
import ResultCard from './ResultCard'

const ResultsList = () => {
  const { results, isSearching, searchTime, tilesProcessed, tilesFromCache, queryType, warnings } = useSearchStore()

  if (isSearching) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-20 bg-secondary/50 animate-pulse rounded-md" />
        ))}
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-xs text-muted-foreground">No results to display.<br />Upload an image or enter text and select a region.</p>
      </div>
    )
  }

  const modeBadge = queryType === 'ai_detection'
    ? { label: 'AI Detection', cls: 'bg-green-100 text-green-700' }
    : queryType === 'text'
      ? { label: 'Text Search', cls: 'bg-blue-100 text-blue-700' }
      : { label: 'Image Search', cls: 'bg-purple-100 text-purple-700' };

  return (
    <div className="space-y-3 pb-4">
      <div className="text-xs text-gray-600 mb-2 p-2 bg-gray-50 rounded border">
        <div className="flex items-center justify-between mb-1">
          <span className="font-semibold">Search Summary</span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${modeBadge.cls}`}>
            {modeBadge.label}
          </span>
        </div>
        {queryType === 'ai_detection' ? (
          <p>Detected {results.length} objects in {searchTime}ms</p>
        ) : (
          <>
            <p>Found {results.length} results in {searchTime}ms</p>
            <p className="text-gray-500">({tilesProcessed} tiles, {tilesFromCache} from cache)</p>
          </>
        )}
        
        {warnings?.length > 0 && (
          <div className="mt-2 text-amber-600 bg-amber-50 p-1.5 rounded border border-amber-200">
            {warnings.map((warn, i) => (
              <p key={i} className="flex items-start gap-1">
                <span className="shrink-0 mt-0.5">⚠️</span> 
                <span>{warn}</span>
              </p>
            ))}
          </div>
        )}
      </div>
      
      {results.map((result, index) => (
        <ResultCard key={result.id} result={result} rank={index + 1} />
      ))}
    </div>
  )
}

export default ResultsList
