import { create } from 'zustand';
import { SearchResult, SearchSettings, SearchMode } from '../types/search';

interface SearchState {
  // Query
  searchMode: SearchMode;
  queryImage: File | null;
  queryText: string;
  
  // Settings
  settings: SearchSettings;
  
  // Results
  results: SearchResult[];
  isSearching: boolean;
  searchTime: number;
  tilesProcessed: number;
  tilesFromCache: number;
  queryType: string;
  warnings: string[];
  
  // Actions
  setSearchMode: (mode: SearchMode) => void;
  setQueryImage: (image: File | null) => void;
  setQueryText: (text: string) => void;
  setSettings: (settings: Partial<SearchSettings>) => void;
  setResults: (
    results: SearchResult[],
    time: number,
    tilesProcessed: number,
    tilesFromCache: number,
    queryType: string,
    warnings?: string[],
  ) => void;
  setSearching: (isSearching: boolean) => void;
  resetSearch: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  searchMode: 'ai_detection',
  queryImage: null,
  queryText: '',
  settings: {
    // AI Detection defaults
    targetClass: 'plane',
    confidenceThreshold: 0.50,
    // RemoteCLIP defaults
    threshold: 0.55,
    tileSize: 120,
    zoomLevel: 17,
    // Shared
    topK: 50,
  },
  results: [],
  isSearching: false,
  searchTime: 0,
  tilesProcessed: 0,
  tilesFromCache: 0,
  queryType: 'ai_detection',
  warnings: [],

  setSearchMode: (mode) => set({ searchMode: mode }),
  setQueryImage: (image) => set({ queryImage: image }),
  setQueryText: (text) => set({ queryText: text }),
  setSettings: (newSettings) =>
    set((state) => ({
      settings: { ...state.settings, ...newSettings },
    })),
  setResults: (results, time, tilesProcessed, tilesFromCache, queryType, warnings = []) =>
    set({ results, searchTime: time, tilesProcessed, tilesFromCache, queryType, warnings }),
  setSearching: (isSearching) => set({ isSearching }),
  resetSearch: () =>
    set({
      results: [],
      searchTime: 0,
      tilesProcessed: 0,
      tilesFromCache: 0,
      warnings: [],
    }),
}));
