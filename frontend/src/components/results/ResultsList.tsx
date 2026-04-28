import { useSearchStore } from '../../stores/searchStore'
import ResultCard from './ResultCard'

const ResultsList = () => {
  const { results, isSearching } = useSearchStore()

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
        <p className="text-xs text-muted-foreground">No results to display.<br />Upload an image and select a region.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3 pb-4">
      {results.map((result, index) => (
        <ResultCard key={result.id} result={result} rank={index + 1} />
      ))}
    </div>
  )
}

export default ResultsList
