
let productosOriginales = [];

document.addEventListener("DOMContentLoaded", async () => {
    const searchInput = document.getElementById("search-input");
    const categorySelect = document.getElementById("category-select");
    const btnSearch = document.getElementById("btn-search");
    const btnClear = document.getElementById("btn-clear");

    try {
        // 1. Cargar productos desde el backend
        // Ajusta la ruta si tu API usa otra (ej. /api/productos)
        productosOriginales = await apiGet("/api/public/productos");

        renderCategorias(productosOriginales, categorySelect);
        renderProductos(productosOriginales);

    } catch (err) {
        console.error(err);
        document.getElementById("products-grid").innerHTML = `
          <div class="alert alert-danger">
            No se pudieron cargar los productos. Verifica que el backend esté en ejecución.
          </div>
        `;
        document.getElementById("products-count").textContent = "";
        return;
    }

    // Botón Buscar
    btnSearch.addEventListener("click", () => {
        aplicarFiltros();
    });

    // Enter en el input de búsqueda
    searchInput.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
            aplicarFiltros();
        }
    });

    // Botón limpiar filtros
    btnClear.addEventListener("click", () => {
        searchInput.value = "";
        categorySelect.value = "";
        renderProductos(productosOriginales);
    });

    // Reporte de todos los productos (PDF total)
    const btnReporte = document.getElementById("btn-reporte-productos");
    if (btnReporte) {
        btnReporte.addEventListener("click", async () => {
            try {
                // Ajusta esta ruta al endpoint real de tu backend
                await apiDownloadPdf("/api/reportes/productos", "reporte_productos.pdf");
            } catch (err) {
                console.error(err);
                alert("No se pudo generar el reporte de productos.");
            }
        });
    }
});

// Aplica búsqueda por texto + categoría
function aplicarFiltros() {
    const searchValue = document.getElementById("search-input").value.trim().toLowerCase();
    const categoryValue = document.getElementById("category-select").value;

    let filtrados = productosOriginales;

    if (searchValue) {
        filtrados = filtrados.filter(p => {
            const nombre = (p.nombre || p.name || "").toLowerCase();
            const desc = (p.descripcion || p.descripcion_corta || p.description || "").toLowerCase();
            return nombre.includes(searchValue) || desc.includes(searchValue);
        });
    }

    if (categoryValue) {
        filtrados = filtrados.filter(p => {
            const cat = (p.categoria || p.categoria_nombre || p.category || "").toString();
            return cat === categoryValue;
        });
    }

    renderProductos(filtrados);
}

// Carga las categorías en el select (basado en los productos)
function renderCategorias(productos, select) {
    const categorias = new Set();
    productos.forEach(p => {
        const cat = p.categoria || p.categoria_nombre || p.category;
        if (cat) categorias.add(cat);
    });

    // Limpiar (dejando el "Todas")
    while (select.options.length > 1) {
        select.remove(1);
    }

    Array.from(categorias).sort().forEach(cat => {
        const opt = document.createElement("option");
        opt.value = String(cat);
        opt.textContent = cat;
        select.appendChild(opt);
    });
}

// Render de tarjetas
function renderProductos(productos) {
    const grid = document.getElementById("products-grid");
    const countLabel = document.getElementById("products-count");

    grid.innerHTML = "";

    if (!productos.length) {
        grid.innerHTML = `
          <div class="alert alert-warning">
            No se encontraron productos con los filtros seleccionados.
          </div>
        `;
        if (countLabel) countLabel.textContent = "0 productos encontrados";
        return;
    }

    productos.forEach(p => {
        const card = document.createElement("div");
        card.className = "product-card";

        const imagenUrl = p.imagen_url || p.image_url || "assets/img/product-placeholder.png";
        const nombre = p.nombre || p.name || "Producto sin nombre";
        const categoria = p.categoria || p.categoria_nombre || p.category || "";
        const desc = p.descripcion_corta || p.descripcion || p.description || "";
        const precio = p.precio || p.price || null;
        const disponible = (p.estatus || p.status || "").toString().toLowerCase();

        card.innerHTML = `
          <div class="product-card__image-wrapper">
             <img class="product-card__image" src="${imagenUrl}" alt="${nombre}">
          </div>
          <div class="product-card__body">
             <div class="product-card__title">${nombre}</div>
             ${categoria ? `<div class="product-card__category">${categoria}</div>` : ""}
             ${desc ? `<div class="product-card__desc">${desc}</div>` : ""}
             <div class="product-card__price-status">
               <span class="product-card__price">
                 ${precio ? "$" + Number(precio).toFixed(2) : ""}
               </span>
               ${
                 disponible
                 ? `<span class="badge-status ${
                        (disponible.includes("agot") || disponible === "0")
                        ? "agotado"
                        : "disponible"
                    }">${disponible}</span>`
                 : ""
               }
             </div>
             <div class="product-card__actions">
               <button class="btn btn-sm btn-primary btn-ficha" data-id="${p.id}">
                 Ficha técnica (PDF)
               </button>
             </div>
          </div>
        `;

        grid.appendChild(card);
    });

    if (countLabel) {
        countLabel.textContent = `${productos.length} producto(s) encontrado(s)`;
    }

    // Asignar eventos a los botones de ficha
    grid.querySelectorAll(".btn-ficha").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");
            if (!id) return;

            try {
                // Ajusta esta ruta a como se llame tu endpoint real
                await apiDownloadPdf(`/api/utils/productos/${id}/ficha-pdf`, `producto_${id}.pdf`);
            } catch (err) {
                console.error(err);
                alert("No se pudo descargar la ficha técnica.");
            }
        });
    });
}
