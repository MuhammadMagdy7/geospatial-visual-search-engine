import { SearchResult } from '../../types/search';
import { formatCoordinate, getScoreColor } from '../../lib/utils';

interface Props {
  result: SearchResult;
}

const ResultPopup = ({ result }: Props) => {
  return (
    <div className="p-3 min-w-[200px]">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-bold">Match Details</span>
        <span className={`text-sm font-bold ${getScoreColor(result.similarity)}`}>
          {(result.similarity * 100).toFixed(1)}%
        </span>
      </div>

      <div className="text-xs font-mono text-muted-foreground space-y-1 mb-3">
        <p>LAT: {formatCoordinate(result.latitude)}</p>
        <p>LON: {formatCoordinate(result.longitude)}</p>
      </div>

      <a
        href={result.google_maps_link}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-center text-xs bg-primary text-white px-3 py-1.5 rounded-md hover:bg-primary/90 transition-colors no-underline"
      >
        Open in Google Maps
      </a>
    </div>
  );
};

export default ResultPopup;
