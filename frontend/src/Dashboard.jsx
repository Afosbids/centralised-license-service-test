import { useState } from 'react';
import BrandSection from './components/BrandSection';
import ProductSection from './components/ProductSection';
import CustomerSection from './components/CustomerSection';
import LicenseSection from './components/LicenseSection';

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('brands');

    const tabs = [
        { id: 'brands', label: 'Brands' },
        { id: 'products', label: 'Products' },
        { id: 'customers', label: 'Customers' },
        { id: 'licenses', label: 'Licenses' },
    ];

    return (
        <div className="dashboard">
            <header style={{ marginBottom: '2rem', borderBottom: '1px solid var(--bg-card)', paddingBottom: '1rem' }}>
                <h1 style={{ color: 'var(--primary)', marginBottom: '0.5rem' }}>License Manager</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Centralized administration system</p>
            </header>

            <div className="flex gap-4" style={{ marginBottom: '2rem' }}>
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`btn ${activeTab === tab.id ? 'btn-primary' : ''}`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="card">
                {activeTab === 'brands' && <BrandSection />}
                {activeTab === 'products' && <ProductSection />}
                {activeTab === 'customers' && <CustomerSection />}
                {activeTab === 'licenses' && <LicenseSection />}
            </div>
        </div>
    );
}
