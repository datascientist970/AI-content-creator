// Global utility functions
function showLoading() {
    let overlay = document.querySelector('.spinner-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'spinner-overlay';
        overlay.innerHTML = '<div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>';
        document.body.appendChild(overlay);
    }
    overlay.classList.add('show');
}

function hideLoading() {
    const overlay = document.querySelector('.spinner-overlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Copy to clipboard function
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        showToast('Failed to copy', 'error');
    });
};

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.querySelector('.toast-container');
    if (container) {
        container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after hiding
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
}

// Character counter for captions
document.addEventListener('DOMContentLoaded', function() {
    const captionTextarea = document.getElementById('id_caption');
    if (captionTextarea) {
        const counter = document.createElement('small');
        counter.className = 'text-muted';
        captionTextarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const length = captionTextarea.value.length;
            counter.textContent = `${length} characters`;
            
            if (length > 2200) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        }
        
        captionTextarea.addEventListener('input', updateCounter);
        updateCounter();
    }
});

// Auto-save functionality
let autoSaveTimer;
function autoSave(formId, data) {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(function() {
        localStorage.setItem(formId, JSON.stringify(data));
        showToast('Draft saved', 'info');
    }, 2000);
}

// Form validation
(function() {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

// AJAX caption generation
window.generateCaptionAJAX = function(ideaTitle, platform, tone) {
    showLoading();
    
    fetch('/api/generate-caption/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            title: ideaTitle,
            platform: platform,
            tone: tone
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            document.getElementById('generated-caption').value = data.caption;
            document.getElementById('generated-hashtags').value = data.hashtags;
        } else {
            showToast('Error: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showToast('Error generating caption', 'danger');
    });
};

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Handle platform selection changes
document.addEventListener('DOMContentLoaded', function() {
    const platformSelect = document.getElementById('id_platform');
    if (platformSelect) {
        platformSelect.addEventListener('change', function() {
            const platform = this.value;
            const guidelines = {
                'linkedin': 'Best for professional, long-form content',
                'instagram': 'Visual-focused, use emojis and hashtags',
                'twitter': 'Concise, under 280 characters',
                'facebook': 'Community-focused, storytelling',
                'tiktok': 'Trendy, energetic, short form'
            };
            
            const helpText = document.getElementById('platform-help');
            if (helpText) {
                helpText.textContent = guidelines[platform] || '';
            }
        });
    }
});