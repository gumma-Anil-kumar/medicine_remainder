// Main JavaScript file for medicine reminder

// Handle notification responses
function handleNotification(historyId, action) {
    fetch(`/api/notification/${historyId}/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            
            if (action === 'taken') {
                // Update UI to show medicine as taken
                updateMedicineStatus(historyId, 'taken');
            }
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred', 'error');
    });
}

// Show notification toast
function showNotification(message, type = 'info') {
    // Create toast container if it doesn't exist
    if (!$('#toast-container').length) {
        $('body').append('<div id="toast-container" class="position-fixed bottom-0 end-0 p-3" style="z-index: 11"></div>');
    }
    
    const toastId = 'toast-' + Date.now();
    const bgColor = type === 'success' ? 'bg-success' : (type === 'error' ? 'bg-danger' : 'bg-info');
    
    const toast = `
        <div id="${toastId}" class="toast ${bgColor} text-white" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgColor} text-white">
                <strong class="me-auto">Medicine Reminder</strong>
                <small>just now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    $('#toast-container').append(toast);
    const toastElement = new bootstrap.Toast(document.getElementById(toastId));
    toastElement.show();
    
    // Remove toast after it's hidden
    document.getElementById(toastId).addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Update medicine status in UI
function updateMedicineStatus(historyId, status) {
    const medicineElement = $(`.medicine-item[data-history-id="${historyId}"]`);
    
    if (medicineElement.length) {
        medicineElement.removeClass('pending missed').addClass(status);
        
        const statusBadge = medicineElement.find('.status-badge');
        if (statusBadge.length) {
            statusBadge.text(status.charAt(0).toUpperCase() + status.slice(1));
            statusBadge.removeClass('bg-warning bg-danger').addClass(
                status === 'taken' ? 'bg-success' : 'bg-warning'
            );
        }
    }
}

// Check for pending reminders
function checkPendingReminders() {
    setInterval(() => {
        // This could be enhanced with WebSocket for real-time updates
        console.log('Checking for pending reminders...');
    }, 60000); // Check every minute
}

// Initialize on document ready
$(document).ready(function() {
    console.log('Medicine Reminder App initialized');
    
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle notification clicks
    $(document).on('click', '.notification-taken', function() {
        const historyId = $(this).data('history-id');
        handleNotification(historyId, 'taken');
    });
    
    $(document).on('click', '.notification-snooze', function() {
        const historyId = $(this).data('history-id');
        handleNotification(historyId, 'snooze');
    });
    
    // Start checking for pending reminders
    checkPendingReminders();
});