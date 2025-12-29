const API_URL = 'http://127.0.0.1:8000';

export async function fetchBrands() {
    const res = await fetch(`${API_URL}/brands/`);
    return res.json();
}

export async function createBrand(data) {
    const res = await fetch(`${API_URL}/brands/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create brand');
    return res.json();
}

export async function fetchProducts() {
    const res = await fetch(`${API_URL}/products/`);
    return res.json();
}

export async function createProduct(data) {
    const res = await fetch(`${API_URL}/products/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create product');
    return res.json();
}

export async function fetchCustomers() {
    const res = await fetch(`${API_URL}/customers/`);
    return res.json();
}

export async function getCustomerLicenses(email) {
    const res = await fetch(`${API_URL}/customers/${email}/licenses`);
    if (!res.ok) throw new Error('Failed to fetch licenses');
    return res.json();
}

export async function deleteActivation(id) {
    const res = await fetch(`${API_URL}/activations/${id}`, {
        method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to create activation');
    return res.json();
}

export async function suspendLicense(id) {
    const res = await fetch(`${API_URL}/licenses/${id}/suspend`, { method: 'PUT' });
    if (!res.ok) throw new Error('Failed to suspend license');
    return res.json();
}

export async function resumeLicense(id) {
    const res = await fetch(`${API_URL}/licenses/${id}/resume`, { method: 'PUT' });
    if (!res.ok) throw new Error('Failed to resume license');
    return res.json();
}

export async function createCustomer(data) {
    const res = await fetch(`${API_URL}/customers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create customer');
    return res.json();
}

export async function createLicense(data) {
    const res = await fetch(`${API_URL}/licenses/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to issue license');
    return res.json();
}

export async function validateLicense(data) {
    const res = await fetch(`${API_URL}/licenses/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return res.json();
}
