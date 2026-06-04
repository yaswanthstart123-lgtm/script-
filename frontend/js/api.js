const API_BASE_URL = '/api';

class ApiClient {
    static getToken() {
        return localStorage.getItem('securehub_token');
    }

    static setToken(token) {
        localStorage.setItem('securehub_token', token);
    }

    static removeToken() {
        localStorage.removeItem('securehub_token');
    }

    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json().catch(() => null);

            if (!response.ok) {
                // If unauthorized and not on login page, redirect to login
                if (response.status === 401 && !window.location.pathname.includes('index.html')) {
                    this.removeToken();
                    window.location.href = 'index.html';
                }
                throw new Error(data?.detail || response.statusText || 'An error occurred');
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    static get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    static post(endpoint, body) {
        return this.request(endpoint, { method: 'POST', body });
    }

    static put(endpoint, body) {
        return this.request(endpoint, { method: 'PUT', body });
    }
}

function logout() {
    ApiClient.post('/auth/logout').finally(() => {
        ApiClient.removeToken();
        window.location.href = 'index.html';
    });
}
