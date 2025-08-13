async function generateCommand() {
    const requirements = document.getElementById('requirements').value.trim();
    const outputDiv = document.getElementById('output');
    const loadingDiv = document.getElementById('loading');
    const statusDiv = document.getElementById('status');
    
    if (!requirements) {
        showStatus('Please enter business requirements first.', 'error');
        return;
    }
    
    // Show loading
    loadingDiv.style.display = 'block';
    outputDiv.style.display = 'none';
    statusDiv.style.display = 'none';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                requirements: requirements
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            outputDiv.style.display = 'block';
            if (result.csv_path) {
                const downloadUrl = '/download?path=' + encodeURIComponent(result.csv_path);
                outputDiv.innerHTML = `
                    <p><strong>Test cases generated successfully!</strong></p>
                    <a class="generate-btn" href="${downloadUrl}">Download test_cases.csv</a>
                `;
            } else {
                outputDiv.textContent = result.message || 'Test cases generated successfully.';
            }
            showStatus('Test cases generated successfully!', 'success');
        } else {
            showStatus('Error: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function clearForm() {
    document.getElementById('requirements').value = '';
    document.getElementById('output').style.display = 'none';
    document.getElementById('status').style.display = 'none';
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + type;
    statusDiv.style.display = 'block';
}

// Add keyboard shortcuts
document.addEventListener('DOMContentLoaded', function() {
    // Ctrl+Enter to generate
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            generateCommand();
        }
    });
    
    // Auto-resize textarea
    const textarea = document.getElementById('requirements');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.max(120, this.scrollHeight) + 'px';
    });
});
