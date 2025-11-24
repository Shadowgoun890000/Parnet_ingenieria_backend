// frontend/assets/js/noticias.js - ACTUALIZADO

const API_BASE_URL = '';

// Elementos del DOM
const newsListEl = document.getElementById('lista-noticias');
const newsPaginationEl = document.getElementById('paginacion-noticias');
const newsDetailEl = document.getElementById('detalle-noticia');
const newsDetailTitleEl = newsDetailEl?.querySelector('.news-detail-title');
const newsDetailMetaEl = newsDetailEl?.querySelector('.news-detail-meta');
const newsDetailBodyEl = newsDetailEl?.querySelector('.news-detail-body');
const recentNewsListEl = document.getElementById('noticias-recientes');

// Estado de paginación
let currentPage = 1;
let perPage = 5;
let totalNoticias = 0;
let totalPages = 1;

// ==================== UTILIDADES ====================

function formatearFecha(fechaRaw) {
    if (!fechaRaw) return '';
    // Intentar parsear la fecha
    const fecha = new Date(fechaRaw);
    if (isNaN(fecha.getTime())) return fechaRaw;

    return fecha.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: '2-digit'
    });
}

// ==================== CARGAR NOTICIAS (LISTA) ====================

async function cargarNoticias() {
    if (!newsListEl) return;

    try {
        newsListEl.innerHTML =
            '<p class="small text-muted">Cargando noticias...</p>';
        newsPaginationEl.innerHTML = '';
        ocultarDetalleNoticia();

        const params = new URLSearchParams();
        params.set('page', String(currentPage));
        params.set('per_page', String(perPage));

        const resp = await fetch(`/api/public/noticias?${params.toString()}`);

        if (!resp.ok) {
            throw new Error('No se pudo obtener el tablero de noticias');
        }

        const data = await resp.json();

        if (data.success === false) {
            throw new Error(data.error || 'Error en la respuesta del servidor');
        }

        const noticias = data.noticias || [];
        totalNoticias = data.total || noticias.length;
        totalPages = data.pages || 1;
        currentPage = data.current_page || 1;

        renderNoticias(noticias);
        renderPaginacionNoticias();
    } catch (err) {
        console.error(err);
        newsListEl.innerHTML =
            `<p class="small text-danger">Ocurrió un error al cargar las noticias: ${err.message}</p>`;
    }
}

function renderNoticias(noticias) {
    if (!noticias.length) {
        newsListEl.innerHTML =
            '<p class="small text-muted">No hay noticias registradas.</p>';
        return;
    }

    newsListEl.innerHTML = '';

    noticias.forEach(n => {
        // Intentar adaptarnos a los posibles nombres que use tu modelo
        const id = n.id;
        const titulo = n.titulo || n.titulo_noticia || 'Noticia';
        const resumen =
            n.resumen ||
            n.descripcion ||
            (n.contenido && n.contenido.slice(0, 180) + '...') ||
            '';
        const fechaPub = n.fecha_publicacion || n.fecha || null;
        const visitas = n.visitas || 0;
        const autor = n.autor || n.creado_por || '';

        const card = document.createElement('article');
        card.className = 'news-card';
        card.dataset.noticiaId = id;

        card.innerHTML = `
            <h3 class="news-card-title">${titulo}</h3>
            <div class="news-card-meta small text-muted">
                ${fechaPub ? formatearFecha(fechaPub) : ''}
                ${autor ? ` &mdash; ${autor}` : ''}
                ${visitas ? ` &mdash; ${visitas} visita(s)` : ''}
            </div>
            ${
                resumen
                    ? `<p class="news-card-summary">${resumen}</p>`
                    : ''
            }
            <button type="button"
                    class="btn btn-link btn-sm p-0 news-card-link">
                Leer más...
            </button>
        `;

        newsListEl.appendChild(card);
    });

    // Delegación para "Leer más..."
    newsListEl.addEventListener(
        'click',
        event => {
            const btn = event.target.closest('.news-card-link');
            if (!btn) return;

            const card = btn.closest('.news-card');
            if (!card) return;

            const noticiaId = card.dataset.noticiaId;
            if (!noticiaId) return;

            cargarDetalleNoticia(noticiaId);
        },
        { once: true }
    );
}

// ==================== PAGINACIÓN ====================

function renderPaginacionNoticias() {
    if (!newsPaginationEl) return;

    newsPaginationEl.innerHTML = '';

    if (totalPages <= 1) return;

    const createBtn = (page, label = null, disabled = false, active = false) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-light news-page-btn';
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
    newsPaginationEl.appendChild(btnPrev);

    // Páginas
    for (let p = 1; p <= totalPages; p++) {
        const btn = createBtn(
            p,
            String(p),
            false,
            p === currentPage
        );
        newsPaginationEl.appendChild(btn);
    }

    // Siguiente
    const btnNext = createBtn(
        currentPage + 1,
        '»',
        currentPage === totalPages
    );
    newsPaginationEl.appendChild(btnNext);

    newsPaginationEl.addEventListener(
        'click',
        event => {
            const btn = event.target.closest('.news-page-btn');
            if (!btn) return;

            const page = Number(btn.dataset.page);
            if (!page || page === currentPage) return;

            currentPage = page;
            cargarNoticias();
        },
        { once: true }
    );
}

