// Session Manager - Handles case persistence without server sessions
class SessionManager {
    constructor() {
        this.STORAGE_KEY = 'tsr_active_case';
        this.init();
    }

    init() {
        // Store case ID when it's available
        const caseIdElement = document.querySelector('[data-case-id]');
        if (caseIdElement) {
            const caseId = caseIdElement.getAttribute('data-case-id');
            this.storeCaseId(caseId);
        }

        // Check for stored case and redirect if needed
        this.checkAndRedirect();
    }

    storeCaseId(caseId) {
        if (caseId) {
            localStorage.setItem(this.STORAGE_KEY, caseId);
            localStorage.setItem(this.STORAGE_KEY + '_timestamp', Date.now());
        }
    }

    getCaseId() {
        const caseId = localStorage.getItem(this.STORAGE_KEY);
        const timestamp = localStorage.getItem(this.STORAGE_KEY + '_timestamp');
        
        if (caseId && timestamp) {
            const hoursSince = (Date.now() - parseInt(timestamp)) / (1000 * 60 * 60);
            if (hoursSince < 24) { // Valid for 24 hours
                return caseId;
            }
        }
        return null;
    }

    checkAndRedirect() {
        // If we're on a page that needs a case but don't have one in URL
        if (window.location.pathname.includes('troubleshoot') && !window.location.search.includes('case_id')) {
            const storedCaseId = this.getCaseId();
            if (storedCaseId) {
                // Redirect with case ID
                const separator = window.location.search ? '&' : '?';
                window.location.href = window.location.href + separator + 'case_id=' + storedCaseId;
            }
        }
    }

    clearCase() {
        localStorage.removeItem(this.STORAGE_KEY);
        localStorage.removeItem(this.STORAGE_KEY + '_timestamp');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    new SessionManager();
});