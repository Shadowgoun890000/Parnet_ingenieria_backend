// frontend/assets/js/contacto.js - ACTUALIZADO

const API_BASE_URL = '';

// Elementos del DOM
const contactForm = document.getElementById('contact-form');
const contactFormMessage = document.getElementById('contact-form-message');

// ==================== ENVIAR FORMULARIO DE CONTACTO ====================

async function enviarFormularioContacto(event) {
    event.preventDefault();

    contactFormMessage.textContent = '';
    contactFormMessage.className = 'contact-form-message';

    // Validación HTML5
    if (!contactForm.checkValidity()) {
        contactFormMessage.textContent =
            'Por favor completa los campos obligatorios marcados con *.';
        contactFormMessage.classList.add('error');
        return;
    }

    // Construir payload
    const payload = {
        nombre: contactForm.nombre_contacto.value.trim(),
        email: contactForm.email_contacto.value.trim(),
        telefono: contactForm.telefono_contacto.value.trim() || null,
        asunto: contactForm.asunto.value.trim() || null,
        mensaje: contactForm.mensaje.value.trim()
    };

    try {
        const resp = await fetch(`/api/contactos/contactos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await resp.json().catch(() => ({}));

        if (!resp.ok || data.success === false) {
            const msg = data.error || data.message || 'No se pudo enviar el mensaje de contacto.';
            throw new Error(msg);
        }

        contactFormMessage.textContent =
            'Tu mensaje ha sido enviado correctamente. En breve nos pondremos en contacto contigo.';
        contactFormMessage.classList.add('success');

        contactForm.reset();
    } catch (err) {
        console.error(err);
        contactFormMessage.textContent = err.message;
        contactFormMessage.classList.add('error');
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    if (contactForm) {
        contactForm.addEventListener('submit', enviarFormularioContacto);
    }
});