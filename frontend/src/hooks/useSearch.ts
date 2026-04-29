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

      if (searchMode === 'image' && !queryImage) {
        throw new Error('Please upload a query image.');
      }

      if (searchMode === 'text' && !queryText.trim()) {
        throw new Error('Please enter a search description.');
      }

      setSearching(true);

      if (searchMode === 'image' && queryImage) {
        return searchAPI.searchByImage(
          queryImage,
          selectedBBox,
          settings.threshold,
          10,
          settings.tileSize,
        );
      } else {
        return searchAPI.searchByText(
          queryText.trim(),
          selectedBBox,
          settings.threshold,
          10,
          settings.tileSize,
        );
      }
    },
    onSuccess: (data) => {
      setResults(
        data.results,
        data.search_time_ms,
        data.tiles_processed,
        data.tiles_from_cache,
        data.query_type,
      );
      setSearching(false);
    },
    onError: () => {
      setSearching(false);
    },
  });
};
