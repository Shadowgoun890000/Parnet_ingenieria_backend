// assets/js/productos.js - ACTUALIZADO

const API_BASE_URL = '';

// Elementos del DOM
const productsGridEl = document.getElementById('products-grid');
const productsFeaturedEl = document.getElementById('products-featured');
const productsFeaturedGridEl = document.getElementById('products-featured-grid');
const productsPaginationEl = document.getElementById('products-pagination');
const productsSummaryEl = document.getElementById('products-summary');
const productsOrderInfoEl = document.getElementById('products-order-info');

const searchInputEl = document.getElementById('product-search');
const categorySelectEl = document.getElementById('product-category');
const perPageSelectEl = document.getElementById('product-per-page');
const searchBtnEl = document.getElementById('product-search-btn');
const refreshBtnEl = document.getElementById('products-refresh-btn');

// Estado de filtros / paginación
let currentPage = 1;
let totalPages = 1;
let totalProductos = 0;

// ==================== UTILIDADES ====================

function getCurrentFilters() {
    return {
        search: (searchInputEl?.value || '').trim(),
        categoria_id: categorySelectEl?.value || '',
        per_page: Number(perPageSelectEl?.value || 9)
    };
}

function buildQuery(paramsObj) {
    const params = new URLSearchParams();
    Object.entries(paramsObj).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
            params.set(key, String(value));
        }
    });
    return params.toString();
}

function mapProduct(p) {
    // Adaptarse a distintos nombres de campos posibles
    return {
        id: p.id,
        nombre: p.nombre || p.nombre_producto || 'Producto',
        sku: p.sku || '',
        descripcion: p.descripcion_corta || p.descripcion || '',
        categoria: p.categoria ? (p.categoria.nombre || p.categoria) : p.nombre_categoria,
        precio: p.precio || p.precio_venta || null,
        estatus: p.estatus || 'disponible',
        imagen: p.imagen || p.imagen_url || null,
        destacado: Boolean(p.destacado)
    };
}

// ==================== CARGA DE CATEGORÍAS ====================

async function cargarCategorias() {
    if (!categorySelectEl) return;

    try {
        const resp = await fetch(`/api/public/categorias`);
        if (!resp.ok) {
            throw new Error('No se pudieron obtener las categorías');
        }

        const data = await resp.json();
        if (data.success === false) {
            throw new Error(data.error || 'Error en la respuesta de categorías');
        }

        const categorias = data.categorias || [];
        categorySelectEl.innerHTML = '<option value="">Todas</option>';

        categorias.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.nombre || cat.nombre_categoria || 'Categoría';
            categorySelectEl.appendChild(opt);
        });
    } catch (err) {
        console.error(err);
        // Si falla, dejamos solo el "Todas"
        if (categorySelectEl) {
            categorySelectEl.innerHTML = '<option value="">Todas</option>';
        }
    }
}

// ==================== CARGA DE PRODUCTOS ====================

async function cargarProductos(page = 1) {
    if (!productsGridEl) return;

    try {
        currentPage = page;
        productsGridEl.innerHTML =
            '<p class="small text-muted">Cargando productos...</p>';
        productsPaginationEl.innerHTML = '';
        productsSummaryEl.textContent = '';

        const filters = getCurrentFilters();

        const params = {
            page,
            per_page: filters.per_page,
            search: filters.search || undefined,
            categoria_id: filters.categoria_id || undefined
        };

        const qs = buildQuery(params);

        const resp = await fetch(`/api/public/productos?${qs}`);

        if (!resp.ok) {
            throw new Error('No se pudo obtener el catálogo de productos');
        }

        const data = await resp.json();
        if (data.success === false) {
            throw new Error(data.error || 'Error en la respuesta del servidor');
        }

        const productos = data.productos || [];
        totalProductos = data.total || productos.length;
        totalPages = data.pages || 1;
        currentPage = data.current_page || page;

        renderProductos(productos);
        renderPaginacion();
        renderResumen();

    } catch (err) {
        console.error(err);
        productsGridEl.innerHTML =
            `<p class="small text-danger">Ocurrió un error al cargar los productos: ${err.message}</p>`;
    }
}

