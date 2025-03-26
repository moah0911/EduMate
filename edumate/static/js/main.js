// Common utility functions
const edumate = {
    // Initialize tooltips and popovers
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Format dates
    formatDate: function(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('en-US', options);
    },
    
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Show toast notification
    showToast: function(message, type = 'success') {
        const toastEl = document.createElement('div');
        toastEl.className = 'toast';
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="toast-header">
                <i class="bi bi-${type === 'success' ? 'check-circle-fill text-success' : 'exclamation-circle-fill text-danger'} me-2"></i>
                <strong class="me-auto">${type === 'success' ? 'Success' : 'Error'}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;
        
        const container = document.querySelector('.toast-container');
        container.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove toast after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    },
    
    // Handle form submission with file uploads
    submitFormWithFiles: async function(form, url, method = 'POST') {
        try {
            const response = await fetch(url, {
                method: method,
                body: new FormData(form)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'An error occurred');
            }
            
            return data;
        } catch (error) {
            console.error('Form submission error:', error);
            throw error;
        }
    },
    
    // Initialize code editor
    initCodeEditor: function(elementId, language = 'python') {
        if (!document.getElementById(elementId)) return null;
        
        const editor = ace.edit(elementId);
        editor.setTheme('ace/theme/monokai');
        editor.session.setMode(`ace/mode/${language}`);
        editor.setOptions({
            fontSize: '14px',
            showPrintMargin: false,
            showGutter: true,
            highlightActiveLine: true,
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true,
            enableSnippets: true
        });
        
        return editor;
    },
    
    // Handle file preview
    handleFilePreview: function(input, previewContainer) {
        const container = document.getElementById(previewContainer);
        if (!container) return;
        
        container.innerHTML = '';
        const files = input.files;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const icon = document.createElement('i');
            icon.className = `bi bi-file-earmark me-2 ${this.getFileIcon(file.type)}`;
            
            const name = document.createElement('span');
            name.className = 'me-auto';
            name.textContent = file.name;
            
            const size = document.createElement('small');
            size.className = 'text-muted ms-2';
            size.textContent = this.formatFileSize(file.size);
            
            fileItem.appendChild(icon);
            fileItem.appendChild(name);
            fileItem.appendChild(size);
            container.appendChild(fileItem);
        }
    },
    
    // Get appropriate file icon based on mime type
    getFileIcon: function(mimeType) {
        if (mimeType.startsWith('image/')) return 'bi-file-image';
        if (mimeType.startsWith('video/')) return 'bi-file-play';
        if (mimeType.startsWith('audio/')) return 'bi-file-music';
        if (mimeType.includes('pdf')) return 'bi-file-pdf';
        if (mimeType.includes('word')) return 'bi-file-word';
        if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'bi-file-excel';
        if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return 'bi-file-ppt';
        if (mimeType.includes('zip') || mimeType.includes('compressed')) return 'bi-file-zip';
        return 'bi-file-text';
    },
    
    // Handle quiz interactions
    handleQuizOptions: function() {
        document.querySelectorAll('.quiz-options .list-group-item').forEach(item => {
            item.addEventListener('click', function() {
                const input = this.querySelector('input[type="radio"]');
                if (input) {
                    input.checked = true;
                    
                    // Remove selected class from siblings
                    this.closest('.quiz-options').querySelectorAll('.list-group-item').forEach(sibling => {
                        sibling.classList.remove('selected');
                    });
                    
                    // Add selected class to clicked item
                    this.classList.add('selected');
                }
            });
        });
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    edumate.initTooltips();
    edumate.handleQuizOptions();
}); 