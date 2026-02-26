#!/bin/bash
# Agent Dashboard 启动脚本
# 启动 Backend + Monitor + Frontend (可选)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
MONITOR_DIR="$PROJECT_DIR/monitor"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Python version: $PYTHON_VERSION"
}

# 安装依赖
install_deps() {
    local dir=$1
    local name=$2
    
    log_info "Installing dependencies for $name..."
    cd "$dir"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    deactivate
    
    log_success "Dependencies installed for $name"
}

# 启动Backend
start_backend() {
    log_info "Starting Backend service..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 检查端口
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "Port 8000 is already in use. Backend may already be running."
        return
    fi
    
    nohup python3 main.py > "$PROJECT_DIR/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_DIR/logs/backend.pid"
    
    sleep 2
    
    if kill -0 $BACKEND_PID 2>/dev/null; then
        log_success "Backend started (PID: $BACKEND_PID)"
        log_info "API: http://localhost:8000"
        log_info "WebSocket: ws://localhost:8000/ws"
    else
        log_error "Backend failed to start. Check logs/backend.log"
    fi
    
    deactivate
}

# 启动Monitor
start_monitor() {
    log_info "Starting Monitor process..."
    cd "$MONITOR_DIR"
    source venv/bin/activate
    
    nohup python3 monitor.py > "$PROJECT_DIR/logs/monitor.log" 2>&1 &
    MONITOR_PID=$!
    echo $MONITOR_PID > "$PROJECT_DIR/logs/monitor.pid"
    
    sleep 1
    
    if kill -0 $MONITOR_PID 2>/dev/null; then
        log_success "Monitor started (PID: $MONITOR_PID)"
    else
        log_error "Monitor failed to start. Check logs/monitor.log"
    fi
    
    deactivate
}

# 启动Frontend (简单HTTP服务器)
start_frontend() {
    log_info "Starting Frontend..."
    cd "$FRONTEND_DIR"
    
    # 检查端口
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "Port 8080 is already in use. Frontend may already be running."
        return
    fi
    
    nohup python3 -m http.server 8080 > "$PROJECT_DIR/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_DIR/logs/frontend.pid"
    
    sleep 1
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        log_success "Frontend started (PID: $FRONTEND_PID)"
        log_info "Dashboard: http://localhost:8080"
    else
        log_error "Frontend failed to start. Check logs/frontend.log"
    fi
}

# 停止所有服务
stop_all() {
    log_info "Stopping all services..."
    
    for pid_file in "$PROJECT_DIR/logs"/*.pid; do
        if [ -f "$pid_file" ]; then
            local service=$(basename "$pid_file" .pid)
            local pid=$(cat "$pid_file")
            
            if kill -0 $pid 2>/dev/null; then
                kill $pid 2>/dev/null || true
                log_success "Stopped $service (PID: $pid)"
            fi
            
            rm -f "$pid_file"
        fi
    done
    
    log_success "All services stopped"
}

# 显示状态
status() {
    log_info "Service Status:"
    echo "-------------------"
    
    for service in backend monitor frontend; do
        local pid_file="$PROJECT_DIR/logs/$service.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 $pid 2>/dev/null; then
                echo -e "$service: ${GREEN}RUNNING${NC} (PID: $pid)"
            else
                echo -e "$service: ${RED}STOPPED${NC} (stale PID file)"
            fi
        else
            echo -e "$service: ${YELLOW}STOPPED${NC}"
        fi
    done
}

# 查看日志
logs() {
    local service=$1
    local log_file="$PROJECT_DIR/logs/${service}.log"
    
    if [ -f "$log_file" ]; then
        tail -f "$log_file"
    else
        log_error "Log file not found: $log_file"
    fi
}

# 创建必要的目录
setup_dirs() {
    mkdir -p "$PROJECT_DIR/logs"
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            setup_dirs
            check_python
            
            log_info "Starting Agent Dashboard..."
            
            install_deps "$BACKEND_DIR" "Backend"
            install_deps "$MONITOR_DIR" "Monitor"
            
            start_backend
            start_monitor
            start_frontend
            
            echo ""
            log_success "Agent Dashboard started successfully!"
            echo ""
            echo "Services:"
            echo "  Backend:   http://localhost:8000"
            echo "  WebSocket: ws://localhost:8000/ws"
            echo "  Dashboard: http://localhost:8080"
            echo ""
            echo "Commands:"
            echo "  ./start.sh stop     - Stop all services"
            echo "  ./start.sh status   - Check service status"
            echo "  ./start.sh logs backend  - View backend logs"
            ;;
            
        stop)
            stop_all
            ;;
            
        restart)
            stop_all
            sleep 2
            $0 start
            ;;
            
        status)
            status
            ;;
            
        logs)
            logs "${2:-backend}"
            ;;
            
        install)
            install_deps "$BACKEND_DIR" "Backend"
            install_deps "$MONITOR_DIR" "Monitor"
            ;;
            
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|install}"
            echo ""
            echo "Commands:"
            echo "  start    - Start all services"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  status   - Check service status"
            echo "  logs     - View logs (backend|monitor|frontend)"
            echo "  install  - Install dependencies only"
            exit 1
            ;;
    esac
}

main "$@"
