#!/bin/bash
# OpenClaw Dashboard WebSocket Deployment Script
# Usage: ./deploy.sh [install|start|stop|restart|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_FILE="$SCRIPT_DIR/backend_ws.py"
FRONTEND_FILE="$SCRIPT_DIR/frontend_ws.html"
PID_FILE="$SCRIPT_DIR/dashboard.pid"
LOG_FILE="$SCRIPT_DIR/dashboard.log"

# Configuration
WS_PORT=${WS_PORT:-8000}
WS_HOST=${WS_HOST:-0.0.0.0}
WORKSPACE_DIR=${WORKSPACE_DIR:-/root/.openclaw/workspace}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
}

check_dependencies() {
    print_status "Checking dependencies..."
    
    local deps=("websockets" "psutil")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -eq 0 ]; then
        print_success "All dependencies installed"
    else
        print_warning "Missing dependencies: ${missing[*]}"
        print_status "Installing dependencies..."
        pip3 install "${missing[@]}"
        print_success "Dependencies installed"
    fi
}

install() {
    print_status "Installing OpenClaw Dashboard..."
    
    check_python
    check_dependencies
    
    # Create systemd service file (optional)
    if command -v systemctl &> /dev/null; then
        print_status "Creating systemd service..."
        
        sudo tee /etc/systemd/system/openclaw-dashboard.service > /dev/null <<EOF
[Unit]
Description=OpenClaw Dashboard WebSocket Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=WS_HOST=$WS_HOST
Environment=WS_PORT=$WS_PORT
Environment=WORKSPACE_DIR=$WORKSPACE_DIR
ExecStart=/usr/bin/python3 $BACKEND_FILE
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        print_success "Systemd service created"
        print_status "You can manage the service with: sudo systemctl [start|stop|restart|status] openclaw-dashboard"
    fi
    
    print_success "Installation complete!"
    print_status "Start the server with: ./deploy.sh start"
}

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Dashboard is already running (PID: $PID)"
            return
        fi
    fi
    
    print_status "Starting OpenClaw Dashboard..."
    check_dependencies
    
    export WS_HOST
    export WS_PORT
    export WORKSPACE_DIR
    
    nohup python3 "$BACKEND_FILE" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if ps -p "$!" > /dev/null 2>&1 || ps -p "$(cat "$PID_FILE")" > /dev/null 2>&1; then
        print_success "Dashboard started successfully!"
        print_status "WebSocket Server: ws://$WS_HOST:$WS_PORT/ws"
        print_status "Frontend: file://$FRONTEND_FILE"
        print_status "Log file: $LOG_FILE"
        
        # Display access URLs
        IP=$(hostname -I | awk '{print $1}')
        echo ""
        print_status "Access URLs:"
        echo "  Local:    http://localhost:$WS_PORT (if serving frontend via backend)"
        echo "  Network:  http://$IP:$WS_PORT"
        echo "  Frontend: Open $FRONTEND_FILE in your browser"
        echo ""
        print_status "To view logs: tail -f $LOG_FILE"
    else
        print_error "Failed to start dashboard"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_status "Stopping Dashboard (PID: $PID)..."
            kill "$PID"
            rm -f "$PID_FILE"
            print_success "Dashboard stopped"
        else
            print_warning "Dashboard is not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found"
        
        # Try to find and kill process
        PID=$(pgrep -f "backend_ws.py" || true)
        if [ -n "$PID" ]; then
            print_status "Killing process $PID..."
            kill "$PID" 2>/dev/null || true
            print_success "Dashboard stopped"
        fi
    fi
}

restart() {
    stop
    sleep 1
    start
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_success "Dashboard is running (PID: $PID)"
            print_status "WebSocket Server: ws://$WS_HOST:$WS_PORT"
            
            # Check if port is listening
            if command -v netstat &> /dev/null; then
                netstat -tlnp 2>/dev/null | grep ":$WS_PORT" || true
            elif command -v ss &> /dev/null; then
                ss -tlnp 2>/dev/null | grep ":$WS_PORT" || true
            fi
        else
            print_error "Dashboard is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        # Check for running process
        PID=$(pgrep -f "backend_ws.py" || true)
        if [ -n "$PID" ]; then
            print_success "Dashboard is running (PID: $PID, no PID file)"
        else
            print_warning "Dashboard is not running"
        fi
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        print_error "Log file not found"
    fi
}

# Main command handler
case "${1:-start}" in
    install)
        install
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 [install|start|stop|restart|status|logs]"
        echo ""
        echo "Commands:"
        echo "  install  - Install dependencies and create systemd service"
        echo "  start    - Start the dashboard server"
        echo "  stop     - Stop the dashboard server"
        echo "  restart  - Restart the dashboard server"
        echo "  status   - Check dashboard status"
        echo "  logs     - View dashboard logs"
        echo ""
        echo "Environment variables:"
        echo "  WS_PORT       - WebSocket port (default: 8000)"
        echo "  WS_HOST       - WebSocket host (default: 0.0.0.0)"
        echo "  WORKSPACE_DIR - Workspace directory (default: /root/.openclaw/workspace)"
        exit 1
        ;;
esac
