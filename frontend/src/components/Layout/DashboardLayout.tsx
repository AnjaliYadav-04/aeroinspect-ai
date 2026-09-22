import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, ClipboardList, Box, Map, FileText, Settings as SettingsIcon, Menu, X } from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/inspections', icon: ClipboardList, label: 'Inspections' },
  { path: '/assets', icon: Box, label: 'Assets' },
  { path: '/map', icon: Map, label: 'Map View' },
  { path: '/reports', icon: FileText, label: 'Reports' },
  { path: '/settings', icon: SettingsIcon, label: 'Settings' },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-primary-900 text-white transition-all duration-300 flex flex-col`}>
        <div className="p-6 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-xl font-bold">🚁 DroneInspect</h1>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 hover:bg-primary-700 rounded">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        <nav className="flex-1 px-3 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link key={item.path} to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-primary-700 text-white' : 'text-primary-100 hover:bg-primary-800'}`}>
                <Icon size={20} />
                {sidebarOpen && <span className="font-medium">{item.label}</span>}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-primary-800">
          {sidebarOpen && <div className="text-sm text-primary-200"><p>v2.0.0</p><p className="mt-1">SQLite Edition</p></div>}
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <header className="bg-white border-b border-gray-200 px-8 py-4 sticky top-0 z-10">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold text-gray-800">
              {navItems.find(n => n.path === location.pathname)?.label || 'Dashboard'}
            </h2>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">● System Online</span>
          </div>
        </header>
        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}