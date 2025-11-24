// frontend/assets/js/admin_auth.js

const API_BASE_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('admin-login-form');
    const emailInput = document.getElementById('admin-email');
    const passwordInput = document.getElementById('admin-password');
    const messageBox = document.getElementById('admin-login-message');

    if (!form || !emailInput || !passwordInput || !messageBox) {
        console.error('admin_auth.js: faltan elementos en el DOM (revisa IDs en login.html)');
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Limpiar mensajes
        messageBox.textContent = '';
        messageBox.className = 'alert';
        messageBox.style.display = 'none';

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        console.log('DEBUG login -> valores formulario:', { email, password });

        if (!email || !password) {
            messageBox.textContent = 'Usuario y contraseña requeridos';
            messageBox.classList.add('alert-danger');
            messageBox.style.display = 'block';
            return;
        }

        const payload = { email, password };
        console.log('DEBUG login -> payload enviado a /api/auth/login:', payload);

        try {
            const resp = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            let data = {};
            try {
                data = await resp.json();
            } catch (e) {
                console.warn('No se pudo parsear JSON de la respuesta', e);
            }

            console.log('DEBUG login -> respuesta:', resp.status, data);

            if (!resp.ok || data.success === false) {
                const msg = data.error || data.message || 'Error al iniciar sesión';
                throw new Error(msg);
            }

            // Guardar token e info admin
            if (data.access_token) {
                localStorage.setItem('parnet_token', data.access_token);
            }
            if (data.admin) {
                localStorage.setItem('parnet_admin', JSON.stringify(data.admin));
            }

            messageBox.textContent = 'Login exitoso. Redirigiendo...';
            messageBox.classList.add('alert-success');
            messageBox.style.display = 'block';

            // 🚩 Cuando tengas dashboard, cambia esta ruta:
            // window.location.href = 'dashboard.html';

        } catch (err) {
            console.error('admin_auth -> error:', err);
            messageBox.textContent = err.message || 'Error al iniciar sesión';
            messageBox.classList.add('alert-danger');
            messageBox.style.display = 'block';
        }
    });
});
