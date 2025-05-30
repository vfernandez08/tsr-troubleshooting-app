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

    // Handle equipment selection buttons with better event handling
    function setupEquipmentButtons() {
        const equipmentButtons = document.querySelectorAll('.cool-equipment-btn');
        equipmentButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const target = this.dataset.target;
                const value = this.dataset.value;
                
                // Remove active class from all buttons in the same group
                const buttonGroup = this.closest('.cool-button-grid');
                if (buttonGroup) {
                    buttonGroup.querySelectorAll('.cool-equipment-btn').forEach(btn => {
                        btn.classList.remove('active');
                    });
                }
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Update the hidden input
                const hiddenInput = document.getElementById(`${target}_input`);
                if (hiddenInput) {
                    hiddenInput.value = value;
                }
                
                // Store selection
                sessionStorage.setItem(`selected_${target}`, value);
                
                // Only prevent form submission on the fiber pre-check page
                const isPreCheckForm = this.closest('#preCheckForm');
                if (isPreCheckForm) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
                
                // For other forms, allow normal submission after a brief delay
                setTimeout(() => {
                    const form = this.closest('form');
                    if (form && !isPreCheckForm) {
                        form.submit();
                    }
                }, 100);
            });
        });
        
        // Only prevent form submission for pre-check form
        const preCheckForm = document.getElementById('preCheckForm');
        if (preCheckForm) {
            preCheckForm.addEventListener('submit', function(e) {
                e.preventDefault();
                return false;
            });
        }
    }

    // Initialize button handling
    setupEquipmentButtons();

    // Restore selections on page load
    setTimeout(() => {
        document.querySelectorAll('.cool-equipment-btn').forEach(button => {
            const target = button.dataset.target;
            const savedValue = sessionStorage.getItem(`selected_${target}`);
            if (savedValue === button.dataset.value) {
                button.classList.add('active');
                const hiddenInput = document.getElementById(`${target}_input`);
                if (hiddenInput) {
                    hiddenInput.value = savedValue;
                }
            }
        });
    }, 100);

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
