import { Routes, Route } from 'react-router-dom'
import DashboardLayout from './components/Layout/DashboardLayout'
import Dashboard from './pages/Dashboard'
import Inspections from './pages/Inspections'
import Assets from './pages/Assets'
import MapView from './pages/MapView'
import Reports from './pages/Reports'
import Settings from './pages/Settings'

function App() {
  return (
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/inspections" element={<Inspections />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/map" element={<MapView />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </DashboardLayout>
  )
}

export default App
