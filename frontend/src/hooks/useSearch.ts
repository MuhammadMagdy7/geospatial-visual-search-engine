import { useMutation } from '@tanstack/react-query';
import { searchAPI } from '../services/api';
import { useSearchStore } from '../stores/searchStore';
import { useMapStore } from '../stores/mapStore';

export const useSearch = () => {
  const { setResults, setSearching, queryImage, settings } = useSearchStore();
  const { selectedBBox } = useMapStore();

  return useMutation({
    mutationFn: async () => {
      if (!queryImage || !selectedBBox) {
        throw new Error('Image and region selection are required');
      }
      setSearching(true);
      return searchAPI.search(
        queryImage,
        selectedBBox,
        settings.threshold,
        10 // topK
      );
    },
    onSuccess: (data) => {
      setResults(data.results, data.search_time_ms);
      setSearching(false);
    },
    onError: () => {
      setSearching(false);
    }
  });
};
