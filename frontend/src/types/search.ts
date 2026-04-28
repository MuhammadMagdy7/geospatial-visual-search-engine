export interface SearchResult {
  id: number;
  latitude: number;
  longitude: number;
  similarity: number;
  tile_size: number;
  google_maps_link: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  search_time_ms: number;
}

export interface SearchSettings {
  threshold: number;
  tileSize: number;
  zoomLevel: number;
}
