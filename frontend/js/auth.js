document.addEventListener('DOMContentLoaded', () => {
    // Redirect if already logged in
    if (ApiClient.getToken()) {
        window.location.href = 'dashboard.html';
        return;
    }

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorDiv = document.getElementById('login-error');

        try {
            const btn = loginForm.querySelector('button');
            btn.disabled = true;
            btn.innerText = 'Logging in...';
            errorDiv.innerText = '';
            
            const res = await ApiClient.post('/auth/login', { email, password });
            ApiClient.setToken(res.access_token);
            window.location.href = 'dashboard.html';
        } catch (err) {
            errorDiv.innerText = err.message;
        } finally {
            const btn = loginForm.querySelector('button');
            btn.disabled = false;
            btn.innerText = 'Login';
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const role = document.getElementById('reg-role').value;
        const errorDiv = document.getElementById('reg-error');
        const successDiv = document.getElementById('reg-success');

        try {
            const btn = registerForm.querySelector('button');
            btn.disabled = true;
            btn.innerText = 'Creating...';
            errorDiv.innerText = '';
            successDiv.innerText = '';

            const res = await ApiClient.post('/auth/register', { email, password, role });
            ApiClient.setToken(res.access_token);
            successDiv.innerText = 'Account created successfully! Redirecting...';
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } catch (err) {
            errorDiv.innerText = err.message;
        } finally {
            const btn = registerForm.querySelector('button');
            btn.disabled = false;
            btn.innerText = 'Create Account';
        }
    });
});
