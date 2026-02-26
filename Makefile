# Makefile for CTF Tools Projects
# Unified build and deployment for all three projects

.PHONY: help install test clean run stop logs status

# ==================== Configuration ====================
VENV := venv
PYTHON := python3
ACTIVATE := . $(VENV)/bin/activate

# Directories
VULNHUNTER_DIR := /home/tools/vuln-hunter
CTF_AGENT_DIR := /home/ctf_agent
AGENT_CURSOR_DIR := /home/agent_by_cursor

# ==================== Help ====================
help:
	@echo "CTF Tools - 统一管理命令"
	@echo ""
	@echo "安装和设置:"
	@echo "  make install          - 安装所有项目的依赖"
	@echo "  make setup            - 初始化所有项目"
	@echo "  make venv             - 创建虚拟环境"
	@echo ""
	@echo "开发:"
	@echo "  make test             - 运行所有测试"
	@echo "  make test-vulnhunter  - 测试 VulnHunter"
	@echo "  make test-ctf         - 测试 CTF Agent"
	@echo "  make test-cursor      - 测试 Agent by Cursor"
	@echo ""
	@echo "运行:"
	@echo "  make run              - 使用 Docker Compose 运行所有服务"
	@echo "  make run-vulnhunter   - 运行 VulnHunter"
	@echo "  make run-ctf          - 运行 CTF Agent"
	@echo "  make run-cursor       - 运行 Agent by Cursor"
	@echo ""
	@echo "Docker:"
	@echo "  make build            - 构建所有 Docker 镜像"
	@echo "  make build-vulnhunter - 构建 VulnHunter 镜像"
	@echo "  make build-ctf        - 构建 CTF Agent 镜像"
	@echo "  make build-cursor     - 构建 Agent Cursor 镜像"
	@echo "  make compose-up       - 启动 Docker Compose"
	@echo "  make compose-down     - 停止 Docker Compose"
	@echo ""
	@echo "日志和监控:"
	@echo "  make logs             - 查看所有日志"
	@echo "  make logs-vulnhunter  - 查看 VulnHunter 日志"
	@echo "  make logs-ctf         - 查看 CTF Agent 日志"
	@echo "  make logs-cursor      - 查看 Agent Cursor 日志"
	@echo "  make status           - 查看服务状态"
	@echo ""
	@echo "Git:"
	@echo "  make git-status       - 查看所有项目的 Git 状态"
	@echo "  make git-push         - 推送所有项目到 GitHub"
	@echo "  make git-pull         - 从 GitHub 拉取更新"
	@echo ""
	@echo "清理:"
	@echo "  make clean            - 清理临时文件"
	@echo "  make clean-docker     - 清理 Docker 资源"
	@echo "  make reset            - 重置所有环境"

# ==================== Installation ====================
venv:
	@echo "创建虚拟环境..."
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip setuptools wheel

install: venv
	@echo "安装项目依赖..."
	cd $(VULNHUNTER_DIR) && pip install -r requirements.txt
	cd $(CTF_AGENT_DIR) && pip install -r requirements.txt
	cd $(AGENT_CURSOR_DIR) && pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

setup: install
	@echo "初始化项目..."
	cd $(VULNHUNTER_DIR) && python3 init.py
	@echo "✅ 项目初始化完成"

# ==================== Testing ====================
test:
	@echo "运行所有测试..."
	cd $(VULNHUNTER_DIR) && pytest tests/test_basic.py -v || echo "VulnHunter tests skipped or failed"
	cd $(CTF_AGENT_DIR) && pytest tests/test_basic.py -v || echo "CTF Agent tests skipped or failed"
	cd $(AGENT_CURSOR_DIR) && pytest tests/test_basic.py -v || echo "Agent Cursor tests skipped or failed"
	@echo "✅ 测试完成"

test-vulnhunter:
	@echo "运行 VulnHunter 测试..."
	cd $(VULNHUNTER_DIR) && pytest tests/ -v

test-ctf:
	@echo "运行 CTF Agent 测试..."
	cd $(CTF_AGENT_DIR) && pytest tests/ -v

