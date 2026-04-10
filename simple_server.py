
import http.server
import socketserver
import json
import os
from pathlib import Path

PORT = 3000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/marketplace.html'
        elif self.path == '/api/agents':
            self.send_json_response(self.get_agents())
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_upload()
            return
        self.send_error(404)
    
    def get_agents(self):
        """Get all listed agents"""
        marketplace_dir = Path('/home/paperclip/arli/data/marketplace')
        agents = []
        
        if marketplace_dir.exists():
            for f in marketplace_dir.glob('*.json'):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        if data.get('status') == 'active':
                            agents.append({
                                'arli_id': data.get('arli_id'),
                                'name': data.get('name'),
                                'tier': data.get('tier', 'COMMON'),
                                'level': data.get('level', 1),
                                'xp': data.get('xp', 0),
                                'price': data.get('price', 0),
                                'capabilities': data.get('capabilities', [])[:3]
                            })
                except:
                    pass
        
        # Add demo agents if empty
        if not agents:
            agents = [
                {
                    'arli_id': 'demo_1',
                    'name': 'Demo Trading Bot',
                    'tier': 'UNCOMMON',
                    'level': 5,
                    'xp': 500,
                    'price': 99.99,
                    'capabilities': [{'name': 'Trading'}, {'name': 'Analysis'}]
                }
            ]
        
        return {'total': len(agents), 'agents': agents}
    
    def handle_upload(self):
        """Handle agent upload"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            # Save to marketplace directory
            marketplace_dir = Path('/home/paperclip/arli/data/marketplace')
            marketplace_dir.mkdir(parents=True, exist_ok=True)
            
            agent_id = data.get('arli_id', 'unknown')
            with open(marketplace_dir / f'{agent_id}.json', 'w') as f:
                json.dump({**data, 'status': 'active', 'listed_at': str(os.times())}, f)
            
            self.send_json_response({'success': True, 'agent_id': agent_id})
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)}, 400)
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir('/home/paperclip/arli')
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    httpd.serve_forever()
