import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix default marker
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const createCustomIcon = (emoji, color) => L.divIcon({
  html: `<div style="
    background: ${color};
    color: white;
    border-radius: 50%;
    width: 50px; height: 50px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    border: 3px solid white;
  ">${emoji}</div>`,
  className: 'custom-div-icon',
  iconSize: [50, 50],
  iconAnchor: [25, 25]
});

const ambulanceIcon = createCustomIcon('🚑', '#e74c3c');
const emergencyIcon = createCustomIcon('⚠️', '#8b0000');
const hospitalIcon = createCustomIcon('🏥', '#27ae60');

function FitBounds({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds?.length) map.fitBounds(L.latLngBounds(bounds), { padding: [60, 60] });
  }, [bounds, map]);
  return null;
}

const Map = ({ emergencyData, routeResult, onLocationUpdate, isOptimizing }) => {
  const mapRef = useRef();
  const getBounds = () => [
    emergencyData.ambulance_location,
    emergencyData.emergency_location,
    emergencyData.hospital_location,
    ...(routeResult?.optimized_route || [])
  ];

  const handleMapClick = (e) => { if (!isOptimizing) onLocationUpdate('emergency_location', [e.latlng.lat, e.latlng.lng]); };

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer
        center={emergencyData.ambulance_location}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        eventHandlers={{ click: handleMapClick }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitBounds bounds={getBounds()} />

        <Marker position={emergencyData.ambulance_location} icon={ambulanceIcon}>
          <Popup>
            <h3>🚑 Ambulance</h3>
            <p><strong>Crew:</strong> {emergencyData.crew_size}</p>
            <p><strong>Vehicle:</strong> {emergencyData.vehicle_type.toUpperCase()}</p>
          </Popup>
        </Marker>

        <Marker position={emergencyData.emergency_location} icon={emergencyIcon}>
          <Popup>
            <h3>⚠️ Emergency</h3>
            <p><strong>Type:</strong> {emergencyData.emergency_type}</p>
            <p><strong>Patients:</strong> {emergencyData.patient_count}</p>
          </Popup>
        </Marker>

        <Marker position={emergencyData.hospital_location} icon={hospitalIcon}>
          <Popup>
            <h3>🏥 Nearest Hospital</h3>
          </Popup>
        </Marker>

        {routeResult && <Polyline positions={routeResult.optimized_route} color="#e74c3c" weight={6} opacity={0.8} dashArray="10,5" />}
      </MapContainer>
    </div>
  );
};

export default Map;
