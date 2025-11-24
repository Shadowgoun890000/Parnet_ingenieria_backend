// assets/js/productos.js

const API_BASE_URL = 'http://127.0.0.1:5000';

// Elementos del DOM
const categoriasListEl = document.getElementById('lista-categorias');
const gridProductosEl = document.getElementById('grid-productos');
const resumenResultadosEl = document.getElementById('resumen-resultados');
const paginacionEl = document.getElementById('paginacion-productos');

const formBusqueda = document.getElementById('form-busqueda-productos');
const inputBusqueda = document.getElementById('busqueda');
const btnLimpiarFiltros = document.getElementById('btn-limpiar-filtros');
const linkReporteProductos = document.getElementById('link-reporte-productos');

// Slider destacados
const sliderTrackEl = document.getElementById('slider-destacados');
const sliderPrevBtn = document.getElementById('slider-prev');
const sliderNextBtn = document.getElementById('slider-next');

// Estado de filtros / paginación
let currentPage = 1;
let perPage = 9;
let currentSearch = '';
let currentCategoriaId = null;
let totalProductos = 0;
let totalPages = 1;

// Estado del slider
let sliderIndex = 0;
let sliderItemsCount = 0;

// ==================== CARGAR CATEGORÍAS ====================

async function cargarCategorias() {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/public/categorias`);
        if (!resp.ok) {
            throw new Error('No se pudo obtener el catálogo de categorías');
        }

        const data = await resp.json();
        const categorias = data.categorias || [];

        categoriasListEl.innerHTML = '';

        // Opción "Todas"
        const liTodas = document.createElement('li');
        liTodas.innerHTML = `
            <a href="#" data-categoria-id=""
               class="areas-link-categoria active">
                Todas las categorías
            </a>
        `;
        categoriasListEl.appendChild(liTodas);

        categorias.forEach(cat => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="#" data-categoria-id="${cat.id}"
                   class="areas-link-categoria">
                    ${cat.nombre}
                </a>
            `;
            categoriasListEl.appendChild(li);
        });

        // Delegación de eventos para filtros
        categoriasListEl.addEventListener('click', event => {
            const link = event.target.closest('.areas-link-categoria');
            if (!link) return;

            event.preventDefault();

            // Quitar "active" de todos y poner al actual
            document
                .querySelectorAll('.areas-link-categoria')
                .forEach(a => a.classList.remove('active'));

            link.classList.add('active');

            const catId = link.getAttribute('data-categoria-id') || '';
            currentCategoriaId = catId ? Number(catId) : null;
            currentPage = 1;

            cargarProductos();
        });
    } catch (err) {
        console.error(err);
        categoriasListEl.innerHTML =
            '<li><span class="small text-muted">No se pudieron cargar las categorías.</span></li>';
    }
}

// ==================== CARGAR PRODUCTOS ====================

function construirUrlProductos() {
    const params = new URLSearchParams();
    params.set('page', currentPage.toString());
    params.set('per_page', perPage.toString());

    if (currentSearch.trim() !== '') {
        params.set('search', currentSearch.trim());
    }

    if (currentCategoriaId) {
        params.set('categoria_id', String(currentCategoriaId));
    }

    return `${API_BASE_URL}/api/public/productos?${params.toString()}`;
}

async function cargarProductos() {
    try {
        gridProductosEl.innerHTML = '<p class="small text-muted">Cargando productos...</p>';
        resumenResultadosEl.textContent = '';

        const url = construirUrlProductos();
        const resp = await fetch(url);

        if (!resp.ok) {
            throw new Error('No se pudo obtener el listado de productos');
        }

        const data = await resp.json();

        if (data.success === false) {
            throw new Error(data.error || 'Error en la respuesta del servidor');
        }

        const productos = data.productos || [];
        totalProductos = data.total || productos.length;
        totalPages = data.pages || 1;
        currentPage = data.current_page || 1;

        renderProductos(productos);
        renderResumen();
        renderPaginacion();
    } catch (err) {
        console.error(err);
        gridProductosEl.innerHTML =
            `<p class="products-form-message error">Ocurrió un error al cargar los productos: ${err.message}</p>`;
        paginacionEl.innerHTML = '';
        resumenResultadosEl.textContent = '';
    }
}

// ==================== RENDERIZAR PRODUCTOS ====================

