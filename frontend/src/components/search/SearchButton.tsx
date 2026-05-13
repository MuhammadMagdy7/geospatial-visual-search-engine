import { Loader2, Search } from 'lucide-react'
import { useSearchStore } from '../../stores/searchStore'
import { useMapStore } from '../../stores/mapStore'
import { useSearch } from '../../hooks/useSearch'

const SearchButton = () => {
  const { searchMode, queryImage, queryText, isSearching } = useSearchStore()
  const { selectedBBox } = useMapStore()
  const { mutate: performSearch } = useSearch()

  const canSearch = 
    selectedBBox && 
    !isSearching && 
    (searchMode === 'ai_detection' 
      ? true 
      : searchMode === 'visual_similarity' 
        ? !!queryImage 
        : !!queryText.trim());

  const isDisabled = !canSearch;

  let estimatedTiles = 0;
  let latDiff = 0;
  let lonDiff = 0;
  let latTiles = 0;
  let lonTiles = 0;
  if (selectedBBox && selectedBBox.length >= 2) {
    const TILE_SPAN_AT_ZOOM_17 = 0.0045;  // degrees per tile (with overlap)

    const lats = selectedBBox.map(p => p[0]);
    const lons = selectedBBox.map(p => p[1]);

    latDiff = Math.max(...lats) - Math.min(...lats);
    lonDiff = Math.max(...lons) - Math.min(...lons);

    // Calculate tile count (matching backend logic)
    const avgLat = (Math.max(...lats) + Math.min(...lats)) / 2;
    const lonCorrection = Math.cos(avgLat * Math.PI / 180);

    latTiles = Math.ceil(latDiff / TILE_SPAN_AT_ZOOM_17);
    lonTiles = Math.ceil(lonDiff / (TILE_SPAN_AT_ZOOM_17 / lonCorrection));
    estimatedTiles = latTiles * lonTiles;
  }

  let warning = null;
  if (searchMode === 'ai_detection' && selectedBBox) {
    if (estimatedTiles <= 1) {
      warning = null;
    } else if (estimatedTiles <= 16) {
      warning = { color: 'text-green-500', text: `Quick tiled search (${estimatedTiles} tiles)` };
    } else if (estimatedTiles <= 64) {
      warning = { color: 'text-amber-500', text: `Tiled search (${estimatedTiles} tiles, ~10-20s)` };
    } else if (estimatedTiles <= 100) {
      warning = { color: 'text-amber-500', text: `Large search (${estimatedTiles} tiles, ~30-60s)` };
    } else {
      warning = { color: 'text-red-500', text: `Very large region (${estimatedTiles}+ tiles, may use lower resolution)` };
    }
  }

  const isTiled = estimatedTiles > 1;

  return (
    <div className="space-y-2">
      <button
        onClick={() => performSearch()}
        disabled={isDisabled}
        className={`
          w-full py-2.5 rounded-md flex items-center justify-center gap-2 font-semibold transition-all
          ${
            isDisabled
              ? 'bg-secondary text-muted-foreground cursor-not-allowed opacity-70'
              : 'bg-[#1D9E75] hover:bg-[#1D9E75]/90 text-white shadow-lg shadow-[#1D9E75]/20 active:scale-[0.98]'
          }
        `}
      >
        {isSearching ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>
              {isTiled ? "Searching tiles (may take a while)..." : "Searching..."}
            </span>
          </>
        ) : (
          <>
            <Search className="w-4 h-4" />
            <span>Search Region</span>
          </>
        )}
      </button>

      {warning && (
        <p className={`text-xs font-medium text-center ${warning.color}`}>
          {warning.text}
        </p>
      )}
    </div>
  );
}

export default SearchButton
