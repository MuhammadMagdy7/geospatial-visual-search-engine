import ImageUpload from '../search/ImageUpload'
import SearchSettings from '../search/SearchSettings'
import SearchButton from '../search/SearchButton'
import ResultsList from '../results/ResultsList'

const Sidebar = () => {
  return (
    <aside className="w-[320px] border-r flex flex-col overflow-hidden bg-card">
      <div className="p-4 space-y-6 overflow-y-auto flex-1 custom-scrollbar">
        <section>
          <h2 className="text-sm font-semibold mb-3 uppercase tracking-wider text-muted-foreground">Query Image</h2>
          <ImageUpload />
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
