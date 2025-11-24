// frontend/assets/js/servicios.js - ACTUALIZADO

const API_BASE_URL = '';

// Elementos del DOM
const servicesListEl = document.getElementById('services-list');
const serviceSelectEl = document.getElementById('servicio_id');
const serviceForm = document.getElementById('service-request-form');
const serviceFormMessage = document.getElementById('service-form-message');

async function cargarServicios() {
    try {
        const resp = await fetch(`/api/public/servicios`);
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
    servicio_id: serviceForm.servicio_id.value,
    nombre_cliente: serviceForm.nombre_cliente.value.trim(),  // ← Coincide con el modelo
    email: serviceForm.email.value.trim(),                    // ← Coincide con el modelo
    telefono: serviceForm.telefono.value.trim(),              // ← Coincide con el modelo
    empresa: serviceForm.empresa.value.trim(),
    mensaje: serviceForm.mensaje.value.trim()                 // ← Coincide con el modelo
};

    try {
        const resp = await fetch(`/api/servicios/solicitudes`, {
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

        // Limpiar formulario
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