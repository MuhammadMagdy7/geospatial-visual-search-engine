import Sidebar from './Sidebar'
import MapView from '../map/MapView'
import StatusBar from './StatusBar'

const AppLayout = () => {
  return (
    <div className="flex flex-col h-screen w-full bg-background overflow-hidden">
      <header className="h-14 border-b flex items-center px-6 shrink-0">
        <h1 className="text-xl font-bold text-primary">Geospatial Visual Search Engine</h1>
      </header>
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 relative">
          <MapView />
        </main>
      </div>
      
      <StatusBar />
    </div>
  )
}

export default AppLayout
