// ARGUS IA - Dashboard JavaScript

class ArgusDashboard {
    constructor() {
        this.initEventListeners();
        this.initCharts();
    }

    initEventListeners() {
        // Tooltip initialization
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Auto-dismiss alerts after 5 seconds
        this.autoDismissAlerts();
    }

    initCharts() {
        // Initialize any charts if needed
        const chartElements = document.querySelectorAll('.chart-container');
        if (chartElements.length > 0) {
            this.createAnalysisCharts();
        }
    }

    createAnalysisCharts() {
        // Placeholder for chart creation
        // Can be extended with Chart.js for visual analytics
        console.log('Charts initialized');
    }

    autoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentElement) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        });
    }

    // Utility function for API calls
    async apiCall(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Show loading state
    showLoading(element) {
        element.disabled = true;
        const originalHTML = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        return originalHTML;
    }

    // Hide loading state
    hideLoading(element, originalHTML) {
        element.disabled = false;
        element.innerHTML = originalHTML;
    }

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(notification, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Format numbers with commas
    formatNumber(number) {
        return new Intl.NumberFormat('pt-BR').format(number);
    }

    // Format percentages
    formatPercentage(number, decimals = 2) {
        return `${number.toFixed(decimals)}%`;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.argusDashboard = new ArgusDashboard();
});

// Utility functions for the detection system
const DetectionUtils = {
    // Risk assessment based on probability
    assessRisk(probability) {
        if (probability > 0.8) return { level: 'high', color: 'danger', text: 'Alto Risco' };
        if (probability > 0.6) return { level: 'medium', color: 'warning', text: 'Risco Médio' };
        if (probability > 0.4) return { level: 'low', color: 'info', text: 'Baixo Risco' };
        return { level: 'safe', color: 'success', text: 'Seguro' };
    },

    // Pattern analysis
    analyzePatterns(patterns) {
        const patternCounts = {};
        patterns.forEach(pattern => {
            patternCounts[pattern] = (patternCounts[pattern] || 0) + 1;
        });
        return patternCounts;
    },

    // Generate risk report
    generateRiskReport(analysisData) {
        const report = {
            summary: {
                totalComments: analysisData.total_comments,
                suspiciousCount: analysisData.suspicious_count,
                detectionRate: analysisData.suspicious_percentage,
                accuracy: analysisData.accuracy
            },
            risks: this.assessRisk(analysisData.suspicious_percentage / 100),
            timestamp: new Date().toISOString()
        };
        return report;
    }
};