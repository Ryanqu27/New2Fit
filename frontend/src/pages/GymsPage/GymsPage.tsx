import { useState, useEffect } from 'react';
import { getGymLocations } from './GymsPageService';
import GymMap from './GymMap';
import './GymsPage.css';

export default function GymsPage() {
    const [gyms, setGyms] = useState([]);
    useEffect(() => {
        const fetchGyms = async () => {
            const response = await getGymLocations();
            setGyms(response);
        }
        fetchGyms();
    }, []);
    return (
        <div style={{ padding: '20px' }}>
            <h1 className="gyms-title">Find a Gym Near You</h1>
            <GymMap gyms={gyms} />
        </div>
    );
}