// API Configuration
const API_BASE_URL = (typeof window !== 'undefined' && window.location && window.location.origin && window.location.origin.includes(':8000'))
    ? window.location.origin
    : 'http://localhost:8000';
// API Client Class
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    // Get auth token from localStorage
    getToken() {
        return localStorage.getItem('access_token');
    }

    // Set auth token
    setToken(token) {
        localStorage.setItem('access_token', token);
    }

    // Remove auth token
    removeToken() {
        localStorage.removeItem('access_token');
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = this.getToken();

        const headers = {
            ...options.headers,
        };

        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers,
        };

        try {
            console.log('[API]', config.method || 'GET', url);
            const response = await fetch(url, config);

            // Handle non-JSON responses
            const contentType = response.headers.get('content-type');
            let data;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const message = (data && (data.detail || data.message)) ? (data.detail || data.message) : 'Request failed';
                throw new Error(`${message} (HTTP ${response.status}) for ${url}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Create and export API client instance
export const api = new APIClient(API_BASE_URL);

// Auth API
export const authAPI = {
    async signup(username, email, name, password, role, semester = null, branch = null, year = null) {
        const response = await api.post('/api/auth/signup', {
            username,
            email,
            name,
            password,
            role,
            semester: semester ? parseInt(semester) : null,
            branch,
            year: year ? parseInt(year) : null
        });
        return response;
    },

    async login(email, password, name = null) {
        // Step 1: Verify credentials and trigger OTP
        return await api.post('/api/auth/login', {
            email,
            password,
            name
        });
    },

    async requestOTP(email) {
        return await api.post('/api/auth/request-otp', { email });
    },

    async verifyOTP(email, otp) {
        const response = await api.post('/api/auth/verify-otp', {
            email,
            otp
        });
        if (response.access_token) {
            api.setToken(response.access_token);
        }
        return response;
    },

    async getCurrentUser() {
        return await api.get('/api/auth/me');
    },

    async forgotPassword(email, name = null) {
        return await api.post('/api/auth/forgot-password', { email, name });
    },

    async resetPassword(token, new_password) {
        return await api.post('/api/auth/reset-password', { token, new_password });
    },

    async updateMyProfile(data) {
        return await api.put('/api/users/me/profile', data);
    },

    logout() {
        api.removeToken();
        sessionStorage.removeItem('currentUser');
    }
};

// Users API
export const usersAPI = {
    async listUsers(role = null) {
        const endpoint = role ? `/api/users/?role=${role}` : '/api/users/';
        return await api.get(endpoint);
    },

    async getUser(userId) {
        return await api.get(`/api/users/${userId}`);
    },

    async createUser(userData) {
        return await api.post('/api/users/', userData);
    },

    async updateUser(userId, userData) {
        return await api.put(`/api/users/${userId}`, userData);
    },

    async deleteUser(userId) {
        return await api.delete(`/api/users/${userId}`);
    },

    async assignSubjects(userId, subjectIds) {
        return await api.put(`/api/users/${userId}/subjects`, subjectIds);
    },

    async getAssignedSubjects() {
        return await api.get('/api/users/me/subjects');
    }
};

// Curriculum API
export const curriculumAPI = {
    async getAllYears() {
        return await api.get('/api/curriculum/years');
    },

    async getSubjects(branch, semester) {
        return await api.get(`/api/curriculum/subjects?branch=${encodeURIComponent(branch)}&semester=${semester}`);
    },

    async getSemesterSubjects(semesterId) {
        return await api.get(`/api/curriculum/semesters/${semesterId}/subjects`);
    },

    async getMyCurriculum() {
        const response = await api.get('/api/curriculum/my-curriculum');
        return response;
    },

    async createSubject(subjectData) {
        return await api.post('/api/curriculum/subjects', subjectData);
    },

    async updateSubject(subjectId, subjectData) {
        return await api.put(`/api/curriculum/subjects/${subjectId}`, subjectData);
    },

    async deleteSubject(subjectId) {
        return await api.delete(`/api/curriculum/subjects/${subjectId}`);
    }
};

// Content API
export const contentAPI = {
    async getSubjectContent(subjectId, authorId = null) {
        let url = `/api/content/subjects/${subjectId}`;
        if (authorId) url += `?author_id=${authorId}`;
        return await api.get(url);
    },

    async getSubjectAuthors(subjectId) {
        return await api.get(`/api/content/subjects/${subjectId}/authors`);
    },

    // Course Outcomes
    async addCourseOutcome(subjectId, outcomeText, order, coNo = null, unit = null) {
        const formData = new FormData();
        formData.append('outcome_text', outcomeText);
        formData.append('order', order);
        if (coNo) formData.append('co_no', coNo);
        if (unit) formData.append('unit', unit);

        return await api.request(`/api/content/subjects/${subjectId}/cos`, {
            method: 'POST',
            body: formData
        });
    },

    async deleteCourseOutcome(coId) {
        return await api.delete(`/api/content/cos/${coId}`);
    },

    // PYQs
    async addPYQ(subjectId, name, year, link = null, file = null) {
        const formData = new FormData();
        if (name) formData.append('name', name);
        if (year) formData.append('year', year);
        if (link) formData.append('link', link);
        if (file) formData.append('file', file);

        return await api.request(`/api/content/subjects/${subjectId}/pyqs`, {
            method: 'POST',
            body: formData
        });
    },

    async deletePYQ(pyqId) {
        return await api.delete(`/api/content/pyqs/${pyqId}`);
    },

    // Important Questions
    async addImportantQuestion(subjectId, questionText, marks, unit = null, topic = null, file = null) {
        const formData = new FormData();
        formData.append('question_text', questionText);
        formData.append('marks', marks);
        if (unit) formData.append('unit', unit);
        if (topic) formData.append('topic', topic);
        if (file) formData.append('file', file);

        return await api.request(`/api/content/subjects/${subjectId}/questions`, {
            method: 'POST',
            body: formData
        });
    },

    async deleteImportantQuestion(questionId) {
        return await api.delete(`/api/content/questions/${questionId}`);
    },

    // Roadmap Steps
    async addRoadmapStep(subjectId, stepNumber, title, description = "", file = null) {
        const formData = new FormData();
        formData.append('step_number', stepNumber);
        formData.append('title', title);
        formData.append('description', description);
        if (file) formData.append('file', file);

        return await api.request(`/api/content/subjects/${subjectId}/roadmap`, {
            method: 'POST',
            body: formData
        });
    },

    async deleteRoadmapStep(stepId) {
        return await api.delete(`/api/content/roadmap/${stepId}`);
    },

    // Notes
    async addNote(subjectId, title, file) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('file', file);

        return await api.request(`/api/content/subjects/${subjectId}/notes`, {
            method: 'POST',
            body: formData
        });
    },

    async deleteNote(noteId) {
        return await api.delete(`/api/content/notes/${noteId}`);
    },

    // Doubt Sessions
    async addDoubtSession(subjectId, title, date, timeFrom, timeTo, zoomLink) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('date', date);
        formData.append('time_from', timeFrom);
        formData.append('time_to', timeTo);
        formData.append('zoom_link', zoomLink);

        return await api.request(`/api/content/subjects/${subjectId}/doubt_sessions`, {
            method: 'POST',
            body: formData
        });
    },

    async deleteDoubtSession(sessionId) {
        return await api.delete(`/api/content/doubt_sessions/${sessionId}`);
    },

    // Reference Videos
    async addReferenceVideo(subjectId, unit, topic, videoLink) {
        const formData = new FormData();
        if (unit) formData.append('unit', unit);
        formData.append('topic', topic);
        formData.append('video_link', videoLink);

        return await api.request(`/api/content/subjects/${subjectId}/videos`, {
            method: 'POST',
            body: formData
        });
    },

    async deleteReferenceVideo(videoId) {
        return await api.delete(`/api/content/videos/${videoId}`);
    }
};
