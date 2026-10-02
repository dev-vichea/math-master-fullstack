"""
Simple Flask server for collecting training data from users.

Run with: python training/scripts/data_collection_server.py
Access at: http://localhost:5001
"""
from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Ensure data directory exists
DATA_DIR = Path(__file__).parent.parent / "data" / "intent_classification"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# HTML template for data collection interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <title>Khmer Math Lab - Data Collection</title>
    <style>
        body { font-family: 'Khmer OS Siemreap', Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea { width: 100%; padding: 10px; font-size: 16px; }
        select { width: 100%; padding: 10px; font-size: 16px; }
        button { background: #3498db; color: white; padding: 10px 30px; border: none; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .success { color: green; margin-top: 10px; }
        .examples { background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🧮 Khmer Math Lab - Data Collection</h1>
    <p>Help us improve by providing examples of math questions!</p>
    
    <div class="examples">
        <h3>Examples:</h3>
        <ul>
            <li><strong>Solve:</strong> "ដោះស្រាយ 2x + 5 = 15" or "រក x ពី 3x = 12"</li>
            <li><strong>Evaluate:</strong> "គណនា 5 + 3 * 2" or "20% នៃ 150"</li>
            <li><strong>Simplify:</strong> "ធ្វើឲ្យសាមញ្ញ 4/8" or "កាត់បន្ថយ 6/9"</li>
        </ul>
    </div>
    
    <form id="dataForm">
        <div class="form-group">
            <label>Question (Khmer or English):</label>
            <textarea name="question" rows="3" required placeholder="Example: ដោះស្រាយ x + 5 = 10"></textarea>
        </div>
        
        <div class="form-group">
            <label>Intent:</label>
            <select name="intent" required>
                <option value="">-- Select Intent --</option>
                <option value="solve_equation">Solve Equation (ដោះស្រាយសមីការ)</option>
                <option value="evaluate_expression">Evaluate Expression (គណនាកន្សោម)</option>
                <option value="simplify_expression">Simplify Expression (ធ្វើឲ្យសាមញ្ញ)</option>
                <option value="unknown">Unknown / Other</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>Expected Answer (optional):</label>
            <input type="text" name="expected_answer" placeholder="Example: x = 5">
        </div>
        
        <button type="submit">Submit</button>
        <div id="message" class="success"></div>
    </form>
    
    <script>
        document.getElementById('dataForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const response = await fetch('/api/collect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            document.getElementById('message').textContent = result.message;
            
            if (result.status === 'success') {
                e.target.reset();
                setTimeout(() => {
                    document.getElementById('message').textContent = '';
                }, 3000);
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/collect', methods=['POST'])
def collect_data():
    try:
        data = request.json
        
        # Add metadata
        data['collected_at'] = datetime.now().isoformat()
        data['source'] = 'manual_collection'
        
        # Save to JSONL file
        data_file = DATA_DIR / "collected_data.jsonl"
        with open(data_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Thank you! Collected {count_collected()} examples so far.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/stats')
def stats():
    """Get collection statistics."""
    count = count_collected()
    
    # Count by intent
    intents = {}
    data_file = DATA_DIR / "collected_data.jsonl"
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line)
                intent = item.get('intent', 'unknown')
                intents[intent] = intents.get(intent, 0) + 1
    
    return jsonify({
        'total_collected': count,
        'by_intent': intents
    })

def count_collected():
    """Count total collected examples."""
    data_file = DATA_DIR / "collected_data.jsonl"
    if not data_file.exists():
        return 0
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

if __name__ == '__main__':
    print("=" * 60)
    print("Khmer Math Lab - Data Collection Server")
    print("=" * 60)
    print(f"📂 Data will be saved to: {DATA_DIR}")
    print(f"🌐 Open: http://localhost:5001")
    print(f"📊 Stats: http://localhost:5001/api/stats")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