function renderProductos(productos) {
    if (!productos.length) {
        gridProductosEl.innerHTML =
            '<p class="small text-muted">No se encontraron productos con los filtros actuales.</p>';
        return;
    }

    gridProductosEl.innerHTML = '';

    productos.forEach(prod => {
        const id = prod.id || prod.producto_id;
        const nombre = prod.nombre || prod.nombre_producto || 'Producto';
        const descripcion =
            prod.descripcion_corta ||
            prod.descripcion_larga ||
            prod.descripcion ||
            '';
        const categoriaNombre =
            (prod.categoria && (prod.categoria.nombre || prod.categoria)) ||
            prod.categoria_nombre ||
            '';
        const estatus =
            prod.estatus ||
            (prod.activo ? 'disponible' : 'agotado') ||
            'disponible';
        const precio =
            prod.precio ||
            prod.precio_unitario ||
            prod.costo ||
            null;

        // Imagen (si tu API trae URL)
        const imagen =
            prod.imagen_url ||
            prod.imagen ||
            null;

        const card = document.createElement('div');
        card.className = 'product-card';

        const statusClass =
            estatus.toLowerCase().includes('agot')
                ? 'agotado'
                : 'disponible';

        card.innerHTML = `
            <div class="product-card__image-wrapper">
                ${
                    imagen
                        ? `<img src="${imagen}" alt="${nombre}" class="product-card__image">`
                        : `<div class="product-card__image product-card__image--placeholder">
                               ${nombre.charAt(0)}
                           </div>`
                }
            </div>
            <div class="product-card__body">
                <div class="product-card__title">${nombre}</div>
                ${
                    categoriaNombre
                        ? `<div class="product-card__category">${categoriaNombre}</div>`
                        : ''
                }
                ${
                    descripcion
                        ? `<div class="product-card__desc">${descripcion}</div>`
                        : ''
                }
                <div class="product-card__price-status">
                    <div class="product-card__price">
                        ${precio ? `Desde $${precio}` : ''}
                    </div>
                    <span class="badge-status ${statusClass}">
                        ${estatus}
                    </span>
                </div>
                <div class="product-card__actions">
                    <button type="button"
                            class="btn btn-outline-primary btn-sm btn-ficha-producto"
                            data-producto-id="${id}">
                        Ficha técnica (PDF)
                    </button>
                </div>
            </div>
        `;

        gridProductosEl.appendChild(card);
    });
}

// ==================== RESUMEN Y PAGINACIÓN ====================

function renderResumen() {
    if (!totalProductos) {
        resumenResultadosEl.textContent = '';
        return;
    }

    const inicio = (currentPage - 1) * perPage + 1;
    const fin = Math.min(currentPage * perPage, totalProductos);

    let texto = `Mostrando ${inicio}–${fin} de ${totalProductos} producto(s)`;

    if (currentSearch.trim()) {
        texto += ` para la búsqueda "${currentSearch.trim()}"`;
    }

    resumenResultadosEl.textContent = texto;
}

function renderPaginacion() {
    paginacionEl.innerHTML = '';

    if (totalPages <= 1) return;

    const createBtn = (page, label = null, disabled = false, active = false) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-light products-page-btn';
        if (active) btn.classList.add('active');
        if (disabled) btn.disabled = true;
        btn.dataset.page = String(page);
        btn.textContent = label || String(page);
        return btn;
    };

    // Botón anterior
    const btnPrev = createBtn(
        currentPage - 1,
        '«',
        currentPage === 1
    );
    paginacionEl.appendChild(btnPrev);

    // Páginas
    for (let p = 1; p <= totalPages; p++) {
        const btn = createBtn(p, String(p), false, p === currentPage);
        paginacionEl.appendChild(btn);
    }

    // Botón siguiente
    const btnNext = createBtn(
        currentPage + 1,
        '»',
        currentPage === totalPages
    );
    paginacionEl.appendChild(btnNext);

    // Manejar clicks
    paginacionEl.addEventListener('click', event => {
        const btn = event.target.closest('.products-page-btn');
        if (!btn) return;

        const page = Number(btn.dataset.page);
        if (!page || page === currentPage) return;

        currentPage = page;
        cargarProductos();
    }, { once: true });
}

// ==================== SLIDER DESTACADOS ====================

