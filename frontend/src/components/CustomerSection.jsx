import { useState } from 'react';
import { createCustomer, getCustomerLicenses, deleteActivation, suspendLicense, resumeLicense } from '../api';

export default function CustomerSection() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    async function handleSubmit(e) {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        try {
            const res = await createCustomer({ email });
            setMessage(`Customer created with ID: ${res.id}`);
            setEmail('');
        } catch (err) {
            setMessage('Error: Could not create customer (Email might be taken)');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div>
            <h2>Customers</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                Manage customer registry.
            </p>

            <form onSubmit={handleSubmit} style={{ maxWidth: '500px' }}>
                <input
                    type="email"
                    placeholder="Customer Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Register Customer'}
                </button>
            </form>

            {message && <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: 'var(--radius-sm)' }}>
                {message}
            </div>}

            <hr style={{ margin: '2rem 0', borderColor: 'var(--bg-card)' }} />

            <h3>Find Licenses by Customer</h3>
            <LicenseSearch />
        </div>
    );
}

function LicenseSearch() {
    const [email, setEmail] = useState('');
    const [licenses, setLicenses] = useState(null);
    const [error, setError] = useState('');

    async function handleSearch(e) {
        e.preventDefault();
        setError('');
        setLicenses(null);
        try {
            const data = await getCustomerLicenses(email);
            setLicenses(data);
        } catch (err) {
            setError('No licenses found for this email');
        }
    }

    return (
        <div>
            <form onSubmit={handleSearch} className="flex gap-4">
                <input
                    type="email"
                    placeholder="Search by Email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                />
                <button className="btn">Search</button>
            </form>

            {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

            {licenses && (

                <div className="flex" style={{ flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                    {licenses.map(l => (
                        <div key={l.id} style={{ padding: '1rem', background: 'var(--bg-card)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                            <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
                                <div>
                                    <div style={{ fontWeight: 'bold' }}>License #{l.id} - {l.product_id}</div>
                                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.9em' }}>Key: {l.key}</div>
                                </div>
                                <div className="flex gap-2">
                                    <span style={{
                                        padding: '0.25rem 0.5rem',
                                        borderRadius: '4px',
                                        background: l.is_active ? 'rgba(57, 181, 74, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                        color: l.is_active ? 'var(--success)' : 'var(--danger)'
                                    }}>
                                        {l.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                    {l.is_active ? (
                                        <button className="btn btn-sm" style={{ background: 'var(--danger)' }} onClick={async () => {
                                            if (!confirm('Suspend License?')) return;
                                            await suspendLicense(l.id);
                                            handleSearch(e); // Refresh
                                        }}>Suspend</button>
                                    ) : (
                                        <button className="btn btn-sm" style={{ background: 'var(--success)' }} onClick={async () => {
                                            await resumeLicense(l.id);
                                            handleSearch(e); // Refresh
                                        }}>Resume</button>
                                    )}
                                </div>
                            </div>

                            {/* Activations */}
                            <div style={{ marginTop: '0.5rem', borderTop: '1px solid var(--border)', paddingTop: '0.5rem' }}>
                                <div style={{ fontSize: '0.9em', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                    Seats: {l.active_seats} / {l.max_seats}
                                </div>
                                {l.activations && l.activations.length > 0 ? (
                                    <table style={{ width: '100%', fontSize: '0.9em' }}>
                                        <thead>
                                            <tr style={{ textAlign: 'left' }}>
                                                <th>Machine ID</th>
                                                <th>Name</th>
                                                <th>Action</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {l.activations.map(a => (
                                                <tr key={a.id}>
                                                    <td>{a.machine_id}</td>
                                                    <td>{a.friendly_name || '-'}</td>
                                                    <td>
                                                        <button
                                                            style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
                                                            onClick={async () => {
                                                                if (!confirm('Deactivate machine?')) return;
                                                                await deleteActivation(a.id);
                                                                handleSearch(e); // Refresh
                                                            }}
                                                        >
                                                            Deactivate
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                ) : (
                                    <div style={{ fontSize: '0.85em', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No active machines</div>
                                )}
                            </div>
                        </div>
                    ))}
                    {licenses.length === 0 && <p>No licenses found.</p>}
                </div>
            )}
        </div>
    )
}
