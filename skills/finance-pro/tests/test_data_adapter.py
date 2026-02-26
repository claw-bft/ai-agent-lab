#!/usr/bin/env python3
"""
Test suite for finance-pro data_adapter module
Tests the multi-source financial data adapter
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock
from data_adapter import (
    DataSourceType,
    AkshareProvider,
    TushareProvider,
    FinanceDataAdapter,
    get_adapter,
    get_stock_quote,
    get_stock_history,
    search_stocks
)


class TestDataSourceType(unittest.TestCase):
    """Test DataSourceType enum"""
    
    def test_enum_values(self):
        """Test enum values are correct"""
        self.assertEqual(DataSourceType.AKSHARE.value, "akshare")
        self.assertEqual(DataSourceType.TUSHARE.value, "tushare")
        self.assertEqual(DataSourceType.YFINANCE.value, "yfinance")


class TestAkshareProvider(unittest.TestCase):
    """Test AkshareProvider"""
    
    def setUp(self):
        self.provider = AkshareProvider()
    
    def test_get_name(self):
        """Test provider name"""
        self.assertEqual(self.provider.get_name(), "Akshare")
    
    def test_normalize_symbol(self):
        """Test symbol normalization"""
        # Test with exchange suffix
        result = self.provider._normalize_symbol("600519.SH")
        self.assertEqual(result, "600519")
        
        # Test without suffix
        result = self.provider._normalize_symbol("000001")
        self.assertEqual(result, "000001")
    
    @patch.object(AkshareProvider, '_try_import')
    def test_is_available_true(self, mock_import):
        """Test is_available when akshare is available"""
        mock_import.return_value = None
        provider = AkshareProvider()
        provider._ak = Mock()  # Mock the akshare module
        self.assertTrue(provider.is_available())
    
    def test_is_available_false(self):
        """Test is_available when akshare is not available"""
        self.provider._ak = None
        self.assertFalse(self.provider.is_available())
    
    def test_get_stock_quote_not_available(self):
        """Test get_stock_quote when akshare not available"""
        self.provider._ak = None
        result = self.provider.get_stock_quote("600519.SH")
        self.assertFalse(result["success"])
        self.assertIn("akshare未安装", result["error"])
    
    @patch.object(AkshareProvider, 'is_available')
    def test_get_stock_quote_success(self, mock_available):
        """Test successful stock quote retrieval"""
        mock_available.return_value = True
        
        # Mock akshare module
        mock_ak = Mock()
        mock_df = Mock()
        mock_df.empty = False
        
        # Create mock row data
        mock_row = Mock()
        mock_row.get.side_effect = lambda key, default: {
            '名称': '贵州茅台',
            '最新价': 1800.50,
            '涨跌幅': 1.5,
            '涨跌额': 26.5,
            '成交量': 10000,
            '成交额': 18000000,
            '最高': 1810.0,
            '最低': 1790.0,
            '今开': 1795.0,
            '昨收': 1774.0,
            '市盈率-动态': 30.5,
            '市净率': 8.2,
            '总市值': 2200000000000
        }.get(key, default)
        
        mock_df.iloc = [mock_row]
        mock_df.__getitem__ = Mock(return_value=mock_df)
        mock_ak.stock_zh_a_spot_em.return_value = mock_df
        
        self.provider._ak = mock_ak
        
        result = self.provider.get_stock_quote("600519.SH")
        self.assertTrue(result["success"])
        self.assertEqual(result["name"], "贵州茅台")
        self.assertEqual(result["price"], 1800.50)
    
    @patch.object(AkshareProvider, 'is_available')
    def test_get_stock_quote_not_found(self, mock_available):
        """Test stock quote when stock not found"""
        mock_available.return_value = True
        
        mock_ak = Mock()
        mock_df = Mock()
        mock_df.empty = True
        mock_df.__getitem__ = Mock(return_value=mock_df)
        mock_ak.stock_zh_a_spot_em.return_value = mock_df
        
        self.provider._ak = mock_ak
        
        result = self.provider.get_stock_quote("999999.SH")
        self.assertFalse(result["success"])
        self.assertIn("未找到股票", result["error"])
    
    @patch.object(AkshareProvider, 'is_available')
    def test_get_stock_history_success(self, mock_available):
        """Test successful history retrieval"""
        mock_available.return_value = True
        
        mock_ak = Mock()
        mock_df = Mock()
        mock_df.empty = False
        mock_df.to_dict.return_value = [
            {"日期": "2024-01-01", "开盘": 100, "收盘": 105, "最高": 106, "最低": 99, "成交量": 1000}
        ]
        mock_ak.stock_zh_a_hist.return_value = mock_df
        
        self.provider._ak = mock_ak
        
        result = self.provider.get_stock_history("600519.SH", days=30)
        self.assertTrue(result["success"])
        self.assertEqual(result["days"], 30)
    
    @patch.object(AkshareProvider, 'is_available')
    def test_search_stocks(self, mock_available):
        """Test stock search"""
        mock_available.return_value = True
        
        mock_ak = Mock()
        mock_df = Mock()
        
        # Mock pandas str.contains
        mock_series = Mock()
        mock_series.str = Mock()
        mock_series.str.contains = Mock(return_value=Mock())
        
        mock_df.__getitem__ = Mock(return_value=mock_df)
        mock_df.head.return_value = mock_df
        mock_df.iterrows.return_value = iter([
            (0, {"代码": "600519", "名称": "贵州茅台", "最新价": 1800.0, "涨跌幅": 1.5})
        ])
        mock_ak.stock_zh_a_spot_em.return_value = mock_df
        
        self.provider._ak = mock_ak
        self.provider._pd = Mock()
        
        result = self.provider.search_stocks("茅台")
        self.assertTrue(result["success"])
        self.assertEqual(result["keyword"], "茅台")


class TestTushareProvider(unittest.TestCase):
    """Test TushareProvider"""
    
    def setUp(self):
        self.provider = TushareProvider()
    
    def test_get_name(self):
        """Test provider name"""
        self.assertEqual(self.provider.get_name(), "Tushare")
    
    def test_is_available_no_token(self):
        """Test is_available without token"""
        self.provider._ts = Mock()
        self.provider._pro = None
        self.assertFalse(self.provider.is_available())
    
    def test_is_available_no_import(self):
        """Test is_available when tushare not installed"""
        self.provider._ts = None
        self.provider._pro = None
        self.assertFalse(self.provider.is_available())
    
    def test_get_stock_quote_not_available(self):
        """Test get_stock_quote when not available"""
        self.provider._ts = None
        result = self.provider.get_stock_quote("600519.SH")
        self.assertFalse(result["success"])
        self.assertIn("Tushare未安装或未配置TOKEN", result["error"])


class TestFinanceDataAdapter(unittest.TestCase):
    """Test FinanceDataAdapter"""
    
    def setUp(self):
        self.adapter = FinanceDataAdapter()
    
    def test_init(self):
        """Test adapter initialization"""
        self.assertIsNotNone(self.adapter)
        self.assertIsInstance(self.adapter.providers, dict)
    
    def test_get_available_sources(self):
        """Test getting available sources"""
        sources = self.adapter.get_available_sources()
        self.assertIsInstance(sources, list)
    
    @patch.object(FinanceDataAdapter, '_get_provider')
    def test_get_stock_quote(self, mock_get_provider):
        """Test get_stock_quote"""
        mock_provider = Mock()
        mock_provider.get_name.return_value = "TestProvider"
        mock_provider.get_stock_quote.return_value = {"success": True, "price": 100}
        mock_get_provider.return_value = mock_provider
        
        result = self.adapter.get_stock_quote("600519.SH")
        self.assertTrue(result["success"])
        self.assertEqual(result["provider"], "TestProvider")
    
    def test_get_stock_quote_no_provider(self):
        """Test get_stock_quote with no provider"""
        self.adapter.providers = {}
        result = self.adapter.get_stock_quote("600519.SH")
        self.assertFalse(result["success"])
        self.assertIn("没有可用的数据源", result["error"])
    
    @patch.object(FinanceDataAdapter, '_get_provider')
    def test_get_stock_history(self, mock_get_provider):
        """Test get_stock_history"""
        mock_provider = Mock()
        mock_provider.get_name.return_value = "TestProvider"
        mock_provider.get_stock_history.return_value = {"success": True, "data": []}
        mock_get_provider.return_value = mock_provider
        
        result = self.adapter.get_stock_history("600519.SH", days=30)
        self.assertTrue(result["success"])
    
    @patch.object(FinanceDataAdapter, '_get_provider')
    def test_search_stocks(self, mock_get_provider):
        """Test search_stocks"""
        mock_provider = Mock()
        mock_provider.get_name.return_value = "TestProvider"
        mock_provider.search_stocks.return_value = {"success": True, "stocks": []}
        mock_get_provider.return_value = mock_provider
        
        result = self.adapter.search_stocks("茅台")
        self.assertTrue(result["success"])
    
    def test_get_provider_with_source(self):
        """Test _get_provider with specific source"""
        mock_provider = Mock()
        self.adapter.providers[DataSourceType.AKSHARE] = mock_provider
        
        result = self.adapter._get_provider(DataSourceType.AKSHARE)
        self.assertEqual(result, mock_provider)
    
    def test_get_provider_default(self):
        """Test _get_provider with default selection"""
        mock_ak = Mock()
        self.adapter.providers[DataSourceType.AKSHARE] = mock_ak
        
        result = self.adapter._get_provider()
        self.assertEqual(result, mock_ak)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience module-level functions"""
    
    @patch('data_adapter.get_adapter')
    def test_get_stock_quote(self, mock_get_adapter):
        """Test get_stock_quote convenience function"""
        mock_adapter = Mock()
        mock_adapter.get_stock_quote.return_value = {"success": True}
        mock_get_adapter.return_value = mock_adapter
        
        result = get_stock_quote("600519.SH")
        self.assertTrue(result["success"])
        mock_adapter.get_stock_quote.assert_called_once_with("600519.SH")
    
    @patch('data_adapter.get_adapter')
    def test_get_stock_history(self, mock_get_adapter):
        """Test get_stock_history convenience function"""
        mock_adapter = Mock()
        mock_adapter.get_stock_history.return_value = {"success": True}
        mock_get_adapter.return_value = mock_adapter
        
        result = get_stock_history("600519.SH", days=30)
        self.assertTrue(result["success"])
        mock_adapter.get_stock_history.assert_called_once_with("600519.SH", 30)
    
    @patch('data_adapter.get_adapter')
    def test_search_stocks(self, mock_get_adapter):
        """Test search_stocks convenience function"""
        mock_adapter = Mock()
        mock_adapter.search_stocks.return_value = {"success": True}
        mock_get_adapter.return_value = mock_adapter
        
        result = search_stocks("茅台")
        self.assertTrue(result["success"])
        mock_adapter.search_stocks.assert_called_once_with("茅台")


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_adapter_singleton(self):
        """Test that get_adapter returns singleton"""
        adapter1 = get_adapter()
        adapter2 = get_adapter()
        self.assertIs(adapter1, adapter2)
    
    def test_full_flow_mocked(self):
        """Test full flow with mocked dependencies"""
        with patch.object(AkshareProvider, 'is_available', return_value=True):
            with patch.object(AkshareProvider, 'get_stock_quote') as mock_quote:
                mock_quote.return_value = {
                    "success": True,
                    "name": "贵州茅台",
                    "price": 1800.50
                }
                
                adapter = FinanceDataAdapter()
                result = adapter.get_stock_quote("600519.SH")
                
                self.assertTrue(result["success"])


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestDataSourceType,
        TestAkshareProvider,
        TestTushareProvider,
        TestFinanceDataAdapter,
        TestConvenienceFunctions,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
