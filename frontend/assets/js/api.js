
const API_BASE_URL = "http://127.0.0.1:5000";

// GET genérico
async function apiGet(path) {
    const res = await fetch(API_BASE_URL + path);
    if (!res.ok) {
        throw new Error(`Error ${res.status} en GET ${path}`);
    }
    return res.json();
}

// Descargar PDF
async function apiDownloadPdf(path, filename) {
    const res = await fetch(API_BASE_URL + path);
    if (!res.ok) {
        throw new Error(`Error ${res.status} al descargar PDF`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}
