from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Cleaner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .panel h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .icon {
            font-size: 1.2em;
        }
        
        textarea {
            width: 100%;
            height: 400px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f5f5f5;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-success:hover {
            background: #059669;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        
        .status {
            padding: 10px 15px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
            animation: slideIn 0.3s;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .status.success {
            background: #d1fae5;
            color: #065f46;
            border-left: 4px solid #10b981;
        }
        
        .status.error {
            background: #fee2e2;
            color: #991b1b;
            border-left: 4px solid #ef4444;
        }
        
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .example-section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-top: 20px;
        }
        
        .example-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .example-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .example-btn {
            padding: 8px 16px;
            background: #f0f0f0;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .example-btn:hover {
            background: #667eea;
            color: white;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧹 HTML Cleaner</h1>
            <p>Remove HTML tags while preserving visible text and links</p>
        </div>
        
        <div class="main-content">
            <div class="panel">
                <h2><span class="icon">📝</span> Input HTML</h2>
                <textarea id="inputHtml" placeholder="Paste your HTML code here..."></textarea>
                <div class="button-group">
                    <button class="btn-primary" onclick="cleanHtml()">
                        <span id="cleanBtnText">🧹 Clean HTML</span>
                        <span id="cleanBtnLoader" class="loading" style="display: none;"></span>
                    </button>
                    <button class="btn-secondary" onclick="clearInput()">🗑️ Clear</button>
                </div>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-label">Characters</div>
                        <div class="stat-value" id="inputChars">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Words</div>
                        <div class="stat-value" id="inputWords">0</div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2><span class="icon">✨</span> Cleaned Output</h2>
                <textarea id="outputText" placeholder="Cleaned text will appear here..." readonly></textarea>
                <div class="button-group">
                    <button class="btn-success" onclick="copyOutput()">📋 Copy to Clipboard</button>
                    <button class="btn-secondary" onclick="downloadOutput()">💾 Download</button>
                </div>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-label">Characters</div>
                        <div class="stat-value" id="outputChars">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Words</div>
                        <div class="stat-value" id="outputWords">0</div>
                    </div>
                </div>
                <div id="status" class="status"></div>
            </div>
        </div>
        
        <div class="example-section">
            <h3>📚 Quick Examples</h3>
            <div class="example-buttons">
                <button class="example-btn" onclick="loadExample(1)">Simple Paragraph</button>
                <button class="example-btn" onclick="loadExample(2)">With Links</button>
                <button class="example-btn" onclick="loadExample(3)">Complex HTML</button>
                <button class="example-btn" onclick="loadExample(4)">Article with Images</button>
            </div>
        </div>
    </div>
    
    <script>
        const examples = {
            1: '<div><h1>Welcome</h1><p>This is a <strong>simple</strong> example.</p></div>',
            2: '<p>Visit <a href="https://example.com">our website</a> for more info. Contact us at <a href="mailto:info@example.com">info@example.com</a></p>',
            3: '<div class="container"><header><nav><ul><li><a href="/">Home</a></li><li><a href="/about">About</a></li></ul></nav></header><main><article><h2>Article Title</h2><p>Some content here with <span style="color:red;">styled text</span>.</p></article></main></div>',
            4: '<article><h1>Travel Guide</h1><img src="photo.jpg" alt="Beach photo"><p>Check out this <a href="https://beach.com">amazing beach</a>!</p><img src="sunset.jpg" alt="Sunset view"><p>Beautiful sunsets every evening.</p></article>'
        };
        
        const inputHtml = document.getElementById('inputHtml');
        const outputText = document.getElementById('outputText');
        
        inputHtml.addEventListener('input', updateInputStats);
        
        function updateInputStats() {
            const text = inputHtml.value;
            document.getElementById('inputChars').textContent = text.length;
            document.getElementById('inputWords').textContent = text.trim() ? text.trim().split(/\s+/).length : 0;
        }
        
        function updateOutputStats() {
            const text = outputText.value;
            document.getElementById('outputChars').textContent = text.length;
            document.getElementById('outputWords').textContent = text.trim() ? text.trim().split(/\s+/).length : 0;
        }
        
        async function cleanHtml() {
            const html = inputHtml.value.trim();
            
            if (!html) {
                showStatus('Please enter some HTML to clean', 'error');
                return;
            }
            
            const cleanBtn = document.querySelector('.btn-primary');
            const btnText = document.getElementById('cleanBtnText');
            const btnLoader = document.getElementById('cleanBtnLoader');
            
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-block';
            cleanBtn.disabled = true;
            
            try {
                const response = await fetch('/api/clean', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ html: html })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    outputText.value = data.cleaned_text;
                    updateOutputStats();
                    showStatus('HTML cleaned successfully!', 'success');
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            } finally {
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
                cleanBtn.disabled = false;
            }
        }
        
        function clearInput() {
            inputHtml.value = '';
            outputText.value = '';
            updateInputStats();
            updateOutputStats();
            hideStatus();
        }
        
        function copyOutput() {
            if (!outputText.value) {
                showStatus('Nothing to copy', 'error');
                return;
            }
            
            outputText.select();
            document.execCommand('copy');
            showStatus('Copied to clipboard!', 'success');
        }
        
        function downloadOutput() {
            if (!outputText.value) {
                showStatus('Nothing to download', 'error');
                return;
            }
            
            const blob = new Blob([outputText.value], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cleaned_text.txt';
            a.click();
            window.URL.revokeObjectURL(url);
            showStatus('Downloaded successfully!', 'success');
        }
        
        function loadExample(num) {
            inputHtml.value = examples[num];
            updateInputStats();
            outputText.value = '';
            updateOutputStats();
            hideStatus();
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            
            setTimeout(() => {
                hideStatus();
            }, 5000);
        }
        
        function hideStatus() {
            const status = document.getElementById('status');
            status.style.display = 'none';
        }
    </script>
</body>
</html>
"""

def clean_html(html_content):
    """
    Clean HTML content by removing tags but preserving visible text and links
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link", "head"]):
            script.decompose()
        
        # Process the HTML to extract text and links
        def extract_text(element):
            result = []
            
            for content in element.children:
                if content.name is None:  # Text node
                    text = str(content).strip()
                    if text:
                        result.append(text)
                elif content.name == 'a':  # Link element
                    link_text = content.get_text().strip()
                    href = content.get('href', '')
                    if link_text and href:
                        result.append(f"{link_text} ({href})")
                    elif link_text:
                        result.append(link_text)
                elif content.name == 'br':  # Line break
                    result.append('\n')
                elif content.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
                    # Block elements - add newlines
                    inner = extract_text(content)
                    if inner:
                        result.append('\n' + ' '.join(inner) + '\n')
                elif content.name == 'img':  # Image with alt text
                    alt = content.get('alt', '')
                    src = content.get('src', '')
                    if alt:
                        result.append(f"[Image: {alt}]")
                    elif src:
                        result.append(f"[Image: {src}]")
                else:
                    # Recursively process other elements
                    result.extend(extract_text(content))
            
            return result
        
        # Extract all text and links
        text_parts = extract_text(soup)
        
        # Join and clean up whitespace
        cleaned_text = ' '.join(text_parts)
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # Remove extra newlines
        cleaned_text = re.sub(r' +', ' ', cleaned_text)  # Remove extra spaces
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    except Exception as e:
        raise Exception(f"Error cleaning HTML: {str(e)}")

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/clean', methods=['POST'])
def clean_html_api():
    try:
        data = request.get_json()
        
        if not data or 'html' not in data:
            return jsonify({
                'success': False,
                'error': 'No HTML content provided'
            }), 400
        
        html_content = data['html']
        cleaned_text = clean_html(html_content)
        
        return jsonify({
            'success': True,
            'cleaned_text': cleaned_text,
            'original_length': len(html_content),
            'cleaned_length': len(cleaned_text)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)