import { useState, useEffect } from 'react'
import Map, { Marker, NavigationControl, Popup } from 'react-map-gl'
import { mapsApi } from '../../services/api'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || ''

export default function InspectionMap({ height = '600px' }: { height?: string }) {
  const [viewport, setViewport] = useState({ longitude: -122.4, latitude: 37.8, zoom: 12 })
  const [detections, setDetections] = useState<any[]>([])
  const [selectedDetection, setSelectedDetection] = useState<any>(null)

  useEffect(() => { loadDetections() }, [])
  const loadDetections = async () => {
    try { const res = await mapsApi.getDetections(); setDetections(res.data.features || []) } catch (e) {}
  }

  const severityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626'
      case 'high': return '#ea580c'
      case 'medium': return '#ca8a04'
      case 'low': return '#16a34a'
      default: return '#0891b2'
    }
  }

  return (
    <div style={{ height, width: '100%' }} className="rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      <Map {...viewport} onMove={(evt) => setViewport(evt.viewState)} style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/satellite-v9" mapboxAccessToken={MAPBOX_TOKEN}>
        <NavigationControl position="top-right" />
        {detections.map((det) => (
          <Marker key={det.properties.id} longitude={det.geometry.coordinates[0]} latitude={det.geometry.coordinates[1]}
            anchor="bottom" onClick={(e) => { e.originalEvent.stopPropagation(); setSelectedDetection(det) }}>
            <div className="w-4 h-4 rounded-full border-2 border-white shadow-lg cursor-pointer hover:scale-125 transition-transform"
              style={{ backgroundColor: severityColor(det.properties.severity) }} />
          </Marker>
        ))}
        {selectedDetection && (
          <Popup longitude={selectedDetection.geometry.coordinates[0]} latitude={selectedDetection.geometry.coordinates[1]}
            anchor="top" onClose={() => setSelectedDetection(null)} closeButton closeOnClick={false}>
            <div className="p-2 min-w-[200px]">
              <p className="font-semibold capitalize">{selectedDetection.properties.class_name.replace('_', ' ')}</p>
              <p className="text-sm"><span className="text-gray-500">Severity:</span> <b>{selectedDetection.properties.severity.toUpperCase()}</b></p>
              <p className="text-sm"><span className="text-gray-500">Confidence:</span> {(selectedDetection.properties.confidence * 100).toFixed(1)}%</p>
            </div>
          </Popup>
        )}
      </Map>
    </div>
  )
}