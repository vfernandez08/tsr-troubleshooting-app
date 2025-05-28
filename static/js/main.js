// Main JavaScript for TSR Troubleshooting Guide

document.addEventListener('DOMContentLoaded', function() {

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Auto-save form data to localStorage
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        // Load saved data
        const savedValue = localStorage.getItem(`tsr_form_${input.name}`);
        if (savedValue && input.type !== 'submit' && input.type !== 'button') {
            input.value = savedValue;
        }

        // Save on change
        input.addEventListener('change', function() {
            if (this.name && this.type !== 'submit' && this.type !== 'button') {
                localStorage.setItem(`tsr_form_${this.name}`, this.value);
            }
        });
    });

    // Clear saved form data when starting new case
    const newCaseForm = document.getElementById('newCaseForm');
    if (newCaseForm) {
        newCaseForm.addEventListener('submit', function() {
            // Clear all saved form data
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('tsr_form_')) {
                    localStorage.removeItem(key);
                }
            });
        });
    }

    // Enhanced button interactions
    const optionButtons = document.querySelectorAll('.option-btn');
    optionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add loading state
            this.classList.add('loading');

            // Remove loading state after form submission
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1000);
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N for new case
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            window.location.href = '/';
        }

        // Escape to go back
        if (e.key === 'Escape' && document.querySelector('[href*="go_back"]')) {
            window.location.href = document.querySelector('[href*="go_back"]').href;
        }

        // Number keys for option selection
        if (e.key >= '1' && e.key <= '9') {
            const optionButtons = document.querySelectorAll('.option-btn');
            const index = parseInt(e.key) - 1;
            if (optionButtons[index]) {
                optionButtons[index].click();
            }
        }
    });

    // Auto-expand textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Search functionality with debouncing
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }

    // Session management disabled - using recovery system instead

    // Auto-save notes
    const notesTextarea = document.querySelector('textarea[name="notes"]');
    if (notesTextarea) {
        let saveTimeout;

        notesTextarea.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const formData = new FormData();
                formData.append('auto_save_notes', this.value);

                fetch('/auto_save_notes', {
                    method: 'POST',
                    body: formData
                }).catch(error => {
                    console.warn('Auto-save failed:', error);
                });
            }, 2000);
        });
    }

    // Print functionality
    const printButtons = document.querySelectorAll('[onclick*="print"]');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Add print-specific classes
            document.body.classList.add('printing');

            setTimeout(() => {
                window.print();
                document.body.classList.remove('printing');
            }, 100);
        });
    });

    // Confirmation dialogs for destructive actions
    const destructiveActions = document.querySelectorAll('[href*="restart"], [href*="delete"]');
    destructiveActions.forEach(action => {
        action.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to proceed? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Enhanced error handling
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);

        // Show user-friendly error message
        showErrorMessage('An unexpected error occurred. Please refresh the page and try again.');
    });

    // Network status monitoring
    window.addEventListener('online', function() {
        hideNetworkMessage();
    });

    window.addEventListener('offline', function() {
        showNetworkMessage('You are currently offline. Some features may not work properly.');
    });

});