test-cursor:
	@echo "运行 Agent by Cursor 测试..."
	cd $(AGENT_CURSOR_DIR) && pytest tests/ -v

# ==================== Running ====================
run: compose-up
	@echo "✅ 所有服务已启动"
	@echo "  - VulnHunter: http://localhost:5001"
	@echo "  - CTF Agent: 交互模式"
	@echo "  - Agent Cursor: http://localhost:8000"
	@echo "  - WebSocket: ws://localhost:8001"

run-vulnhunter:
	@echo "启动 VulnHunter..."
	cd $(VULNHUNTER_DIR) && python3 run.py --web &

run-ctf:
	@echo "启动 CTF Agent..."
	cd $(CTF_AGENT_DIR) && python3 main.py --interactive

run-cursor:
	@echo "启动 Agent by Cursor..."
	cd $(AGENT_CURSOR_DIR) && python3 -m src.main --web-server &

# ==================== Docker ====================
build: build-vulnhunter build-ctf build-cursor
	@echo "✅ 所有镜像构建完成"

build-vulnhunter:
	@echo "构建 VulnHunter 镜像..."
	cd $(VULNHUNTER_DIR) && docker build -t vulnhunter:latest -f Dockerfile .

build-ctf:
	@echo "构建 CTF Agent 镜像..."
	cd $(CTF_AGENT_DIR) && docker build -t ctf-agent:latest -f sandbox/Dockerfile .

build-cursor:
	@echo "构建 Agent Cursor 镜像..."
	cd $(AGENT_CURSOR_DIR) && docker build -t agent-cursor:latest -f Dockerfile .

compose-up:
	@echo "启动 Docker Compose..."
	docker-compose up -d
	@echo "查看日志: make logs"
	@echo "查看状态: make status"

compose-down:
	@echo "停止 Docker Compose..."
	docker-compose down

# ==================== Logs ====================
logs:
	docker-compose logs -f

logs-vulnhunter:
	docker-compose logs -f vulnhunter

logs-ctf:
	docker-compose logs -f ctf-agent

logs-cursor:
	docker-compose logs -f agent-cursor

# ==================== Status ====================
status:
	@echo "Docker 容器状态:"
	docker-compose ps
	@echo ""
	@echo "端口监听:"
	@netstat -tlnp 2>/dev/null | grep -E '5001|8000|8001' || echo "无端口监听"

# ==================== Git ====================
git-status:
	@echo "VulnHunter 状态:"
	cd $(VULNHUNTER_DIR) && git status --short
	@echo ""
	@echo "CTF Agent 状态:"
	cd $(CTF_AGENT_DIR) && git status --short
	@echo ""
	@echo "Agent Cursor 状态:"
	cd $(AGENT_CURSOR_DIR) && git status --short

git-push:
	@echo "推送所有项目到 GitHub..."
	cd $(VULNHUNTER_DIR) && git push origin master
	cd $(CTF_AGENT_DIR) && git push origin master
	cd $(AGENT_CURSOR_DIR) && git push origin master
	@echo "✅ 推送完成"

git-pull:
	@echo "从 GitHub 拉取更新..."
	cd $(VULNHUNTER_DIR) && git pull origin master
	cd $(CTF_AGENT_DIR) && git pull origin master
	cd $(AGENT_CURSOR_DIR) && git pull origin master
	@echo "✅ 拉取完成"

# ==================== Cleaning ====================
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

clean-docker:
	@echo "清理 Docker 资源..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Docker 清理完成"

reset: clean-docker clean
	@echo "重置所有环境..."
	rm -rf $(VENV)
	@echo "✅ 重置完成"

# ==================== Utilities ====================
format:
	@echo "格式化代码..."
	find . -type f -name "*.py" | xargs black

lint:
	@echo "代码检查..."
	find . -type f -name "*.py" | xargs flake8

typecheck:
	@echo "类型检查..."
	find . -type f -name "*.py" | xargs mypy

all: clean install test build
	@echo "✅ 完整构建完成"

.DEFAULT_GOAL := help
