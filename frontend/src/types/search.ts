export interface SearchResult {
  id: number;
  latitude: number;
  longitude: number;
  similarity: number;
  tile_size: number;
  google_maps_link: string;
  tile_x?: number;
  tile_y?: number;
  detected_class?: string; // Populated in AI Detection mode
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  search_time_ms: number;
  tiles_processed: number;
  tiles_from_cache: number;
  query_type: string;
  search_mode: string;
}

export interface SearchSettings {
  // AI Detection settings
  targetClass: string;
  confidenceThreshold: number;
  // RemoteCLIP settings
  threshold: number;
  tileSize: number;
  zoomLevel: number;
  // Shared
  topK: number;
}

export type SearchMode = 'ai_detection' | 'visual_similarity' | 'text_search';