// Utility functions
function performSearch(query) {
    const resultsDiv = document.getElementById('searchResults');

    if (query.length < 3) {
        resultsDiv.innerHTML = '';
        return;
    }

    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(results => {
            displaySearchResults(results, query);
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    Search temporarily unavailable. Please try again.
                </div>
            `;
        });
}

function displaySearchResults(results, query) {
    const resultsDiv = document.getElementById('searchResults');

    if (results.length > 0) {
        resultsDiv.innerHTML = `
            <div class="alert alert-info">
                <h6><i class="fas fa-search me-1"></i> Search Results for "${query}":</h6>
                <ul class="mb-0">
                    ${results.map(result => `
                        <li>
                            <strong>${result.step_id}:</strong> ${highlightSearchTerm(result.title, query)}
                            <span class="badge bg-secondary ms-1">${result.type}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    } else {
        resultsDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-info-circle me-1"></i>
                No results found for "${query}". Try different keywords.
            </div>
        `;
    }
}

function highlightSearchTerm(text, term) {
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showNetworkMessage(message) {
    const existingMessage = document.getElementById('networkMessage');
    if (existingMessage) {
        existingMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.id = 'networkMessage';
    messageDiv.className = 'alert alert-warning position-fixed';
    messageDiv.style.cssText = 'top: 80px; left: 50%; transform: translateX(-50%); z-index: 9998;';
    messageDiv.innerHTML = `
        <i class="fas fa-wifi me-1"></i>
        ${message}
    `;

    document.body.appendChild(messageDiv);
}

function hideNetworkMessage() {
    const messageDiv = document.getElementById('networkMessage');
    if (messageDiv) {
        messageDiv.remove();
    }
}

function showSessionExpiredModal() {
    // Popup removed - just redirect to recovery instead
    window.location.href = '/recover_session';
}

// Export for global access
window.TSRApp = {
    showErrorMessage,
    showNetworkMessage,
    hideNetworkMessage,
    performSearch
};

// Add any additional JavaScript functionality here
console.log('Main.js loaded');

// AI Troubleshooting Suggestions
document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generateAISuggestions');
    const loadingIndicator = document.getElementById('aiLoadingIndicator');
    const suggestionsContainer = document.getElementById('aiSuggestionsContainer');
    const suggestionsContent = document.getElementById('aiSuggestionsContent');
    const modelUsed = document.getElementById('aiModelUsed');

    if (generateButton) {
        generateButton.addEventListener('click', function() {
            // Show loading indicator
            loadingIndicator.style.display = 'block';
            suggestionsContainer.style.display = 'none';
            generateButton.disabled = true;

            // Collect event data from the form
            const selectedEvents = [];
            const eventCheckboxes = document.querySelectorAll('input[name="selected_events"]:checked');
            eventCheckboxes.forEach(checkbox => {
                selectedEvents.push(checkbox.value);
            });

            const channel24 = document.querySelector('input[name="channel_utilization_2_4"]')?.value || 0;
            const channel5 = document.querySelector('input[name="channel_utilization_5"]')?.value || 0;

            // Make API request
            fetch('/get_ai_troubleshooting_suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_events: selectedEvents,
                    channel_utilization_2_4: parseInt(channel24),
                    channel_utilization_5: parseInt(channel5)
                })
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = 'none';
                generateButton.disabled = false;

                if (data.success) {
                    // Format suggestions with line breaks
                    const formattedSuggestions = data.suggestions.replace(/\n/g, '<br>');
                    suggestionsContent.innerHTML = formattedSuggestions;
                    if (data.model_used) {
                        modelUsed.textContent = data.model_used;
                    }
                    suggestionsContainer.style.display = 'block';
                } else {
                    // Show fallback suggestions
                    const fallbackText = data.fallback_suggestions || 'Unable to generate suggestions at this time.';
                    suggestionsContent.innerHTML = fallbackText.replace(/\n/g, '<br>');
                    modelUsed.textContent = 'Fallback recommendations';
                    suggestionsContainer.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loadingIndicator.style.display = 'none';
                generateButton.disabled = false;

                suggestionsContent.innerHTML = 'Error generating suggestions. Please follow the standard troubleshooting steps for each selected event.';
                modelUsed.textContent = 'Error';
                suggestionsContainer.style.display = 'block';
            });
        });
    }
});

function getAITroubleshootingSuggestions() {
    const selectedEvents = Array.from(document.querySelectorAll('input[name="selected_events"]:checked')).map(cb => cb.value);
    const channel24 = document.querySelector('input[name="channel_utilization_2_4"]')?.value || 0;
    const channel5 = document.querySelector('input[name="channel_utilization_5"]')?.value || 0;

    if (selectedEvents.length === 0) {
        alert('Please select at least one event before getting AI suggestions.');
        return;
    }

    const aiButton = document.querySelector('button[onclick="getAITroubleshootingSuggestions()"]');
    if (aiButton) {
        aiButton.disabled = true;
        aiButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing Data & Generating Report...';
    }

    fetch('/get_ai_troubleshooting_suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            selected_events: selectedEvents,
            channel_utilization_2_4: parseInt(channel24),
            channel_utilization_5: parseInt(channel5)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAISuggestions(data.suggestions, data.model_used, data.data_summary);
        } else {
            displayAISuggestions(data.fallback_suggestions || 'Unable to generate suggestions at this time.', 'fallback');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayAISuggestions('Error generating AI suggestions. Please try again.', 'error');
    })
    .finally(() => {
        if (aiButton) {
            aiButton.disabled = false;
            aiButton.innerHTML = '<i class="fas fa-robot me-2"></i>Generate AI Troubleshooting Plan';
        }
    });
}

