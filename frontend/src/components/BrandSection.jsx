import { useState, useEffect } from 'react';
import { fetchBrands, createBrand } from '../api';

export default function BrandSection() {
    const [brands, setBrands] = useState([]);
    const [newBrand, setNewBrand] = useState({ name: '', email: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadBrands();
    }, []);

    async function loadBrands() {
        try {
            const data = await fetchBrands();
            setBrands(data);
        } catch (err) {
            console.error(err);
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await createBrand(newBrand);
            setNewBrand({ name: '', email: '' });
            await loadBrands();
        } catch (err) {
            setError('Failed to create brand. Name might be duplicate.');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div>
            <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
                <h2>Brands</h2>
            </div>

            <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-md)' }}>
                <h3 style={{ fontSize: '1.1rem' }}>Register New Brand</h3>
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Brand Name"
                        value={newBrand.name}
                        onChange={(e) => setNewBrand({ ...newBrand, name: e.target.value })}
                        required
                    />
                    <input
                        type="email"
                        placeholder="Contact Email"
                        value={newBrand.email}
                        onChange={(e) => setNewBrand({ ...newBrand, email: e.target.value })}
                        required
                    />
                </div>
                {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Brand'}
                </button>
            </form>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
                    {brands.map((brand) => (
                        <tr key={brand.id}>
                            <td>{brand.id}</td>
                            <td>{brand.name}</td>
                            <td>{brand.email}</td>
                        </tr>
                    ))}
                    {brands.length === 0 && (
                        <tr>
                            <td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No brands found</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
