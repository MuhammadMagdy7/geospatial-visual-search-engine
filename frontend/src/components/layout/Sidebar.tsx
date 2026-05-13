import ImageUpload from '../search/ImageUpload'
import TextSearch from '../search/TextSearch'
import SearchModeToggle from '../search/SearchModeToggle'
import SearchSettings from '../search/SearchSettings'
import SearchButton from '../search/SearchButton'
import ResultsList from '../results/ResultsList'
import { useSearchStore } from '../../stores/searchStore'

const Sidebar = () => {
  const { searchMode } = useSearchStore()

  return (
    <aside className="w-[320px] border-r flex flex-col overflow-hidden bg-card">
      <div className="p-4 space-y-6 overflow-y-auto flex-1 custom-scrollbar">
        <section>
          <SearchModeToggle />
          {searchMode === 'ai_detection' && (
            <div className="text-xs text-muted-foreground bg-secondary/30 rounded-md p-3 border border-border">
              <p className="font-medium text-foreground mb-1">🎯 AI Detection Mode</p>
              <p>Select an object class below and draw a region on the map. YOLOv8 will detect objects automatically.</p>
            </div>
          )}
          {searchMode === 'visual_similarity' && <ImageUpload />}
          {searchMode === 'text_search' && <TextSearch />}
        </section>
        
        <section>
          <h2 className="text-sm font-semibold mb-3 uppercase tracking-wider text-muted-foreground">Search Settings</h2>
          <SearchSettings />
        </section>
        
        <SearchButton />
        
        <section className="pt-4 border-t">
          <h2 className="text-sm font-semibold mb-3 uppercase tracking-wider text-muted-foreground">Results</h2>
          <ResultsList />
        </section>
      </div>
    </aside>
  )
}

export default Sidebar
