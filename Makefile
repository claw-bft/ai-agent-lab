# Makefile for AI Agent Lab

.PHONY: test test-unit test-integration test-e2e coverage lint clean install

# 默认目标
all: test

# 安装依赖
install:
	pip install pytest pytest-cov

# 运行所有测试
test:
	python -m pytest tests/ -v

# 运行单元测试
test-unit:
	python -m pytest tests/unit/ -v

# 运行集成测试
test-integration:
	python -m pytest tests/integration/ -v

# 运行端到端测试
test-e2e:
	python -m pytest tests/e2e/ -v

# 生成覆盖率报告
coverage:
	python -m pytest tests/ --cov=skills --cov-report=term-missing --cov-report=json:coverage_report.json

# 快速测试（跳过慢测试）
test-fast:
	python -m pytest tests/ -v -m "not slow"

# 清理
clean:
	rm -rf __pycache__ .pytest_cache *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# 代码检查（如果有安装flake8/black）
lint:
	@echo "Linting not configured yet"

# 帮助
help:
	@echo "Available targets:"
	@echo "  install          - Install test dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e         - Run end-to-end tests only"
	@echo "  test-fast        - Run tests (skip slow ones)"
	@echo "  coverage         - Generate coverage report"
	@echo "  clean            - Clean up cache files"
	@echo "  help             - Show this help"
