"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
// Fix Leaflet icons in Next.js
import "leaflet-defaulticon-compatibility";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";

interface GeoResult {
  lat: string;
  lon: string;
  display_name: string;
}

function MapUpdater({ markers }: { markers: { lat: number; lng: number }[] }) {
  const map = useMap();

  useEffect(() => {
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers.map((m) => [m.lat, m.lng]));
      map.flyToBounds(bounds, { padding: [50, 50], maxZoom: 5 });
    }
  }, [markers, map]);

  return null;
}

export default function StrategicMap({ locations }: { locations: string[] }) {
  const [markers, setMarkers] = useState<{ lat: number; lng: number; name: string }[]>([]);

  useEffect(() => {
    // Geocode locations into coordinates using OpenStreetMap Nominatim API
    const fetchCoords = async () => {
      const newMarkers = [];
      for (const loc of locations) {
        try {
          let lat = 0;
          let lng = 0;
          let success = false;

          // Attempt 1: OpenStreetMap Nominatim (Good for Countries like 'USA')
          try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(loc)}&email=admin@projectchanakya.com`);
            if (res.ok) {
              const data = await res.json();
              if (data && data.length > 0) {
                lat = parseFloat(data[0].lat);
                lng = parseFloat(data[0].lon);
                success = true;
              }
            }
          } catch (e) {
            console.warn(`Nominatim failed for ${loc}, trying fallback...`);
          }

          // Attempt 2: Open-Meteo (Fallback: Good for cities/regions, Immune to CORS)
          if (!success) {
            try {
              const res2 = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(loc)}&count=1&format=json`);
              if (res2.ok) {
                const data2 = await res2.json();
                if (data2 && data2.results && data2.results.length > 0) {
                  lat = data2.results[0].latitude;
                  lng = data2.results[0].longitude;
                  success = true;
                }
              }
            } catch (e) {
              console.error(`Both Geocoders failed for ${loc}`, e);
            }
          }

          if (success) {
            newMarkers.push({ lat, lng, name: loc });
          }

          // Respect Nominatim limits by waiting (1.5 req/sec)
          await new Promise(resolve => setTimeout(resolve, 1500));
        } catch (error) {
          console.error(`Failed to geocode ${loc}`, error);
        }
      }
      setMarkers(newMarkers);
    };

    if (locations && locations.length > 0) {
      fetchCoords();
    } else {
      setMarkers([]);
    }
  }, [locations]);

  return (
    <div className="w-full h-full relative z-0">
      <MapContainer 
        center={[20, 0]} 
        zoom={2} 
        style={{ height: "100%", width: "100%", backgroundColor: "#0b0c10" }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        <MapUpdater markers={markers} />
        {markers.map((m, idx) => (
          <Marker key={idx} position={[m.lat, m.lng]}>
            <Popup>
              <div className="font-mono text-xs font-bold text-black">{m.name.toUpperCase()}</div>
              <div className="text-[9px] text-gray-500">LAT: {m.lat.toFixed(4)}</div>
              <div className="text-[9px] text-gray-500">LNG: {m.lng.toFixed(4)}</div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
