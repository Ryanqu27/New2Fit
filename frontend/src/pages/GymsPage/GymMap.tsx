import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

interface GymDTO {
    URL: string;
    latitude: number;
    longitude: number;
    city: string;
    state: string;
    brand: string;
}

interface GymMapProps {
    gyms: GymDTO[];
}

export default function GymMap({ gyms }: GymMapProps) {
    // Center the map on middle of US
    const defaultCenter: [number, number] = [39.8283, -98.5795];

    return (
        <MapContainer
            center={defaultCenter}
            zoom={4}
            style={{ height: '500px', width: '100%', borderRadius: '8px' }}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {gyms.map((gym, index) => (
                <Marker key={index} position={[gym.latitude, gym.longitude]}>
                    <Popup>
                        <strong>{gym.brand}</strong> <br />
                        {gym.city}, {gym.state} <br />
                        <a href={gym.URL} target="_blank" rel="noreferrer">
                            View Gym Details
                        </a>
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
}