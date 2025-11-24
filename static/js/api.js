// API Utilities - Frontend JavaScript
const API_BASE_URL = '';

// Función principal para requests API
async function apiRequest(endpoint, options = {}) {
    try {
        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        // Si tenemos token, lo agregamos
        const token = localStorage.getItem('parnet_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, config);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// GET request
async function apiGet(path) {
    return apiRequest(`/api${path}`);
}

// POST request
async function apiPost(path, data) {
    return apiRequest(`/api${path}`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// PUT request
async function apiPut(path, data) {
    return apiRequest(`/api${path}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

// DELETE request
async function apiDelete(path) {
    return apiRequest(`/api${path}`, {
        method: 'DELETE',
    });
}

// Descargar archivos (PDFs)
async function apiDownload(path, filename) {
    const token = localStorage.getItem('parnet_token');
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(path, { headers });
    if (!response.ok) {
        throw new Error(`Error ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}

// Verificar autenticación
function isAuthenticated() {
    return !!localStorage.getItem('parnet_token');
}

// Redirigir si no está autenticado
function requireAuth(redirectUrl = '/admin') {
    if (!isAuthenticated()) {
        window.location.href = redirectUrl;
        return false;
    }
    return true;
}

// Logout
function logout() {
    localStorage.removeItem('parnet_token');
    localStorage.removeItem('parnet_admin');
    window.location.href = '/';
}