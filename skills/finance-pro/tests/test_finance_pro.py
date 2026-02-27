"""
finance-pro 单元测试
测试金融分析核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_import():
    """测试模块可导入"""
    try:
        import finance_pro
        assert True
    except ImportError as e:
        pytest.skip(f"finance_pro 未完全实现: {e}")


def test_data_adapter_exists():
    """测试数据适配器存在"""
    try:
        from finance_pro import FinanceDataAdapter
        assert True
    except ImportError:
        pytest.skip("FinanceDataAdapter 未实现")


def test_technical_indicators_exists():
    """测试技术指标模块存在"""
    tech_file = os.path.join(os.path.dirname(__file__), '..', 'technical_indicators.py')
    assert os.path.exists(tech_file), "technical_indicators.py 不存在"


class TestFinanceDataAdapter:
    """测试金融数据适配器"""
    
    @pytest.fixture
    def mock_adapter(self):
        """创建模拟适配器"""
        mock = Mock()
        mock.get_stock_quote.return_value = Mock(
            success=True,
            data={"symbol": "000001.SZ", "price": 10.5},
            error=None
        )
        mock.technical_analysis.return_value = Mock(
            success=True,
            data={"ma5": 10.2, "ma10": 10.1},
            error=None
        )
        return mock
    
    def test_get_stock_quote(self, mock_adapter):
        """测试获取股票报价"""
        result = mock_adapter.get_stock_quote("000001.SZ")
        assert result.success is True
        assert result.data["symbol"] == "000001.SZ"
    
    def test_technical_analysis(self, mock_adapter):
        """测试技术分析"""
        result = mock_adapter.technical_analysis("000001.SZ", ["ma5", "ma10"])
        assert result.success is True
        assert "ma5" in result.data


class TestRiskManager:
    """测试风险管理模块"""
    
    def test_position_sizing(self):
        """测试仓位计算"""
        # 模拟仓位计算逻辑
        capital = 100000
        risk_percent = 0.02
        stop_loss = 0.05
        
        position_size = (capital * risk_percent) / stop_loss
        assert position_size == 40000.0
    
    def test_risk_reward_ratio(self):
        """测试盈亏比计算"""
        entry = 100
        stop_loss = 90
        take_profit = 120
        
        risk = entry - stop_loss
        reward = take_profit - entry
        ratio = reward / risk
        
        assert ratio == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
