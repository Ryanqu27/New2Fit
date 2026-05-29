import { useState, useEffect, useRef } from 'react';
import { getGymLocations } from './GymsPageService';
import GymMap from './GymMap';
import './GymsPage.css';

export default function GymsPage() {
    const [gyms, setGyms] = useState([]);
    const [search, setSearch] = useState('');
    const locateRef = useRef<(() => void) | null>(null);

    useEffect(() => {
        const fetchGyms = async () => {
            const response = await getGymLocations();
            setGyms(response);
        }
        fetchGyms();
    }, []);

    const filteredGyms = gyms.filter((gym: any) =>
        gym.brand.toLowerCase().includes(search.toLowerCase()) ||
        gym.city.toLowerCase().includes(search.toLowerCase()) ||
        gym.state.toLowerCase().includes(search.toLowerCase())
    );

    const handleLocate = () => {
        if (locateRef.current) locateRef.current();
    };

    return (
        <div className="gyms-page">
            <div className="gyms-header">
                <h1 className="gyms-title">Find a Gym Near You</h1>
                <p className="gyms-subtitle">{filteredGyms.length} gyms found</p>
            </div>

            {/* Search bar sits above the map */}
            <div className="gyms-search-bar">
                <span className="search-icon">🔍</span>
                <input
                    className="gyms-search-input"
                    type="text"
                    placeholder="Search by gym name, city, or state..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                {search && (
                    <button className="search-clear-btn" onClick={() => setSearch('')}>✕</button>
                )}
                <button className="locate-btn" onClick={handleLocate} title="Use my location">
                    📍 Use My Location
                </button>
            </div>

            <div className="gyms-map-wrapper">
                <GymMap gyms={filteredGyms} locateRef={locateRef} />
            </div>
        </div>
    );
}