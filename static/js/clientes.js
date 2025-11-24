const API_BASE_URL = 'http://127.0.0.1:5000';

// Elemento donde se colocarán los clientes
const clientsGrid = document.getElementById('clients-grid');

// ==================== MAPEO FLEXIBLE DE CAMPOS ====================

function mapClient(raw) {
    // Nombre de la empresa
    const nombre =
        raw.nombre ||
        raw.nombre_comercial ||
        raw.razon_social ||
        'Cliente';

    // URL del cliente (sitio web)
    const url =
        raw.url ||
        raw.sitio_web ||
        raw.website ||
        raw.link ||
        '#';

    // Logo / imagen
    const logo =
        raw.logo_url ||
        raw.logo ||
        raw.imagen ||
        'assets/img/product_placeholder.png'; // reutilizamos placeholder

    return { nombre, url, logo };
}

// ==================== CARGAR CLIENTES ====================

async function cargarClientes() {
    if (!clientsGrid) return;

    try {
        const resp = await fetch(`${API_BASE_URL}/api/public/clientes`);
        if (!resp.ok) {
            throw new Error('No se pudo obtener el listado de clientes');
        }

        const data = await resp.json();
        const clientes = Array.isArray(data)
            ? data
            : (data.clientes || []);

        clientsGrid.innerHTML = '';

        if (!clientes.length) {
            clientsGrid.innerHTML = `
                <p class="small text-muted">
                    No hay clientes registrados por el momento.
                </p>
            `;
            return;
        }

        clientes.forEach(c => {
            const cliente = mapClient(c);

            const card = document.createElement('a');
            card.className = 'client-card';
            card.href = cliente.url && cliente.url !== '#'
                ? cliente.url
                : '#';
            if (cliente.url && cliente.url !== '#') {
                card.target = '_blank';
                card.rel = 'noopener';
            }

            card.innerHTML = `
                <div class="client-card__image-wrapper">
                    <img 
                        src="${cliente.logo}" 
                        alt="${cliente.nombre}" 
                        class="client-card__image"
                        onerror="this.src='assets/img/product_placeholder.png'"
                    />
                </div>
                <div class="client-card__name">
                    ${cliente.nombre}
                </div>
            `;

            clientsGrid.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        if (clientsGrid) {
            clientsGrid.innerHTML = `
                <p class="clients-error">
                    Ocurrió un error al cargar los clientes: 
                    ${err.message}
                </p>
            `;
        }
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    cargarClientes();
});
