import { create } from 'zustand';
import { SearchResult, SearchSettings } from '../types/search';

interface SearchState {
  queryImage: File | null;
  settings: SearchSettings;
  results: SearchResult[];
  isSearching: boolean;
  searchTime: number;
  
  setQueryImage: (image: File | null) => void;
  setSettings: (settings: Partial<SearchSettings>) => void;
  setResults: (results: SearchResult[], time: number) => void;
  setSearching: (isSearching: boolean) => void;
  resetSearch: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  queryImage: null,
  settings: {
    threshold: 0.55,
    tileSize: 120,
    zoomLevel: 17,
  },
  results: [],
  isSearching: false,
  searchTime: 0,

  setQueryImage: (image) => set({ queryImage: image }),
  setSettings: (newSettings) => set((state) => ({ 
    settings: { ...state.settings, ...newSettings } 
  })),
  setResults: (results, time) => set({ results, searchTime: time }),
  setSearching: (isSearching) => set({ isSearching }),
  resetSearch: () => set({ results: [], searchTime: 0 }),
}));
