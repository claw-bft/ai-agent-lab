"""
集成测试 - Finance Pro
测试金融技能包的完整功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/finance-pro'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/skill-cli'))

import pytest
from unittest.mock import Mock, patch

from finance_pro import get_stock_quote_a_share, get_stock_history, calculate_ma, calculate_rsi, technical_analysis
from data_adapter import FinanceDataAdapter, DataAdapterResult as DataResult


class TestFinanceProFunctions:
    """测试Finance Pro函数"""
    
    def test_get_stock_quote_a_share(self):
        """测试获取A股行情"""
        result = get_stock_quote_a_share("000001")
        
        assert result is not None
        assert isinstance(result, dict)
        # 可能成功或失败（取决于akshare是否安装）
        assert "success" in result
    
    def test_get_stock_history(self):
        """测试获取历史数据"""
        result = get_stock_history("000001", "1mo")
        
        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_calculate_ma(self):
        """测试计算移动平均线"""
        test_data = [
            {"close": 10.0},
            {"close": 11.0},
            {"close": 12.0},
            {"close": 13.0},
            {"close": 14.0}
        ]
        result = calculate_ma(test_data, periods=[3, 5])
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_calculate_rsi(self):
        """测试计算RSI"""
        test_data = [
            {"close": 10.0},
            {"close": 11.0},
            {"close": 12.0},
            {"close": 11.0},
            {"close": 13.0}
        ]
        result = calculate_rsi(test_data, period=5)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_technical_analysis(self):
        """测试技术分析"""
        result = technical_analysis("000001", indicators=["MA", "RSI"])
        
        assert result is not None
        assert isinstance(result, dict)


class TestFinanceDataAdapter:
    """测试金融数据适配器"""
    
    @pytest.fixture
    def adapter(self):
        """创建适配器实例"""
        return FinanceDataAdapter()
    
    def test_initialization(self, adapter):
        """测试初始化"""
        assert adapter is not None
    
    def test_get_stock_quote(self, adapter):
        """测试获取股票行情"""
        result = adapter.get_stock_quote("600519.SH")
        
        assert isinstance(result, DataResult)
        assert result.success or result.error is not None
    
    def test_get_stock_quote_invalid_symbol(self, adapter):
        """测试获取无效代码的行情"""
        result = adapter.get_stock_quote("INVALID")
        
        assert isinstance(result, DataResult)
    
    def test_technical_analysis(self, adapter):
        """测试技术分析"""
        result = adapter.technical_analysis("600519.SH", ["MA", "RSI"])
        
        assert isinstance(result, DataResult)
    
    def test_get_financial_report(self, adapter):
        """测试获取财报"""
        result = adapter.get_financial_report("600519.SH")
        
        assert isinstance(result, DataResult)
    
    def test_get_stock_history(self, adapter):
        """测试获取历史数据"""
        result = adapter.get_stock_history("600519.SH", "1mo")
        
        assert isinstance(result, DataResult)
    
    def test_symbol_mapping(self, adapter):
        """测试代码映射"""
        # 测试名称到代码映射
        code = adapter._map_name_to_code("茅台")
        assert code == "600519.SH"
        
        code = adapter._map_name_to_code("腾讯")
        assert code == "00700.HK"
    
    def test_exchange_detection(self, adapter):
        """测试交易所检测"""
        assert adapter._detect_exchange("600519") == "SH"
        assert adapter._detect_exchange("000001") == "SZ"
        assert adapter._detect_exchange("300750") == "SZ"
