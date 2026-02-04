// Global variable for last prediction
let lastPredictionData = null;

document.getElementById('predictionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const btn = document.getElementById('predictBtn');
    const originalText = btn.querySelector('.btn-text').innerText;

    // Loading State
    btn.querySelector('.btn-text').innerText = 'Analyzing...';
    btn.disabled = true;

    // Gather Data
    const data = {
        ir_value: parseFloat(document.getElementById('ir_value').value),
        us_value: parseFloat(document.getElementById('us_value').value),
        acc_x: parseFloat(document.getElementById('acc_x').value),
        acc_y: parseFloat(document.getElementById('acc_y').value),
        acc_z: parseFloat(document.getElementById('acc_z').value),
        gyr_x: parseFloat(document.getElementById('gyr_x').value),
        gyr_y: parseFloat(document.getElementById('gyr_y').value),
        gyr_z: parseFloat(document.getElementById('gyr_z').value)
    };

    // Store for later use in records
    lastPredictionData = data;

    try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API Error');
        }

        const result = await response.json();

        updateUI(result);
        
        // Automatically save the record
        await saveRecordToBackend(data);

    } catch (error) {
        console.error('Error:', error);
        alert(`Error connecting to API: ${error.message}. Make sure the API is running at http://127.0.0.1:8000`);
    } finally {
        // Reset Button
        btn.querySelector('.btn-text').innerText = originalText;
        btn.disabled = false;
    }
});

function updateUI(result) {
    // Update Text Results
    const levelElement = document.getElementById('levelResult');
    const turbidityElement = document.getElementById('turbidityResult');

    // Animate Number
    animateValue(levelElement, parseFloat(levelElement.innerText) || 0, result.predicted_water_level, 1000);

    turbidityElement.innerText = result.detected_turbidity_status;

    // Update Water Visualization
    const water = document.getElementById('waterLevel');

    // Clamp percentage between 0 and 100
    // Assuming max water level is around 100cm for visualization scaling
    // Adjust this max value based on your actual data range
    const maxLevel = 350;
    const percentage = Math.min(Math.max((result.predicted_water_level / maxLevel) * 100, 0), 100);

    water.style.height = `${percentage}%`;

    // Update Color based on Turbidity
    updateWaterColor(result.detected_turbidity_status);
}

function updateWaterColor(status) {
    const water = document.getElementById('waterLevel');
    const badge = document.getElementById('turbidityResult');

    // Reset classes
    badge.className = 'value status-badge';

    if (status === 'High') {
        // Murky/Brownish - High Turbidity (Red/Danger)
        water.style.background = 'linear-gradient(to top, #b91c1c, #ef4444)';
        water.style.boxShadow = '0 0 30px rgba(239, 68, 68, 0.6)';
        badge.style.color = '#ffffff';
        badge.style.background = '#ef4444';
        badge.style.border = '1px solid #dc2626';
    } else if (status === 'Medium') {
        // Slightly cloudy - Medium Turbidity (Yellow/Warning)
        water.style.background = 'linear-gradient(to top, #d97706, #f59e0b)';
        water.style.boxShadow = '0 0 30px rgba(245, 158, 11, 0.6)';
        badge.style.color = '#ffffff';
        badge.style.background = '#f59e0b';
        badge.style.border = '1px solid #d97706';
    } else {
        // Clear Blue - Low Turbidity (Green/Success)
        water.style.background = 'linear-gradient(to top, #059669, #10b981)';
        water.style.boxShadow = '0 0 30px rgba(16, 185, 129, 0.6)';
        badge.style.color = '#ffffff';
        badge.style.background = '#10b981';
        badge.style.border = '1px solid #059669';
    }
}

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = (progress * (end - start) + start).toFixed(2);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Theme Toggle Functionality
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

// Load saved theme from localStorage
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    html.setAttribute('data-theme', 'dark');
}

// Toggle theme on button click
themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
});

// ==================== Tab Navigation ====================
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');
        
        // Remove active class from all tabs
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked tab
        btn.classList.add('active');
        document.getElementById(`${targetTab}-tab`).classList.add('active');
        
        // Load records if switching to records tab
        if (targetTab === 'records') {
            loadRecords();
        }
    });
});

// ==================== Records Management ====================
let currentEditId = null;

// Load all records
async function loadRecords() {
    try {
        const response = await fetch('http://127.0.0.1:8000/records');
        if (!response.ok) throw new Error('Failed to load records');
        
        const records = await response.json();
        displayRecords(records);
    } catch (error) {
        console.error('Error loading records:', error);
        alert('Error loading records: ' + error.message);
    }
}

