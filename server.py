from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)
pc_history = []

@app.route('/report', methods=['POST'])
def report():
    global pc_history
    data = request.json
    data['timestamp'] = datetime.now().strftime("%H:%M:%S")
    
    if len(pc_history) >= 10:
        pc_history.clear()

    pc_history.append(data)
    return {"status": "success"}, 200

@app.route('/')
def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Advanced PC Monitor</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; padding: 20px; }
            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-radius: 10px; overflow: hidden; }
            th { background: #333; color: white; padding: 12px; font-size: 12px; }
            td { padding: 15px; border-bottom: 1px solid #eee; text-align: center; font-size: 13px; }
            
            .usage-box { width: 200px; text-align: left; margin: 0 auto; }
            .bar-bg { background: #eee; height: 8px; border-radius: 4px; overflow: hidden; margin: 4px 0 10px; }
            .bar-fill { height: 100%; transition: 0.5s; }
            
            .net-info { font-size: 11px; color: #666; text-align: left; background: #f1f1f1; padding: 5px; border-radius: 4px; display: inline-block; }
            .proc-tag { display: block; font-size: 10px; background: #e8f4fd; color: #2980b9; margin: 2px; padding: 2px 5px; border-radius: 3px; text-align: left; }
            
            .critical { background: #e74c3c !important; }
        </style>
    </head>
    <body>
        <h2 style="text-align: center;">🚀 Advanced System Monitoring Station</h2>
        <table>
            <thead>
                <tr>
                    <th>Time / Host</th>
                    <th>CPU & RAM (Usage)</th>
                    <th>Disk C & D (Free/Total)</th>
                    <th>Network (MB/s)</th>
                    <th>Top 3 Processes (CPU)</th>
                </tr>
            </thead>
            <tbody>
                {% for stats in data %}
                <tr>
                    <td>{{ stats.timestamp }}<br><strong>{{ stats.hostname }}</strong></td>
                    <td>
                        <div class="usage-box">
                            <small>CPU: {{ stats.cpu_usage }}%</small>
                            <div class="bar-bg"><div class="bar-fill" style="width: {{ stats.cpu_usage }}%; background:#3498db;"></div></div>
                            <small>RAM: {{ stats.ram_usage }}%</small>
                            <div class="bar-bg"><div class="bar-fill" style="width: {{ stats.ram_usage }}%; background:#2ecc71;"></div></div>
                        </div>
                    </td>
                    <td>
                        <div class="usage-box">
                            <small>C: {{ stats.disk_c_free }}GB / {{ stats.disk_c_total }}GB</small>
                            <div class="bar-bg"><div class="bar-fill" style="width: {{ stats.disk_c }}%; background:#9b59b6;"></div></div>
                            {% if stats.disk_d is not none %}
                            <small>D: {{ stats.disk_d_free }}GB / {{ stats.disk_d_total }}GB</small>
                            <div class="bar-bg"><div class="bar-fill" style="width: {{ stats.disk_d }}%; background:#e67e22;"></div></div>
                            {% else %}<small style="color:#ccc;">D: Not Connected</small>{% endif %}
                        </div>
                    </td>
                    <td>
                        <div class="net-info">
                            🔼 Up: {{ stats.net_sent }} MB/s<br>🔽 Down: {{ stats.net_recv }} MB/s
                        </div>
                    </td>
                    <td>
                        {% for proc in stats.top_processes %}
                        <span class="proc-tag">{{ proc }}</span>
                        {% endfor %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <script>setTimeout(() => location.reload(), 4000);</script>
    </body>
    </html>
    """
    return render_template_string(html, data=pc_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)