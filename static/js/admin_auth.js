// frontend/assets/js/admin_auth.js - ACTUALIZADO

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('admin-login-form');
    const emailInput = document.getElementById('admin-email');
    const passwordInput = document.getElementById('admin-password');
    const messageBox = document.getElementById('admin-login-message');

    if (!form || !emailInput || !passwordInput || !messageBox) {
        console.error('Elementos del formulario no encontrados');
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

        if (!email || !password) {
            showMessage('Usuario y contraseña requeridos', 'error');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Error al iniciar sesión');
            }

            // Guardar token e info admin
            if (data.access_token) {
                localStorage.setItem('parnet_token', data.access_token);
            }
            if (data.admin) {
                localStorage.setItem('parnet_admin', JSON.stringify(data.admin));
            }

            showMessage('✅ Login exitoso. Redirigiendo...', 'success');
            
            // Redirigir al dashboard (crear dashboard.html después)
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);

        } catch (error) {
            console.error('Login error:', error);
            showMessage(error.message || 'Error al iniciar sesión', 'error');
        }
    });

    function showMessage(message, type) {
        messageBox.textContent = message;
        messageBox.className = `alert alert-${type === 'error' ? 'danger' : 'success'}`;
        messageBox.style.display = 'block';
    }
});