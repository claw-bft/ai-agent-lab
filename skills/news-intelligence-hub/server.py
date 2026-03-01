#!/usr/bin/env python3
"""
新闻智能分析中心 - 本地服务器
提供可视化仪表板访问
"""

import http.server
import socketserver
import json
import webbrowser
from pathlib import Path

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
        return super().do_GET()

def start_server():
    """启动本地服务器"""
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"\n🚀 新闻智能分析中心已启动!")
        print(f"📊 访问地址: http://localhost:{PORT}")
        print(f"📱 移动端访问: http://0.0.0.0:{PORT}")
        print(f"\n按 Ctrl+C 停止服务器\n")
        
        # 自动打开浏览器
        webbrowser.open(f'http://localhost:{PORT}')
        
        httpd.serve_forever()

if __name__ == '__main__':
    start_server()
