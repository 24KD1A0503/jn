from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'JatayuNetra AI Service',
        'port': os.getenv('PORT', 5000)
    })

@app.route('/api/ai/analyze', methods=['POST'])
def analyze():
    return jsonify({
        'success': True,
        'data': {
            'anomaly_score': 0.2,
            'safety_score': 0.8,
            'recommendations': ['All systems normal']
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'🤖 AI Service starting on port {port}')
    app.run(host='0.0.0.0', port=port, debug=True)