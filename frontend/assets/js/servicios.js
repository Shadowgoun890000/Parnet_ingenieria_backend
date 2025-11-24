// Ajusta esto si sirves el backend en otra URL/puerto
const API_BASE_URL = 'http://127.0.0.1:5000';

// Elementos del DOM
const servicesListEl = document.getElementById('services-list');
const serviceSelectEl = document.getElementById('servicio_id');
const serviceForm = document.getElementById('service-request-form');
const serviceFormMessage = document.getElementById('service-form-message');

async function cargarServicios() {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/public/servicios`);
        if (!resp.ok) {
            throw new Error('No se pudo obtener el catálogo de servicios');
        }

        const data = await resp.json();

        const servicios = Array.isArray(data)
            ? data
            : (data.servicios || []);

        // Limpiar DOM
        servicesListEl.innerHTML = '';
        serviceSelectEl.innerHTML =
            '<option value="">Selecciona un servicio...</option>';

        if (!servicios.length) {
            servicesListEl.innerHTML =
                '<p class="small text-muted">No hay servicios registrados por el momento.</p>';
            return;
        }

        servicios.forEach(servicio => {
            const id = servicio.id || servicio.servicio_id;
            const nombre = servicio.nombre || servicio.nombre_servicio || 'Servicio';
            const area = servicio.area || servicio.area_servicio || '';
            const descripcion = servicio.descripcion || servicio.descripcion_corta || servicio.detalle || '';

            // Tarjeta en el panel de servicios
            const card = document.createElement('div');
            card.className = 'service-card';

            card.innerHTML = `
                <div class="service-card__title">${nombre}</div>
                ${area ? `<div class="service-card__area">Área: ${area}</div>` : ''}
                ${descripcion ? `<div class="service-card__desc">${descripcion}</div>` : ''}
            `;

            servicesListEl.appendChild(card);

            // Opción en el select del formulario
            if (id) {
                const opt = document.createElement('option');
                opt.value = id;
                opt.textContent = nombre + (area ? ` - ${area}` : '');
                serviceSelectEl.appendChild(opt);
            }
        });

    } catch (err) {
        console.error(err);
        servicesListEl.innerHTML =
            '<p class="services-form-message error">Ocurrió un error al cargar los servicios.</p>';
    }
}

function validarCaptcha() {
    const valor = document.getElementById('captcha_respuesta').value.trim();
    return valor === '7';
}

async function enviarSolicitudServicio(event) {
    event.preventDefault();
    serviceFormMessage.textContent = '';
    serviceFormMessage.className = 'services-form-message';

    // Validación básica
    if (!serviceForm.checkValidity()) {
        serviceFormMessage.textContent =
            'Por favor completa todos los campos obligatorios marcados con *.';
        serviceFormMessage.classList.add('error');
        return;
    }

    // Validar captcha
    if (!validarCaptcha()) {
        serviceFormMessage.textContent = 'Captcha incorrecto. Inténtalo de nuevo.';
        serviceFormMessage.classList.add('error');
        return;
    }

    const payload = {
        // Estos nombres pueden ajustarse a lo que espere tu backend
        nombre_contacto: serviceForm.nombre_contacto.value.trim(),
        empresa: serviceForm.empresa.value.trim(),
        email_contacto: serviceForm.email_contacto.value.trim(),
        telefono_contacto: serviceForm.telefono_contacto.value.trim(),
        servicio_id: serviceForm.servicio_id.value,
        area_servicio: serviceForm.area_servicio.value.trim(),
        detalle: serviceForm.detalle.value.trim()
    };

    try {
        const resp = await fetch(`${API_BASE_URL}/api/servicios/solicitudes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await resp.json().catch(() => ({}));

        if (!resp.ok || data.success === false) {
            const msg = data.error || data.message || 'No se pudo registrar la solicitud.';
            throw new Error(msg);
        }

        serviceFormMessage.textContent =
            'Tu solicitud de servicio se ha enviado correctamente. En breve nos pondremos en contacto contigo.';
        serviceFormMessage.classList.add('success');

        // Limpiar formulario (excepto captcha si quieres)
        serviceForm.reset();

    } catch (err) {
        console.error(err);
        serviceFormMessage.textContent = err.message;
        serviceFormMessage.classList.add('error');
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    cargarServicios();
    serviceForm.addEventListener('submit', enviarSolicitudServicio);
});
