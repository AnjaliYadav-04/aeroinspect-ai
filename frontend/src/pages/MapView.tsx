import InspectionMap from '../components/Map/InspectionMap'

export default function MapView() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Geospatial Intelligence</h2>
        <div className="flex gap-2">
          {['critical', 'high', 'medium', 'low'].map((sev) => (
            <span key={sev} className="flex items-center gap-1 text-sm">
              <span className={`w-3 h-3 rounded-full bg-severity-${sev}`} />
              <span className="capitalize">{sev}</span>
            </span>
          ))}
        </div>
      </div>
      <InspectionMap height="calc(100vh - 200px)" />
    </div>
  )
}