from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import sys
import os
import re
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    """Main page of the Flask application."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_browser_command():
    """Generate browser-use command based on business requirements."""
    try:
        print("=" * 50)
        print("GENERATE BUTTON CLICKED")
        print("=" * 50)
        
        data = request.get_json()
        requirements = data.get('requirements', '').strip()
        
        print(f"Received requirements: {requirements}")
        
        if not requirements:
            print("ERROR: No requirements provided")
            return jsonify({
                'success': False,
                'error': 'Business requirements are required'
            })
        
        # Construct the command
        command = f'uvx browser-use -p "{requirements}"'
        print(f"Constructed command: {command}")
        
        print("Executing command...")
        print(f"Command: {command}")
        
        # Execute the command - use shell=True to handle quotes properly
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout for browser automation tasks
        )
        
        print(f"Command execution completed")
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        print("=" * 50)

		# Attempt to locate generated CSV
        user_task = requirements
        csv_path = None
        if result.stdout:
            # Primary pattern from logs
            csv_pattern = r'C:\\Users\\USER\\AppData\\Local\\Temp\\browser_use_agent_[^\\]+_[^\\]+\\browseruse_agent_data\\test_cases\.csv'
            match = re.search(csv_pattern, result.stdout)
            if match:
                csv_path = match.group(0)
            # Fallback: any agent directory
            if not csv_path:
                csv_fallback_pattern = r'C:\\Users\\USER\\AppData\\Local\\Temp\\[^\\]+\\browseruse_agent_data\\test_cases\.csv'
                match = re.search(csv_fallback_pattern, result.stdout)
                if match:
                    csv_path = match.group(0)

        # Additional fallback: scan TEMP for newest browser_use_agent_* directory
        if not csv_path:
            temp_dir = Path(os.environ.get('TEMP', r'C:\\Users\\USER\\AppData\\Local\\Temp'))
            if temp_dir.exists():
                agent_dirs = list(temp_dir.glob('browser_use_agent_*'))
                if agent_dirs:
                    agent_dirs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                    for agent_dir in agent_dirs:
                        candidate = agent_dir / 'browseruse_agent_data' / 'test_cases.csv'
                        if candidate.exists():
                            csv_path = str(candidate)
                            break

        if result.returncode == 0:
            print("SUCCESS: Command executed successfully")
            if csv_path and os.path.exists(csv_path):
                print(f"Found CSV at: {csv_path}")
                return jsonify({
                    'success': True,
                    'message': result,
                    'csv_path': csv_path,
                    'task': user_task
                })
            # CSV not found, still report success but include output for troubleshooting
            return jsonify({
                'success': True,
                'message': 'Test cases generated successfully, but CSV not found in expected location.',
                'output': result.stdout,
                'task': user_task
            })
        else:
            print(f"ERROR: Command failed with return code {result.returncode}")
            return jsonify({
                'success': False,
                'error': f'Command failed: {result.stderr or "Unknown error"}',
                'output': result.stdout
            })
            
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out after 5 minutes")
        return jsonify({
            'success': False,
            'error': 'Command timed out after 5 minutes. Browser automation tasks can take longer.'
        })
    except FileNotFoundError:
        print("ERROR: uvx command not found")
        return jsonify({
            'success': False,
            'error': 'uvx command not found. Please make sure uv is installed and uvx is available.'
        })
    except Exception as e:
        print(f"ERROR: Unexpected exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask app is running'
    })

@app.route('/download')
def download_csv():
    """Download the generated CSV file by absolute path passed as query param `path`."""
    csv_path = request.args.get('path')
    if not csv_path or not os.path.exists(csv_path):
        return jsonify({'success': False, 'error': 'CSV file not found'}), 404
    # Force a meaningful filename for download
    return send_file(csv_path, as_attachment=True, download_name='test_cases.csv')

