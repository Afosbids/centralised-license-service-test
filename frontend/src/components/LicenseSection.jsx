import { useState, useEffect } from 'react';
import { fetchProducts, fetchCustomers, createLicense, validateLicense } from '../api';

export default function LicenseSection() {
    const [products, setProducts] = useState([]);
    const [customers, setCustomers] = useState([]);
    const [formData, setFormData] = useState({
        customer_id: '',
        product_id: '',
        key: '',
        max_seats: 1
    });
    const [valData, setValData] = useState({
        key: '',
        product_id: ''
    });

    const [result, setResult] = useState(null);
    const [valResult, setValResult] = useState(null);

    useEffect(() => {
        fetchProducts().then(setProducts);
        fetchCustomers().then(setCustomers);
    }, []);

    async function handleIssue(e) {
        e.preventDefault();
        try {
            const res = await createLicense(formData);
            setResult({ success: true, license: res });
            setFormData({ ...formData, key: '' }); // reset key
        } catch (err) {
            setResult({ success: false, error: err.message });
        }
    }

    async function handleValidate(e) {
        e.preventDefault();
        try {
            const res = await validateLicense(valData);
            setValResult(res);
        } catch (err) {
            setValResult({ error: 'Validation request failed' });
        }
    }

    return (
        <div className="flex gap-4" style={{ flexDirection: 'column' }}>

            {/* Issue License */}
            <div style={{ padding: '1.5rem', background: 'rgba(57, 181, 74, 0.1)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(57, 181, 74, 0.2)' }}>
                <h3>Issue New License</h3>
                <form onSubmit={handleIssue} style={{ marginTop: '1rem' }}>
                    <div className="flex gap-4">
                        <select
                            value={formData.customer_id}
                            onChange={e => setFormData({ ...formData, customer_id: e.target.value })}
                            required
                        >
                            <option value="">Select Customer...</option>
                            {customers.map(c => <option key={c.id} value={c.id}>{c.email}</option>)}
                        </select>
                        <select
                            value={formData.product_id}
                            onChange={e => setFormData({ ...formData, product_id: e.target.value })}
                            required
                        >
                            <option value="">Select Product...</option>
                            {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                    </div>
                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="License Key (Optional - Auto-generated if empty)"
                            value={formData.key}
                            onChange={e => setFormData({ ...formData, key: e.target.value })}
                        />
                        <input
                            type="number"
                            placeholder="Max Seats"
                            value={formData.max_seats}
                            onChange={e => setFormData({ ...formData, max_seats: e.target.value })}
                            style={{ width: '150px' }}
                        />
                    </div>
                    <button className="btn btn-primary">Issue License</button>
                </form>
                {result && (
                    <div style={{ marginTop: '1rem', color: result.success ? 'var(--success)' : 'var(--danger)' }}>
                        {result.success ? `License Issued! ID: ${result.license.id}` : 'Failed to issue license'}
                    </div>
                )}
            </div>

            {/* Validate License */}
            <div style={{ padding: '1.5rem', background: 'rgba(56, 189, 248, 0.1)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
                <h3>Validate License</h3>
                <form onSubmit={handleValidate} style={{ marginTop: '1rem' }}>
                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="License Key"
                            value={valData.key}
                            onChange={e => setValData({ ...valData, key: e.target.value })}
                            required
                        />
                        <select
                            value={valData.product_id}
                            onChange={e => setValData({ ...valData, product_id: e.target.value })}
                            required
                        >
                            <option value="">Select Product...</option>
                            {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                    </div>
                    <button className="btn btn-primary">Validate</button>
                </form>
                {valResult && (
                    <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)' }}>
                        {valResult.valid ?
                            <span style={{ color: 'var(--success)', fontWeight: 'bold' }}>VALID ✅ (Seats: {valResult.seats_available})</span> :
                            <span style={{ color: 'var(--danger)', fontWeight: 'bold' }}>INVALID ❌ ({valResult.reason || valResult.error})</span>
                        }
                    </div>
                )}
            </div>
        </div>
    );
}
