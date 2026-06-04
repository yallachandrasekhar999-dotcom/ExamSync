import { authAPI, api } from './api.js';

export async function login(email, password, name = null) {
    try {
        const response = await authAPI.login(email, password, name);

        // Handle direct login (bypass OTP for admin)
        if (response.access_token) {
            api.setToken(response.access_token);

            // Get user info and store in session
            const user = await authAPI.getCurrentUser();
            if (user) {
                sessionStorage.setItem('currentUser', JSON.stringify(user));
                return { success: true, role: response.role || user.role, otp_required: false };
            }
        }

        return { success: true, otp_required: response.otp_required };
    } catch (error) {
        return { success: false, message: error.message || "Login failed" };
    }
}

export async function verifyOTP(email, otp) {
    try {
        const response = await authAPI.verifyOTP(email, otp);

        // Get user info and store in session
        const user = await authAPI.getCurrentUser();
        sessionStorage.setItem('currentUser', JSON.stringify(user));

        return { success: true, role: response.role || user.role };
    } catch (error) {
        return { success: false, message: error.message || "OTP verification failed" };
    }
}

export async function getCurrentUser() {
    // First check session storage
    const userStr = sessionStorage.getItem('currentUser');
    if (userStr) {
        return JSON.parse(userStr);
    }

    // If not in session, try to get from API
    try {
        const user = await authAPI.getCurrentUser();
        sessionStorage.setItem('currentUser', JSON.stringify(user));
        return user;
    } catch (error) {
        return null;
    }
}

export function logout(redirectUrl = 'Login.html') {
    // If called directly as an event handler, the first arg is an Event object
    if (typeof redirectUrl !== 'string' || !redirectUrl) {
        redirectUrl = 'Login.html';
    }
    authAPI.logout();
    window.location.href = redirectUrl;
}

// Redirect if not logged in (to be used in dashboards)
export async function requireAuth(allowedRoles = []) {
    const user = await getCurrentUser();

    if (!user) {
        console.warn("No authenticated user found. Redirecting to login.");
        if (allowedRoles.includes('admin')) {
            window.location.href = 'admin_login.html';
        } else {
            window.location.href = 'Login.html';
        }
        return null;
    }

    const currentRole = user.role ? user.role.toLowerCase() : '';
    const roles = allowedRoles.map(r => r.toLowerCase());

    if (roles.length > 0 && !roles.includes(currentRole)) {
        console.error(`Access Denied: Role '${currentRole}' not in allowed list [${roles.join(', ')}]`);

        if (roles.includes('admin')) {
            window.location.href = 'admin_login.html';
        } else {
            alert(`Access Denied for role: ${currentRole}`);
            window.location.href = 'Login.html';
        }
        return null;
    }

    return user;
}

export async function signup(name, username, email, password, role = 'student', semester = null, branch = null, year = null) {
    try {
        const response = await authAPI.signup(username, email, name, password, role, semester, branch, year);

        // Direct signup (no OTP) - token returned immediately
        if (response.access_token) {
            api.setToken(response.access_token);

            // Get user info and store in session
            const user = await authAPI.getCurrentUser();
            if (user) {
                sessionStorage.setItem('currentUser', JSON.stringify(user));
            }
            return { success: true, otp_required: false, role: response.role || role };
        }

        return { success: true, otp_required: response.otp_required };
    } catch (error) {
        return { success: false, message: error.message || 'Signup failed' };
    }
}
