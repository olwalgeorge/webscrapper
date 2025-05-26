#!/usr/bin/env python3
"""
Simple web dashboard for viewing crop nutrition data
"""
import sqlite3
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import os

class CropDataHandler(SimpleHTTPRequestHandler):
    """Custom handler for crop data API and web interface"""
    
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/crops':
            self.serve_crops_api()
        elif self.path == '/api/crop-detail':
            self.serve_crop_detail()
        elif self.path.startswith('/api/'):
            self.serve_api_endpoint()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML page"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🌱 Agricultural Nutrition Database</title>
            <meta charset="UTF-8">
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                    margin: 0; padding: 20px; background: #f5f7fa; 
                }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #2d5016; text-align: center; margin-bottom: 30px; }
                .stats-grid { 
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; margin-bottom: 30px; 
                }
                .stat-card { 
                    background: white; padding: 20px; border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; 
                }
                .stat-number { font-size: 2.5rem; font-weight: bold; color: #2d5016; }
                .stat-label { color: #666; margin-top: 5px; }
                
                .crop-grid { 
                    display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                    gap: 20px; 
                }
                .crop-card { 
                    background: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; 
                }
                .crop-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
                .crop-name { font-size: 1.3rem; font-weight: bold; color: #2d5016; margin-bottom: 10px; }
                .crop-detail { margin: 8px 0; font-size: 0.9rem; }
                .crop-detail strong { color: #444; }
                .data-source { 
                    background: #e8f5e8; padding: 4px 8px; border-radius: 4px; 
                    font-size: 0.8rem; color: #2d5016; display: inline-block; margin-top: 10px; 
                }
                
                .loading { text-align: center; padding: 40px; color: #666; }
                .search-box { 
                    width: 100%; max-width: 400px; padding: 12px; border: 1px solid #ddd; 
                    border-radius: 6px; margin: 0 auto 30px; display: block; font-size: 16px; 
                }
                
                .filter-buttons { 
                    text-align: center; margin-bottom: 20px; 
                }
                .filter-btn { 
                    background: #f0f0f0; border: 1px solid #ddd; padding: 8px 16px; 
                    margin: 0 5px; border-radius: 4px; cursor: pointer; transition: all 0.2s; 
                }
                .filter-btn:hover, .filter-btn.active { background: #2d5016; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌱 Agricultural Nutrition Database</h1>
                
                <div class="stats-grid" id="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="total-crops">-</div>
                        <div class="stat-label">Total Crops</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="data-sources">-</div>
                        <div class="stat-label">Data Sources</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="completeness">-</div>
                        <div class="stat-label">Avg Completeness</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="last-updated">-</div>
                        <div class="stat-label">Last Updated</div>
                    </div>
                </div>
                
                <input type="text" class="search-box" id="search" placeholder="🔍 Search crops...">
                
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterCrops('all')">All Crops</button>
                    <button class="filter-btn" onclick="filterCrops('high-water')">High Water Needs</button>
                    <button class="filter-btn" onclick="filterCrops('low-maintenance')">Low Maintenance</button>
                </div>
                
                <div class="crop-grid" id="crops">
                    <div class="loading">Loading crop data...</div>
                </div>
            </div>
            
            <script>
                let cropsData = [];
                
                // Load crop data from API
                async function loadCrops() {
                    try {
                        const response = await fetch('/api/crops');
                        const data = await response.json();
                        cropsData = data.crops;
                        displayCrops(cropsData);
                        updateStats(data.stats);
                    } catch (error) {
                        document.getElementById('crops').innerHTML = 
                            '<div class="loading">Error loading data. Is the server running?</div>';
                    }
                }
                
                function displayCrops(crops) {
                    const container = document.getElementById('crops');
                    if (crops.length === 0) {
                        container.innerHTML = '<div class="loading">No crops found</div>';
                        return;
                    }
                    
                    container.innerHTML = crops.map(crop => `
                        <div class="crop-card">
                            <div class="crop-name">${crop.name}</div>
                            <div class="crop-detail"><strong>Water:</strong> ${truncateText(crop.water_needs || 'Not specified', 60)}</div>
                            <div class="crop-detail"><strong>Soil pH:</strong> ${truncateText(crop.soil_ph || 'Not specified', 40)}</div>
                            <div class="crop-detail"><strong>Sun:</strong> ${truncateText(crop.sun_requirements || 'Not specified', 40)}</div>
                            <div class="crop-detail"><strong>Fertilizer:</strong> ${truncateText(crop.fertilizer_recommendations || 'Not specified', 60)}</div>
                            <span class="data-source">${crop.data_source}</span>
                        </div>
                    `).join('');
                }
                
                function updateStats(stats) {
                    document.getElementById('total-crops').textContent = stats.total_crops;
                    document.getElementById('data-sources').textContent = stats.data_sources;
                    document.getElementById('completeness').textContent = stats.avg_completeness + '%';
                    document.getElementById('last-updated').textContent = 'Today';
                }
                
                function truncateText(text, maxLength) {
                    if (!text || text === 'None') return 'Not available';
                    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
                }
                
                function filterCrops(filter) {
                    // Update active button
                    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                    event.target.classList.add('active');
                    
                    let filtered = cropsData;
                    if (filter === 'high-water') {
                        filtered = cropsData.filter(crop => 
                            crop.water_needs && (crop.water_needs.includes('frequent') || crop.water_needs.includes('regular'))
                        );
                    } else if (filter === 'low-maintenance') {
                        filtered = cropsData.filter(crop => 
                            crop.water_needs && crop.water_needs.includes('drought')
                        );
                    }
                    
                    displayCrops(filtered);
                }
                
                // Search functionality
                document.getElementById('search').addEventListener('input', function(e) {
                    const searchTerm = e.target.value.toLowerCase();
                    const filtered = cropsData.filter(crop => 
                        crop.name.toLowerCase().includes(searchTerm) ||
                        (crop.water_needs && crop.water_needs.toLowerCase().includes(searchTerm)) ||
                        (crop.fertilizer_recommendations && crop.fertilizer_recommendations.toLowerCase().includes(searchTerm))
                    );
                    displayCrops(filtered);
                });
                
                // Load data when page loads
                loadCrops();
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_crops_api(self):
        """Serve crops data as JSON API"""
        try:
            conn = sqlite3.connect('crops.db')
            cursor = conn.cursor()
            
            # Get all crops
            cursor.execute('''
                SELECT name, water_needs, soil_ph, sun_requirements, 
                       fertilizer_recommendations, data_source, created_at
                FROM crops 
                ORDER BY name
            ''')
            
            crops = []
            for row in cursor.fetchall():
                crops.append({
                    'name': row[0],
                    'water_needs': row[1],
                    'soil_ph': row[2],                    'sun_requirements': row[3],
                    'fertilizer_recommendations': row[4],
                    'data_source': row[5],
                    'created_at': row[6]
                })
            
            # Get stats
            cursor.execute('SELECT COUNT(*) FROM crops')
            total_crops = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT data_source) FROM crops')
            data_sources = cursor.fetchone()[0]
            
            # Calculate completeness
            cursor.execute('''
                SELECT 
                    (COUNT(CASE WHEN water_needs IS NOT NULL AND water_needs != '' THEN 1 END) +
                     COUNT(CASE WHEN soil_ph IS NOT NULL AND soil_ph != '' THEN 1 END) +
                     COUNT(CASE WHEN fertilizer_recommendations IS NOT NULL AND fertilizer_recommendations != '' THEN 1 END) +
                     COUNT(CASE WHEN sun_requirements IS NOT NULL AND sun_requirements != '' THEN 1 END)) * 100.0 / (COUNT(*) * 4)
                FROM crops
            ''')
            result = cursor.fetchone()
            avg_completeness = round(result[0], 1) if result and result[0] is not None else 0
            
            conn.close()
            
            response_data = {
                'crops': crops,
                'stats': {
                    'total_crops': total_crops,
                    'data_sources': data_sources,
                    'avg_completeness': avg_completeness
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

def start_server(port=8000):
    """Start the web server"""
    print(f"🌱 Starting Agricultural Nutrition Database Server...")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔗 API: http://localhost:{port}/api/crops")
    print(f"⚡ Press Ctrl+C to stop\n")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    server = HTTPServer(('localhost', port), CropDataHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_server()