// Display records in table
function displayRecords(records) {
    const tbody = document.getElementById('recordsTableBody');
    
    if (records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-records">No records available. Create a prediction to save records.</td></tr>';
        return;
    }
    
    tbody.innerHTML = records.map(record => `
        <tr>
            <td>${record.id}</td>
            <td>${new Date(record.timestamp).toLocaleString()}</td>
            <td>${record.ir_value.toFixed(2)}</td>
            <td>${record.us_value.toFixed(2)}</td>
            <td>${record.acc_x.toFixed(2)}, ${record.acc_y.toFixed(2)}, ${record.acc_z.toFixed(2)}</td>
            <td>${record.gyr_x.toFixed(2)}, ${record.gyr_y.toFixed(2)}, ${record.gyr_z.toFixed(2)}</td>
            <td>${record.predicted_water_level.toFixed(2)}</td>
            <td><span class="turbidity-badge turbidity-${record.detected_turbidity_status.toLowerCase()}">${record.detected_turbidity_status}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn-edit" onclick="editRecord(${record.id})">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14">
                            <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                        </svg>
                        Edit
                    </button>
                    <button class="btn-delete" onclick="deleteRecord(${record.id})">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14">
                            <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                        Delete
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Helper function to save record to backend
async function saveRecordToBackend(data) {
    try {
        const response = await fetch('http://127.0.0.1:8000/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to save record');
        
        return true;
    } catch (error) {
        console.error('Error saving record:', error);
        return false;
    }
}

// Edit record
function editRecord(id) {
    fetch(`http://127.0.0.1:8000/records/${id}`)
        .then(response => response.json())
        .then(record => {
            currentEditId = id;
            document.getElementById('editRecordId').value = id;
            document.getElementById('modalTitle').textContent = `Edit Record #${id}`;
            
            // Fill form
            document.getElementById('form_ir_value').value = record.ir_value;
            document.getElementById('form_us_value').value = record.us_value;
            document.getElementById('form_acc_x').value = record.acc_x;
            document.getElementById('form_acc_y').value = record.acc_y;
            document.getElementById('form_acc_z').value = record.acc_z;
            document.getElementById('form_gyr_x').value = record.gyr_x;
            document.getElementById('form_gyr_y').value = record.gyr_y;
            document.getElementById('form_gyr_z').value = record.gyr_z;
            
            // Show modal
            document.getElementById('editModal').classList.add('active');
        })
        .catch(error => {
            console.error('Error loading record:', error);
            alert('Error loading record: ' + error.message);
        });
}

// Delete record
async function deleteRecord(id) {
    if (!confirm(`Are you sure you want to delete record #${id}?`)) return;
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/records/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete record');
        
        alert('Record deleted successfully!');
        loadRecords();
    } catch (error) {
        console.error('Error deleting record:', error);
        alert('Error deleting record: ' + error.message);
    }
}

// Submit record form (update)
document.getElementById('recordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentEditId) {
        alert('No record selected for editing');
        return;
    }
    
    const id = currentEditId;
    const data = {
        ir_value: parseFloat(document.getElementById('form_ir_value').value),
        us_value: parseFloat(document.getElementById('form_us_value').value),
        acc_x: parseFloat(document.getElementById('form_acc_x').value),
        acc_y: parseFloat(document.getElementById('form_acc_y').value),
        acc_z: parseFloat(document.getElementById('form_acc_z').value),
        gyr_x: parseFloat(document.getElementById('form_gyr_x').value),
        gyr_y: parseFloat(document.getElementById('form_gyr_y').value),
        gyr_z: parseFloat(document.getElementById('form_gyr_z').value)
    };
    
    console.log('Updating record:', id, 'with data:', data);
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/records/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update record');
        }
        
        const updatedRecord = await response.json();
        console.log('Record updated:', updatedRecord);
        
        alert('Record updated successfully!');
        cancelEdit();
        loadRecords();
    } catch (error) {
        console.error('Error updating record:', error);
        alert('Error updating record: ' + error.message);
    }
});

// Cancel edit
function cancelEdit() {
    currentEditId = null;
    document.getElementById('editModal').classList.remove('active');
    document.getElementById('recordForm').reset();
    document.getElementById('modalTitle').textContent = 'Edit Record';
}

document.getElementById('cancelEditBtn').addEventListener('click', cancelEdit);
document.getElementById('closeModalBtn').addEventListener('click', cancelEdit);

// Close modal when clicking outside
document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target.id === 'editModal') {
        cancelEdit();
    }
});

// Refresh records
document.getElementById('refreshRecordsBtn').addEventListener('click', loadRecords);

// Export records to CSV
document.getElementById('exportCsvBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/records');
        if (!response.ok) throw new Error('Failed to load records');
        
        const records = await response.json();
        
        if (records.length === 0) {
            alert('No records to export');
            return;
        }
        
        // Create CSV content
        const headers = ['ID', 'Timestamp', 'IR Value', 'US Value', 'Acc X', 'Acc Y', 'Acc Z', 'Gyr X', 'Gyr Y', 'Gyr Z', 'Water Level', 'Turbidity Status'];
        const csvRows = [headers.join(',')];
        
        records.forEach(record => {
            const row = [
                record.id,
                new Date(record.timestamp).toISOString(),
                record.ir_value,
                record.us_value,
                record.acc_x,
                record.acc_y,
                record.acc_z,
                record.gyr_x,
                record.gyr_y,
                record.gyr_z,
                record.predicted_water_level,
                record.detected_turbidity_status
            ];
            csvRows.push(row.join(','));
        });
        
        const csvContent = csvRows.join('\n');
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `sensor_records_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Error exporting CSV: ' + error.message);
    }
});

// Delete all records
document.getElementById('deleteAllBtn').addEventListener('click', async () => {
    if (!confirm('Are you sure you want to delete ALL records? This cannot be undone!')) return;
    
    try {
        const response = await fetch('http://127.0.0.1:8000/records', {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete records');
        
        alert('All records deleted successfully!');
        loadRecords();
    } catch (error) {
        console.error('Error deleting records:', error);
        alert('Error deleting records: ' + error.message);
    }
});