function renderProductos(productos) {
    if (!productos.length) {
        productsGridEl.innerHTML =
            '<p class="small text-muted">No se encontraron productos con los filtros seleccionados.</p>';
        return;
    }

    productsGridEl.innerHTML = '';

    productos.forEach(p => {
        const prod = mapProduct(p);

        const card = document.createElement('div');
        card.className = 'product-card';

        // Construir etiqueta de estatus
        let estatusHtml = '';
        if (prod.estatus) {
            const cls = prod.estatus.toLowerCase() === 'disponible'
                ? 'badge-status disponible'
                : 'badge-status agotado';

            estatusHtml = `<span class="${cls}">${prod.estatus}</span>`;
        }

        // Precio formateado
        let precioHtml = '';
        if (prod.precio !== null && prod.precio !== undefined) {
            precioHtml = `$${Number(prod.precio).toFixed(2)}`;
        }

        // Imagen
        const imagenSrc = prod.imagen
            ? prod.imagen
            : 'assets/img/product_placeholder.png';

        card.innerHTML = `
            <div class="product-card__image-wrapper">
                <img src="${imagenSrc}"
                     alt="${prod.nombre}"
                     class="product-card__image">
            </div>
            <div class="product-card__body">
                <div class="product-card__title">${prod.nombre}</div>
                ${
                    prod.categoria
                        ? `<div class="product-card__category">${prod.categoria}</div>`
                        : ''
                }
                ${
                    prod.descripcion
                        ? `<div class="product-card__desc">${prod.descripcion}</div>`
                        : ''
                }
                <div class="product-card__price-status">
                    <div class="product-card__price">
                        ${precioHtml || ''}
                    </div>
                    <div>${estatusHtml}</div>
                </div>
                <div class="product-card__actions">
                    <button type="button"
                            class="btn btn-sm btn-primary product-pdf-btn"
                            data-product-id="${prod.id}">
                        Ficha técnica PDF
                    </button>
                    <button type="button"
                            class="btn btn-sm btn-outline-secondary product-detail-btn"
                            data-product-id="${prod.id}">
                        Detalles
                    </button>
                </div>
            </div>
        `;

        productsGridEl.appendChild(card);
    });

    // Delegación para los botones (una sola vez)
    productsGridEl.addEventListener(
        'click',
        event => {
            const pdfBtn = event.target.closest('.product-pdf-btn');
            const detailBtn = event.target.closest('.product-detail-btn');

            if (pdfBtn) {
                const id = pdfBtn.dataset.productId;
                if (id) {
                    abrirFichaTecnicaPDF(id);
                }
            }

            if (detailBtn) {
                const id = detailBtn.dataset.productId;
                if (id) {
                    mostrarDetallesProducto(id);
                }
            }
        },
        { once: true }
    );
}

function renderPaginacion() {
    if (!productsPaginationEl) return;

    productsPaginationEl.innerHTML = '';

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

    // Anterior
    const btnPrev = createBtn(
        currentPage - 1,
        '«',
        currentPage === 1
    );
    productsPaginationEl.appendChild(btnPrev);

    // Páginas numeradas
    for (let p = 1; p <= totalPages; p++) {
        const btn = createBtn(
            p,
            String(p),
            false,
            p === currentPage
        );
        productsPaginationEl.appendChild(btn);
    }

    // Siguiente
    const btnNext = createBtn(
        currentPage + 1,
        '»',
        currentPage === totalPages
    );
    productsPaginationEl.appendChild(btnNext);

    productsPaginationEl.addEventListener(
        'click',
        event => {
            const btn = event.target.closest('.products-page-btn');
            if (!btn) return;

            const page = Number(btn.dataset.page);
            if (!page || page === currentPage) return;

            cargarProductos(page);
        },
        { once: true }
    );
}

function renderResumen() {
    if (!productsSummaryEl) return;

    if (!totalProductos) {
        productsSummaryEl.textContent = 'No hay productos para mostrar.';
        return;
    }

    const filters = getCurrentFilters();

    let texto = `Total de productos: ${totalProductos}`;
    if (filters.search) {
        texto += ` | Búsqueda: "${filters.search}"`;
    }
    if (filters.categoria_id) {
        texto += ` | Categoría seleccionada`;
    }

    texto += ` | Página ${currentPage} de ${totalPages}`;

    productsSummaryEl.textContent = texto;
}

// ==================== DESTACADOS ====================

