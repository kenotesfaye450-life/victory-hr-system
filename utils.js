// Victory Water & Happy Juice - Utility Functions

// Toast notification system
function showMessage(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    }[type] || 'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Modal management
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    }
}

// Custom confirmation modal
function showConfirmModal(message, onConfirm, onCancel) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('customConfirmModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'customConfirmModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h2 class="modal-title">Confirm Action</h2>
                </div>
                <div style="padding: 1.5rem;">
                    <p id="confirmMessage" style="margin-bottom: 2rem; color: var(--dark);"></p>
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button class="btn btn-secondary" id="confirmCancelBtn">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                        <button class="btn btn-danger" id="confirmOkBtn">
                            <i class="fas fa-check"></i> Yes, proceed
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    const messageEl = document.getElementById('confirmMessage');
    const okBtn = document.getElementById('confirmOkBtn');
    const cancelBtn = document.getElementById('confirmCancelBtn');
    
    messageEl.textContent = message;
    
    // Remove old event listeners by cloning
    const newOkBtn = okBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    okBtn.parentNode.replaceChild(newOkBtn, okBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    // Add new event listeners
    newOkBtn.addEventListener('click', () => {
        closeModal('customConfirmModal');
        if (onConfirm) onConfirm();
    });
    
    newCancelBtn.addEventListener('click', () => {
        closeModal('customConfirmModal');
        if (onCancel) onCancel();
    });
    
    openModal('customConfirmModal');
}

// Tab switching
function switchTab(tabName, group = 'main') {
    // Hide all tab contents in this group
    document.querySelectorAll(`.tab-content[data-group="${group}"]`).forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs in this group
    document.querySelectorAll(`.tab[data-group="${group}"]`).forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedContent = document.getElementById(`${tabName}-tab`);
    if (selectedContent) {
        selectedContent.classList.add('active');
    }
    
    // Activate selected tab button
    const selectedTab = document.querySelector(`.tab[data-tab="${tabName}"][data-group="${group}"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

// Table rendering helper
function renderTable(tableId, data, columns, actions = null) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = columns.length + (actions ? 1 : 0);
        td.textContent = 'No data available';
        td.style.textAlign = 'center';
        td.style.color = '#7f8c8d';
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
    }
    
    data.forEach((row, index) => {
        const tr = document.createElement('tr');
        
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col.field] || '';
            tr.appendChild(td);
        });
        
        if (actions) {
            const td = document.createElement('td');
            td.innerHTML = actions(row, index);
            tr.appendChild(td);
        }
        
        tbody.appendChild(tr);
    });
}

// Date formatting - supports Ethiopian/Gregorian toggle
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

// Format display date based on Ethiopian/Gregorian preference
function formatDisplayDate(gregDate, ethDate) {
    // This function will be overridden by index.html if needed
    // Default to Gregorian if not overridden
    if (window.useEthiopian && ethDate) {
        return formatEthiopianDate(ethDate);
    }
    return formatDate(gregDate);
}

// Format Ethiopian date string for display
function formatEthiopianDate(ethDateStr) {
    if (!ethDateStr) return '';
    // Ethiopian date is in format YYYY-MM-DD
    const parts = ethDateStr.split('-');
    if (parts.length !== 3) return ethDateStr;
    return `${parts[2]}/${parts[1]}/${parts[0]}`; // DD/MM/YYYY format
}

// Time formatting
function formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

// Date-time formatting
function formatDateTime(timestamp) {
    if (!timestamp) return '';
    return `${formatDate(timestamp)} ${formatTime(timestamp)}`;
}

// Currency formatting
function formatCurrency(amount) {
    return `${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ETB`;
}

// Get current date in YYYY-MM-DD format
function getCurrentDate() {
    return new Date().toISOString().split('T')[0];
}

// Get current ISO timestamp
function getCurrentTimestamp() {
    return new Date().toISOString();
}

// Validate email format
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Calculate hours worked between check-in and check-out
function calculateHoursWorked(checkInTimestamp, checkOutTimestamp) {
    if (!checkInTimestamp || !checkOutTimestamp) return '';
    const checkIn = new Date(checkInTimestamp);
    const checkOut = new Date(checkOutTimestamp);
    const diffMs = checkOut - checkIn;
    const hours = (diffMs / (1000 * 60 * 60)).toFixed(2);
    return `${hours} hours`;
}

// Export data to CSV
function exportToCSV(data, filename) {
    if (data.length === 0) {
        showMessage('No data to export', 'warning');
        return;
    }
    
    // Get headers from first object
    const headers = Object.keys(data[0]);
    
    // Create CSV content
    let csv = headers.join(',') + '\n';
    
    data.forEach(row => {
        const values = headers.map(header => {
            let value = row[header] || '';
            // Escape quotes and wrap in quotes if contains comma
            if (typeof value === 'string') {
                value = value.replace(/"/g, '""');
                if (value.includes(',') || value.includes('\n') || value.includes('"')) {
                    value = `"${value}"`;
                }
            }
            return value;
        });
        csv += values.join(',') + '\n';
    });
    
    // Create blob and download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showMessage('CSV file downloaded successfully', 'success');
}
