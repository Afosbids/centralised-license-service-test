import { useState, useEffect } from 'react';
import { fetchProducts, createProduct, fetchBrands } from '../api';

export default function ProductSection() {
    const [products, setProducts] = useState([]);
    const [brands, setBrands] = useState([]);
    const [newProduct, setNewProduct] = useState({ name: '', brand_id: '' });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    async function loadData() {
        const [pData, bData] = await Promise.all([fetchProducts(), fetchBrands()]);
        setProducts(pData);
        setBrands(bData);
        if (bData.length > 0 && !newProduct.brand_id) {
            setNewProduct(prev => ({ ...prev, brand_id: bData[0].id }));
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (!newProduct.brand_id) return;

        setLoading(true);
        try {
            await createProduct(newProduct);
            setNewProduct({ ...newProduct, name: '' });
            const pData = await fetchProducts();
            setProducts(pData);
        } catch (err) {
            alert('Failed to create product');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div>
            <h2>Products</h2>

            <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-md)' }}>
                <h3>Add Product</h3>
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Product Name"
                        value={newProduct.name}
                        onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                        required
                    />
                    <select
                        value={newProduct.brand_id}
                        onChange={(e) => setNewProduct({ ...newProduct, brand_id: e.target.value })}
                        required
                    >
                        <option value="" disabled>Select Brand</option>
                        {brands.map(b => (
                            <option key={b.id} value={b.id}>{b.name}</option>
                        ))}
                    </select>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Saving...' : 'Add Product'}
                </button>
            </form>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Brand ID</th>
                    </tr>
                </thead>
                <tbody>
                    {products.map((p) => (
                        <tr key={p.id}>
                            <td>{p.id}</td>
                            <td>{p.name}</td>
                            <td>{p.brand_id}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