function displayAISuggestions(suggestions, modelUsed, dataSummary = '') {
    const container = document.getElementById('ai-suggestions-container');
    if (!container) return;

    const summaryHtml = dataSummary ? `
        <div class="alert alert-info mb-3">
            <i class="fas fa-chart-line me-2"></i><strong>Data Analysis:</strong> ${dataSummary}
        </div>
    ` : '';

    container.innerHTML = `
        ${summaryHtml}
        <div class="alert alert-success">
            <h6><i class="fas fa-robot me-2"></i>AI Troubleshooting Recommendations</h6>
            <div class="ai-suggestions-content">
                ${suggestions.replace(/\n/g, '<br>')}
            </div>
            <small class="text-muted mt-2 d-block">Generated by ${modelUsed}</small>
            <div class="mt-3">
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="copyToClipboard('${suggestions.replace(/'/g, "\\'")}')">
                    <i class="fas fa-copy me-1"></i>Copy Recommendations
                </button>
            </div>
        </div>
    `;

    container.style.display = 'block';
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text.replace(/<br>/g, '\n')).then(() => {
        // Show brief success message
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    });
}

// Handle AI troubleshooting suggestions button (vanilla JS instead of jQuery)
document.addEventListener('click', function(e) {
    if (e.target.matches('[name="get_ai_suggestions"]') || e.target.closest('[name="get_ai_suggestions"]')) {
        e.preventDefault();
        
        const button = e.target.matches('[name="get_ai_suggestions"]') ? e.target : e.target.closest('[name="get_ai_suggestions"]');
        const originalText = button.textContent;

        button.disabled = true;
        button.textContent = '🤖 Generating...';

        // Collect current form data (Step 3 data)
        const form = button.closest('form');
        const formData = {};

        // Get selected events
        const selectedEvents = [];
        const eventCheckboxes = form.querySelectorAll('input[name="selected_events"]:checked');
        eventCheckboxes.forEach(checkbox => {
            selectedEvents.push(checkbox.value);
        });
        formData.selected_events = selectedEvents;

        // Get channel utilization
        const channel24Input = form.querySelector('input[name="channel_utilization_2_4"]');
        const channel5Input = form.querySelector('input[name="channel_utilization_5"]');
        formData.channel_utilization_2_4 = parseInt(channel24Input?.value || 0);
        formData.channel_utilization_5 = parseInt(channel5Input?.value || 0);

        // Show loading state
        let aiContainer = document.getElementById('ai-suggestions-container');
        if (!aiContainer) {
            // Create AI suggestions container if it doesn't exist
            aiContainer = document.createElement('div');
            aiContainer.id = 'ai-suggestions-container';
            aiContainer.className = 'card mt-3';
            aiContainer.innerHTML = `
                <div class="card-header bg-info text-white">
                    <h6 class="mb-0"><i class="fas fa-robot me-2"></i>AI Troubleshooting Suggestions</h6>
                </div>
                <div class="card-body">
                    <div class="text-center">
                        <i class="fas fa-spinner fa-spin me-2"></i>Analyzing your specific WiFi environment and event data...
                    </div>
                </div>
            `;
            button.closest('.form-group').insertAdjacentElement('afterend', aiContainer);
        } else {
            aiContainer.querySelector('.card-body').innerHTML = `
                <div class="text-center">
                    <i class="fas fa-spinner fa-spin me-2"></i>Analyzing your specific WiFi environment and event data...
                </div>
            `;
        }

        fetch('/get_ai_troubleshooting_suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(response => {
            if (response.success) {
                const suggestions = response.suggestions.replace(/\n/g, '<br>');
                let debugInfo = '';
                if (response.debug_data) {
                    debugInfo = `
                        <details class="mt-2">
                            <summary class="text-muted small">Debug: Data Used by AI</summary>
                            <pre class="small mt-2">${JSON.stringify(response.debug_data, null, 2)}</pre>
                        </details>
                    `;
                }
                aiContainer.querySelector('.card-body').innerHTML = `
                    <div class="ai-suggestions-content">
                        <div class="mb-3">
                            <strong>Model Used:</strong> ${response.model_used}<br>
                            <strong>Analysis:</strong> ${response.data_summary}
                        </div>
                        <div class="suggestions-text">${suggestions}</div>
                        ${debugInfo}
                    </div>
                `;
            } else {
                aiContainer.querySelector('.card-body').innerHTML = `
                    <div class="alert alert-warning">
                        <strong>Unable to generate AI suggestions:</strong> ${response.message}<br>
                        <strong>Fallback suggestions:</strong><br>
                        ${response.fallback_suggestions}
                        ${response.debug_data ? `<details class="mt-2"><summary>Debug Data</summary><pre>${JSON.stringify(response.debug_data, null, 2)}</pre></details>` : ''}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            aiContainer.querySelector('.card-body').innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-circle me-2"></i>Error</h6>
                    <p>Failed to generate AI suggestions. Please try again.</p>
                </div>
            `;
        })
        .finally(() => {
            button.disabled = false;
            button.textContent = originalText;
        });
    }
});

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text.replace(/<br>/g, '\n')).then(() => {
        // Show brief success message
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    });
}