export type LngLat = [number, number];

export interface BBox {
  minLat: number;
  minLon: number;
  maxLat: number;
  maxLon: number;
}

export type MapMode = 'view' | 'draw';
