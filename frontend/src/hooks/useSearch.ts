import { useMutation } from '@tanstack/react-query';
import { searchAPI } from '../services/api';
import { useSearchStore } from '../stores/searchStore';
import { useMapStore } from '../stores/mapStore';

export const useSearch = () => {
  const setResults = useSearchStore((s) => s.setResults);
  const setSearching = useSearchStore((s) => s.setSearching);

  return useMutation({
    mutationFn: async () => {
      // Read FRESH state inside the mutationFn to avoid stale closures.
      // Zustand's getState() always returns the latest snapshot.
      const { searchMode, queryImage, queryText, settings } =
        useSearchStore.getState();
      const { selectedBBox } = useMapStore.getState();

      if (!selectedBBox) {
        throw new Error('Please select a region on the map first.');
      }

      // Mode-specific validation
      if (searchMode === 'visual_similarity' && !queryImage) {
        throw new Error('Please upload a query image.');
      }

      if (searchMode === 'text_search' && !queryText.trim()) {
        throw new Error('Please enter a search description.');
      }

      setSearching(true);

      // Build mode-specific options
      const options: Record<string, unknown> = {
        topK: settings.topK,
      };

      if (searchMode === 'ai_detection') {
        options.targetClass = settings.targetClass;
        options.confidenceThreshold = settings.confidenceThreshold;
      } else if (searchMode === 'visual_similarity') {
        options.queryImage = queryImage!;
        options.threshold = settings.threshold;
        options.tileSize = settings.tileSize;
      } else if (searchMode === 'text_search') {
        options.queryText = queryText.trim();
        options.threshold = settings.threshold;
        options.tileSize = settings.tileSize;
      }

      return searchAPI.search(selectedBBox, searchMode, options);
    },
    onSuccess: (data) => {
      // For debugging: compare frontend tile estimate vs backend actual tiles
      const { selectedBBox } = useMapStore.getState();
      if (selectedBBox && selectedBBox.length >= 2) {
        const lats = selectedBBox.map(p => p[0]);
        const lons = selectedBBox.map(p => p[1]);
        const latDiff = Math.max(...lats) - Math.min(...lats);
        const lonDiff = Math.max(...lons) - Math.min(...lons);
        const avgLat = (Math.max(...lats) + Math.min(...lats)) / 2;
        const lonCorrection = Math.cos(avgLat * Math.PI / 180);
        const latTiles = Math.ceil(latDiff / 0.0045);
        const lonTiles = Math.ceil(lonDiff / (0.0045 / lonCorrection));
        const estimatedTiles = latTiles * lonTiles;

        console.log('--- Search Complete ---');
        console.log(`Frontend Estimated Tiles: ${estimatedTiles}`);
        console.log(`Backend Processed Tiles: ${data.tiles_processed}`);
      }

      setResults(
        data.results,
        data.search_time_ms,
        data.tiles_processed,
        data.tiles_from_cache,
        data.query_type,
        data.warnings,
      );
      setSearching(false);
    },
    onError: () => {
      setSearching(false);
    },
  });
};
