export interface SearchResult {
  id: number;
  latitude: number;
  longitude: number;
  similarity: number;
  tile_size: number;
  google_maps_link: string;
  tile_x?: number;
  tile_y?: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  search_time_ms: number;
  tiles_processed: number;
  tiles_from_cache: number;
  query_type: string;
}

export interface SearchSettings {
  threshold: number;
  tileSize: number;
  zoomLevel: number;
}

export type SearchMode = 'image' | 'text';
