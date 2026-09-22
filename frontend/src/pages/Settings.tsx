import { useState } from 'react'
import { Save, Key, Database, Bell } from 'lucide-react'

export default function Settings() {
  const [settings, setSettings] = useState({
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    mapboxToken: import.meta.env.VITE_MAPBOX_TOKEN || '',
    notifications: true,
    autoRefresh: true,
  })

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
      <div className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
          <Database size={20} className="text-primary-600" />
          <h3 className="text-lg font-semibold">API Configuration</h3>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Backend API URL</label>
            <input type="text" value={settings.apiUrl} onChange={(e) => setSettings({...settings, apiUrl: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mapbox Token</label>
            <div className="relative">
              <Key size={16} className="absolute left-3 top-3 text-gray-400" />
              <input type="password" value={settings.mapboxToken} onChange={(e) => setSettings({...settings, mapboxToken: e.target.value})}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
            </div>
          </div>
        </div>
      </div>
      <div className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
          <Bell size={20} className="text-primary-600" />
          <h3 className="text-lg font-semibold">Notifications</h3>
        </div>
        <div className="space-y-4">
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-gray-700">Enable push notifications</span>
            <input type="checkbox" checked={settings.notifications} onChange={(e) => setSettings({...settings, notifications: e.target.checked})}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500" />
          </label>
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-gray-700">Auto-refresh dashboard</span>
            <input type="checkbox" checked={settings.autoRefresh} onChange={(e) => setSettings({...settings, autoRefresh: e.target.checked})}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500" />
          </label>
        </div>
      </div>
      <button className="btn-primary flex items-center gap-2"><Save size={18} /> Save Settings</button>
    </div>
  )
}