async function cargarProductosDestacados() {
    if (!sliderTrackEl) return;

    try {
        const resp = await fetch(`${API_BASE_URL}/api/public/productos/destacados?limit=10`);
        if (!resp.ok) {
            throw new Error('No se pudo obtener el listado de productos destacados');
        }

        const data = await resp.json();
        const destacados = data.productos || data || [];

        sliderTrackEl.innerHTML = '';

        if (!destacados.length) {
            sliderTrackEl.innerHTML =
                '<div class="small text-muted">No hay productos destacados por el momento.</div>';
            if (sliderPrevBtn) sliderPrevBtn.disabled = true;
            if (sliderNextBtn) sliderNextBtn.disabled = true;
            return;
        }

        destacados.forEach(prod => {
            const id = prod.id || prod.producto_id;
            const nombre = prod.nombre || prod.nombre_producto || 'Producto';
            const descripcion =
                prod.descripcion_corta ||
                prod.descripcion_larga ||
                prod.descripcion ||
                '';
            const categoriaNombre =
                (prod.categoria && (prod.categoria.nombre || prod.categoria)) ||
                prod.categoria_nombre ||
                '';
            const imagen =
                prod.imagen_url ||
                prod.imagen ||
                null;

            const slide = document.createElement('div');
            slide.className = 'slider-item';

            slide.innerHTML = `
                <div class="slider-card">
                    <div class="slider-card__image-wrapper">
                        ${
                            imagen
                                ? `<img src="${imagen}" alt="${nombre}" class="slider-card__image">`
                                : `<div class="slider-card__image slider-card__image--placeholder">
                                       ${nombre.charAt(0)}
                                   </div>`
                        }
                    </div>
                    <div class="slider-card__body">
                        <div class="slider-card__title">${nombre}</div>
                        ${
                            categoriaNombre
                                ? `<div class="slider-card__category">${categoriaNombre}</div>`
                                : ''
                        }
                        ${
                            descripcion
                                ? `<div class="slider-card__desc">${descripcion}</div>`
                                : ''
                        }
                        <button type="button"
                                class="btn btn-outline-primary btn-sm btn-ficha-producto"
                                data-producto-id="${id}">
                            Ficha técnica (PDF)
                        </button>
                    </div>
                </div>
            `;

            sliderTrackEl.appendChild(slide);
        });

        sliderItemsCount = destacados.length;
        sliderIndex = 0;
        actualizarSlider();
    } catch (err) {
        console.error(err);
        sliderTrackEl.innerHTML =
            '<div class="small text-muted">Error al cargar productos destacados.</div>';
        if (sliderPrevBtn) sliderPrevBtn.disabled = true;
        if (sliderNextBtn) sliderNextBtn.disabled = true;
    }
}

function actualizarSlider() {
    if (!sliderTrackEl || sliderItemsCount === 0) return;

    const itemWidth = 260; // ancho aproximado de cada tarjeta + gap
    const offset = -sliderIndex * itemWidth;

    sliderTrackEl.style.transform = `translateX(${offset}px)`;

    if (sliderPrevBtn) {
        sliderPrevBtn.disabled = (sliderIndex === 0);
    }
    if (sliderNextBtn) {
        sliderNextBtn.disabled = (sliderIndex >= sliderItemsCount - 1);
    }
}

// ==================== MANEJO DE EVENTOS ====================

// Búsqueda
if (formBusqueda) {
    formBusqueda.addEventListener('submit', event => {
        event.preventDefault();
        currentSearch = inputBusqueda.value || '';
        currentPage = 1;
        cargarProductos();
    });
}

// Limpiar filtros
if (btnLimpiarFiltros) {
    btnLimpiarFiltros.addEventListener('click', () => {
        inputBusqueda.value = '';
        currentSearch = '';
        currentCategoriaId = null;
        currentPage = 1;

        // Quitar active de categorías
        document
            .querySelectorAll('.areas-link-categoria')
            .forEach(a => a.classList.remove('active'));

        cargarProductos();
    });
}

// Reporte general PDF
if (linkReporteProductos) {
    linkReporteProductos.addEventListener('click', event => {
        event.preventDefault();
        const url = `${API_BASE_URL}/api/utils/productos/reporte-pdf`;
        window.open(url, '_blank');
    });
}

// Ficha técnica PDF (delegación en el grid + slider)
if (gridProductosEl) {
    gridProductosEl.addEventListener('click', event => {
        const btn = event.target.closest('.btn-ficha-producto');
        if (!btn) return;

        const productoId = btn.getAttribute('data-producto-id');
        if (!productoId) return;

        const url = `${API_BASE_URL}/api/utils/productos/${productoId}/ficha-pdf`;
        window.open(url, '_blank');
    });
}

if (sliderTrackEl) {
    sliderTrackEl.addEventListener('click', event => {
        const btn = event.target.closest('.btn-ficha-producto');
        if (!btn) return;

        const productoId = btn.getAttribute('data-producto-id');
        if (!productoId) return;

        const url = `${API_BASE_URL}/api/utils/productos/${productoId}/ficha-pdf`;
        window.open(url, '_blank');
    });
}

// Slider botones
if (sliderPrevBtn) {
    sliderPrevBtn.addEventListener('click', () => {
        if (sliderIndex > 0) {
            sliderIndex--;
            actualizarSlider();
        }
    });
}

if (sliderNextBtn) {
    sliderNextBtn.addEventListener('click', () => {
        if (sliderIndex < sliderItemsCount - 1) {
            sliderIndex++;
            actualizarSlider();
        }
    });
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    if (categoriasListEl && gridProductosEl) {
        cargarCategorias();
        cargarProductos();
    }
    if (sliderTrackEl) {
        cargarProductosDestacados();
    }
});