async function cargarProductosDestacados() {
    if (!productsFeaturedEl || !productsFeaturedGridEl) return;

    try {
        const resp = await fetch(`/api/public/productos/destacados?limit=4`);
        if (!resp.ok) {
            throw new Error('No se pudieron obtener productos destacados');
        }

        const data = await resp.json();
        if (data.success === false) {
            throw new Error(data.error || 'Error en destacados');
        }

        const productos = data.productos || [];
        if (!productos.length) {
            // Si no hay destacados, ocultamos el bloque
            productsFeaturedEl.classList.add('d-none');
            return;
        }

        productsFeaturedEl.classList.remove('d-none');
        productsFeaturedGridEl.innerHTML = '';

        productos.forEach(p => {
            const prod = mapProduct(p);

            const card = document.createElement('div');
            card.className = 'product-card';

            const imagenSrc = prod.imagen
                ? prod.imagen
                : 'assets/img/product_placeholder.png';

            card.innerHTML = `
                <div class="product-card__image-wrapper">
                    <img src="${imagenSrc}"
                         alt="${prod.nombre}"
                         class="product-card__image">
                </div>
                <div class="product-card__body">
                    <div class="product-card__title">${prod.nombre}</div>
                    ${
                        prod.categoria
                            ? `<div class="product-card__category">${prod.categoria}</div>`
                            : ''
                    }
                    <div class="product-card__actions">
                        <button type="button"
                                class="btn btn-sm btn-primary product-pdf-btn"
                                data-product-id="${prod.id}">
                            Ficha técnica PDF
                        </button>
                    </div>
                </div>
            `;

            productsFeaturedGridEl.appendChild(card);
        });

        // Delegación para botones PDF dentro de destacados
        productsFeaturedGridEl.addEventListener(
            'click',
            event => {
                const pdfBtn = event.target.closest('.product-pdf-btn');
                if (!pdfBtn) return;
                const id = pdfBtn.dataset.productId;
                if (!id) return;
                abrirFichaTecnicaPDF(id);
            },
            { once: true }
        );
    } catch (err) {
        console.error(err);
        // Si falla, simplemente ocultamos el bloque de destacados
        productsFeaturedEl.classList.add('d-none');
    }
}

// ==================== ACCIONES: PDF Y DETALLES ====================

function abrirFichaTecnicaPDF(productId) {
    if (!productId) return;
    // Endpoint ya definido en tu backend en app.py:
    // /api/utils/productos/<int:producto_id>/ficha-pdf
    const url = `/api/utils/productos/${productId}/ficha-pdf`;
    window.open(url, '_blank');
}

async function mostrarDetallesProducto(productId) {
    if (!productId) return;

    try {
        const resp = await fetch(`/api/public/productos/${productId}`);

        if (!resp.ok) {
            throw new Error('No se pudo obtener el detalle del producto');
        }

        const data = await resp.json();
        if (data.success === false) {
            throw new Error(data.error || 'Error en detalle de producto');
        }

        const p = data.producto || data;
        const prod = mapProduct(p);

        let detalle = `Nombre: ${prod.nombre}\n`;
        if (prod.sku) detalle += `SKU: ${prod.sku}\n`;
        if (prod.categoria) detalle += `Categoría: ${prod.categoria}\n`;
        if (prod.descripcion) detalle += `Descripción: ${prod.descripcion}\n`;
        if (prod.precio) detalle += `Precio: $${Number(prod.precio).toFixed(2)}\n`;
        if (prod.estatus) detalle += `Estatus: ${prod.estatus}\n`;

        alert(detalle);

    } catch (err) {
        console.error(err);
        alert(`Error al obtener detalles del producto: ${err.message}`);
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    if (!productsGridEl) return;

    // Cargar combos y datos iniciales
    cargarCategorias();
    cargarProductos(1);
    cargarProductosDestacados();

    // Eventos de búsqueda / filtros
    if (searchBtnEl) {
        searchBtnEl.addEventListener('click', () => {
            cargarProductos(1);
        });
    }

    if (refreshBtnEl) {
        refreshBtnEl.addEventListener('click', () => {
            searchInputEl.value = '';
            if (categorySelectEl) categorySelectEl.value = '';
            if (perPageSelectEl) perPageSelectEl.value = '9';
            cargarProductos(1);
        });
    }

    // Enter en el campo de búsqueda
    if (searchInputEl) {
        searchInputEl.addEventListener('keyup', event => {
            if (event.key === 'Enter') {
                cargarProductos(1);
            }
        });
    }

    // Cambio de categoría
    if (categorySelectEl) {
        categorySelectEl.addEventListener('change', () => {
            cargarProductos(1);
        });
    }

    // Cambio de per_page
    if (perPageSelectEl) {
        perPageSelectEl.addEventListener('change', () => {
            cargarProductos(1);
        });
    }
});