// ==================== DETALLE DE NOTICIA ====================

function ocultarDetalleNoticia() {
    if (!newsDetailEl) return;
    newsDetailEl.classList.add('d-none');
    if (newsDetailTitleEl) newsDetailTitleEl.textContent = '';
    if (newsDetailMetaEl) newsDetailMetaEl.textContent = '';
    if (newsDetailBodyEl) newsDetailBodyEl.innerHTML = '';
}

async function cargarDetalleNoticia(noticiaId) {
    if (!newsDetailEl) return;

    try {
        newsDetailEl.classList.remove('d-none');
        if (newsDetailTitleEl) newsDetailTitleEl.textContent = 'Cargando...';
        if (newsDetailMetaEl) newsDetailMetaEl.textContent = '';
        if (newsDetailBodyEl) newsDetailBodyEl.innerHTML = '';

        const resp = await fetch(`/api/public/noticias/${noticiaId}`);

        if (!resp.ok) {
            throw new Error('No se pudo obtener el detalle de la noticia');
        }

        const data = await resp.json();

        if (data.success === false) {
            throw new Error(data.error || 'Error en la respuesta del servidor');
        }

        const n = data.noticia || data;

        const titulo = n.titulo || n.titulo_noticia || 'Noticia';
        const fechaPub = n.fecha_publicacion || n.fecha || null;
        const visitas = n.visitas || 0;
        const autor = n.autor || n.creado_por || '';
        const contenido =
            n.contenido ||
            n.cuerpo ||
            n.detalle ||
            n.descripcion ||
            '';

        if (newsDetailTitleEl) newsDetailTitleEl.textContent = titulo;

        const metaPieces = [];
        if (fechaPub) metaPieces.push(formatearFecha(fechaPub));
        if (autor) metaPieces.push(autor);
        if (visitas) metaPieces.push(`${visitas} visita(s)`);

        if (newsDetailMetaEl) {
            newsDetailMetaEl.innerHTML = metaPieces.join(' &mdash; ');
        }

        if (newsDetailBodyEl) {
            // Si el backend devuelve HTML, lo mostramos tal cual
            newsDetailBodyEl.innerHTML = contenido;
        }
    } catch (err) {
        console.error(err);
        if (newsDetailTitleEl) {
            newsDetailTitleEl.textContent = 'Error al cargar la noticia';
        }
        if (newsDetailBodyEl) {
            newsDetailBodyEl.innerHTML =
                `<p class="text-danger small">${err.message}</p>`;
        }
    }
}

// ==================== NOTICIAS RECIENTES (SIDEBAR) ====================

async function cargarNoticiasRecientes() {
    if (!recentNewsListEl) return;

    try {
        recentNewsListEl.innerHTML =
            '<li class="small text-muted">Cargando...</li>';

        const resp = await fetch(`/api/public/noticias/recientes?limit=3`);

        if (!resp.ok) {
            throw new Error('No se pudo obtener las noticias recientes');
        }

        const data = await resp.json();

        if (data.success === false) {
            throw new Error(data.error || 'Error en la respuesta del servidor');
        }

        const noticias = data.noticias || [];

        if (!noticias.length) {
            recentNewsListEl.innerHTML =
                '<li class="small text-muted">No hay noticias recientes.</li>';
            return;
        }

        recentNewsListEl.innerHTML = '';

        noticias.forEach(n => {
            const id = n.id;
            const titulo = n.titulo || n.titulo_noticia || 'Noticia';
            const fechaPub = n.fecha_publicacion || n.fecha || null;

            const li = document.createElement('li');
            li.className = 'news-recent-item';
            li.dataset.noticiaId = id;

            li.innerHTML = `
                <a href="#" class="news-recent-link">
                    <div class="news-recent-title">${titulo}</div>
                    ${
                        fechaPub
                            ? `<div class="news-recent-date small text-muted">
                                   ${formatearFecha(fechaPub)}
                               </div>`
                            : ''
                    }
                </a>
            `;

            recentNewsListEl.appendChild(li);
        });

        // Click en noticia reciente → muestra detalle
        recentNewsListEl.addEventListener(
            'click',
            event => {
                const link = event.target.closest('.news-recent-link');
                if (!link) return;

                event.preventDefault();

                const li = link.closest('.news-recent-item');
                if (!li) return;

                const id = li.dataset.noticiaId;
                if (!id) return;

                cargarDetalleNoticia(id);
            },
            { once: true }
        );
    } catch (err) {
        console.error(err);
        recentNewsListEl.innerHTML =
            `<li class="small text-danger">Error al cargar noticias recientes: ${err.message}</li>`;
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    if (newsListEl) {
        cargarNoticias();
    }
    if (recentNewsListEl) {
        cargarNoticiasRecientes();
    }
});