import { Loader2, Search } from 'lucide-react'
import { useSearchStore } from '../../stores/searchStore'
import { useMapStore } from '../../stores/mapStore'
import { useSearch } from '../../hooks/useSearch'

const SearchButton = () => {
  const { queryImage, isSearching } = useSearchStore()
  const { selectedBBox } = useMapStore()
  const { mutate: performSearch } = useSearch()

  const isDisabled = !queryImage || !selectedBBox || isSearching

  return (
    <button
      onClick={() => performSearch()}
      disabled={isDisabled}
      className={`
        w-full py-2.5 rounded-md flex items-center justify-center gap-2 font-semibold transition-all
        ${isDisabled 
          ? 'bg-secondary text-muted-foreground cursor-not-allowed opacity-70' 
          : 'bg-[#1D9E75] hover:bg-[#1D9E75]/90 text-white shadow-lg shadow-[#1D9E75]/20 active:scale-[0.98]'}
      `}
    >
      {isSearching ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Searching...</span>
        </>
      ) : (
        <>
          <Search className="w-4 h-4" />
          <span>Search Region</span>
        </>
      )}
    </button>
  )
}

export default SearchButton
