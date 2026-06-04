/**
 * Premium Toast Notification System
 */

const createNotificationContainer = () => {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 30px;
            right: 30px;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            gap: 15px;
            pointer-events: none;
        `;
        document.body.appendChild(container);

        // Inject styles
        const style = document.createElement('style');
        style.textContent = `
            .toast-notification {
                background: #ffffff !important;
                border-left: 6px solid #7c77ff !important;
                padding: 16px 24px !important;
                border-radius: 12px !important;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2) !important;
                color: #101828 !important;
                font-weight: 700 !important;
                font-family: 'Poppins', sans-serif !important;
                font-size: 15px !important;
                min-width: 320px !important;
                max-width: 450px !important;
                display: flex !important;
                align-items: center !important;
                gap: 15px !important;
                opacity: 0 !important;
                transform: translateY(-20px) !important;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
                pointer-events: auto !important;
                border: 1px solid rgba(0,0,0,0.05) !important;
            }
            .toast-notification.success { border-left-color: #00c9a7 !important; }
            .toast-notification.error { border-left-color: #ff6b6b !important; }
            .toast-notification.warning { border-left-color: #f59e0b !important; }
            .toast-notification.info { border-left-color: #3b82f6 !important; }
            .toast-notification.show { 
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `;
        document.head.appendChild(style);
    }
    return container;
};

export const showToast = (message, type = 'success', duration = 5000) => {
    console.log(`[TOAST] ${type}: ${message}`);
    try {
        const container = createNotificationContainer();
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;

        const icons = {
            success: '<span>✅</span>',
            error: '<span>❌</span>',
            warning: '<span>⚠️</span>',
            info: '<span>ℹ️</span>'
        };

        toast.innerHTML = `${icons[type] || '<span>🔔</span>'} <span>${message}</span>`;
        container.appendChild(toast);

        // Animation
        setTimeout(() => toast.classList.add('show'), 50);

        // Auto-remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 500);
        }, duration);
    } catch (e) {
        console.error('Toast failed, falling back to alert', e);
        alert(message);
    }
};

if (typeof window !== 'undefined') {
    window.showToast = showToast;
}
