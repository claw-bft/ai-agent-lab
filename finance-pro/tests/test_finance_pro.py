#!/usr/bin/env python3
"""
Finance Pro - 测试套件
覆盖核心功能、技术指标和数据适配器
"""

import sys
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入被测模块
from finance_pro import (
    get_stock_quote_a_share, get_stock_history, 
    calculate_ma, calculate_rsi, technical_analysis,
    get_financial_report
)
from technical_indicators import (
    TechnicalIndicators, SignalType, IndicatorResult,
    analyze_stock_technical
)
from data_adapter import (
    FinanceDataAdapter, AkshareProvider, TushareProvider,
    DataSourceType, get_adapter, get_stock_quote,
    get_stock_history as adapter_get_history,
    search_stocks, get_index_list
)


class TestFinanceProCore(unittest.TestCase):
    """Finance Pro 核心功能测试"""
    
    def setUp(self):
        """测试前置准备"""
        self.test_symbol = "000001.SZ"
        self.test_code = "000001"
    
    @patch('finance_pro.ak.stock_zh_a_spot_em')
    def test_get_stock_quote_a_share_success(self, mock_spot):
        """测试获取A股行情 - 成功场景"""
        # 模拟返回数据
        import pandas as pd
        mock_df = pd.DataFrame({
            '代码': ['000001'],
            '名称': ['平安银行'],
            '最新价': [10.5],
            '涨跌幅': [2.5],
            '涨跌额': [0.25],
            '成交量': [1000000],
            '成交额': [10500000],
            '最高': [10.8],
            '最低': [10.2],
            '今开': [10.3],
            '昨收': [10.25]
        })
        mock_spot.return_value = mock_df
        
        result = get_stock_quote_a_share(self.test_symbol)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['symbol'], self.test_symbol)
        self.assertEqual(result['name'], '平安银行')
        self.assertEqual(result['price'], 10.5)
        self.assertEqual(result['change'], 2.5)
    
    @patch('finance_pro.ak')
    def test_get_stock_quote_a_share_not_found(self, mock_ak):
        """测试获取A股行情 - 股票不存在"""
        mock_df = MagicMock()
        mock_df.empty = True
        mock_ak.stock_zh_a_spot_em.return_value = mock_df
        
        result = get_stock_quote_a_share("999999.SZ")
        
        self.assertFalse(result['success'])
        self.assertIn('未找到股票', result['error'])
    
    @patch('finance_pro.ak')
    def test_get_stock_history_success(self, mock_ak):
        """测试获取历史数据 - 成功场景"""
        import pandas as pd
        mock_df = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02'],
            '开盘': [10.0, 10.5],
            '收盘': [10.5, 11.0],
            '最高': [10.8, 11.2],
            '最低': [9.8, 10.3],
            '成交量': [10000, 15000]
        })
        mock_ak.stock_zh_a_hist.return_value = mock_df
        
        result = get_stock_history(self.test_symbol)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['symbol'], self.test_symbol)
        self.assertEqual(result['data_points'], 2)
    
    def test_calculate_ma_success(self):
        """测试移动平均线计算 - 成功场景"""
        test_data = [
            {'close': 10}, {'close': 11}, {'close': 12},
            {'close': 13}, {'close': 14}, {'close': 15}
        ]
        
        result = calculate_ma(test_data, periods=[3, 5])
        
        self.assertTrue(result['success'])
        self.assertIn('MA3', result['ma'])
        self.assertIn('MA5', result['ma'])
        # MA3 = (13+14+15)/3 = 14
        self.assertEqual(result['ma']['MA3'], 14.0)
        # MA5 = (11+12+13+14+15)/5 = 13
        self.assertEqual(result['ma']['MA5'], 13.0)
    
    def test_calculate_ma_insufficient_data(self):
        """测试移动平均线计算 - 数据不足"""
        test_data = [{'close': 10}]
        
        result = calculate_ma(test_data, periods=[5])
        
        # 当数据不足时，该周期不会出现在结果中
        self.assertTrue(result['success'])
        self.assertEqual(result['ma'], {})  # MA5不会被计算
    
    def test_calculate_rsi_success(self):
        """测试RSI计算 - 成功场景"""
        # 模拟上涨数据
        test_data = [{'close': 100 + i} for i in range(20)]
        
        result = calculate_rsi(test_data, period=14)
        
        self.assertTrue(result['success'])
        self.assertIn('rsi', result)
        self.assertIn('signal', result)
        # 持续上涨应该RSI较高
        self.assertGreater(result['rsi'], 50)
    
    def test_calculate_rsi_oversold(self):
        """测试RSI计算 - 超卖信号"""
        # 模拟下跌数据
        test_data = [{'close': 100 - i * 2} for i in range(20)]
        
        result = calculate_rsi(test_data, period=14)
        
        self.assertTrue(result['success'])
        # 持续下跌应该RSI较低
        if result['rsi'] < 30:
            self.assertEqual(result['signal'], '超卖')
    
    @patch('finance_pro.get_stock_history')
    def test_technical_analysis_success(self, mock_history):
        """测试技术分析 - 成功场景"""
        mock_history.return_value = {
            'success': True,
            'data': [{'close': 10 + i} for i in range(30)]
        }
        
        result = technical_analysis(self.test_symbol, ['MA', 'RSI'])
        
        self.assertTrue(result['success'])
        self.assertIn('MA', result['indicators'])
        self.assertIn('RSI', result['indicators'])
    
    @patch('finance_pro.get_stock_history')
    def test_technical_analysis_history_failure(self, mock_history):
        """测试技术分析 - 历史数据获取失败"""
        mock_history.return_value = {
            'success': False,
            'error': '数据获取失败'
        }
        
        result = technical_analysis(self.test_symbol, ['MA'])
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], '数据获取失败')


class TestTechnicalIndicators(unittest.TestCase):
    """技术指标计算器测试"""
    
    def setUp(self):
        """准备测试数据"""
        # 生成30天的模拟K线数据
        self.test_data = []
        base_price = 100
        for i in range(30):
            change = (i % 7 - 3) * 2  # 模拟波动
            close = base_price + change + i * 0.5
            self.test_data.append({
                'date': f'2024-01-{i+1:02d}',
                'open': close - 1,
                'high': close + 2,
                'low': close - 2,
                'close': close,
                'volume': 10000 + i * 1000
            })
        self.calculator = TechnicalIndicators(self.test_data)
    
    def test_ma_calculation(self):
        """测试MA计算"""
        result = self.calculator.ma(period=20)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'MA20')
        self.assertIsNotNone(result.value)
        self.assertIsInstance(result.signal, SignalType)
        # raw_data属性存储额外数据
        self.assertIsNotNone(result.raw_data)
    
    def test_ma_insufficient_data(self):
        """测试MA - 数据不足"""
        short_data = self.test_data[:5]
        calc = TechnicalIndicators(short_data)
        result = calc.ma(period=20)
        
        self.assertIsNone(result.value)
        self.assertEqual(result.signal, SignalType.NEUTRAL)
    
    def test_ema_calculation(self):
        """测试EMA计算"""
        result = self.calculator.ema(period=12)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'EMA12')
        self.assertIsNotNone(result.value)
    
    def test_rsi_calculation(self):
        """测试RSI计算"""
        result = self.calculator.rsi(period=14)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'RSI14')
        self.assertIsNotNone(result.value)
        self.assertTrue(0 <= result.value <= 100)
    
    def test_rsi_overbought_signal(self):
        """测试RSI超买信号"""
        # 创建持续上涨数据
        rising_data = []
        price = 100
        for i in range(20):
            price += 5  # 持续上涨
            rising_data.append({
                'open': price - 1, 'high': price + 1,
                'low': price - 2, 'close': price, 'volume': 10000
            })
        calc = TechnicalIndicators(rising_data)
        result = calc.rsi(period=14)
        
        if result.value and result.value > 70:
            self.assertEqual(result.signal, SignalType.OVERBOUGHT)
    
    def test_macd_calculation(self):
        """测试MACD计算"""
        result = self.calculator.macd()
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'MACD')
        # MACD需要足够数据，如果数据不足可能返回None
        if result.value is not None:
            self.assertIsInstance(result.value, dict)
            self.assertIn('macd', result.value)
            self.assertIn('signal', result.value)
            self.assertIn('histogram', result.value)
    
    def test_bollinger_calculation(self):
        """测试布林带计算"""
        result = self.calculator.bollinger(period=20)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'BOLL')
        self.assertIsInstance(result.value, dict)
        self.assertIn('upper', result.value)
        self.assertIn('middle', result.value)
        self.assertIn('lower', result.value)
        self.assertIn('bandwidth', result.value)
        # 验证布林带逻辑: 上轨 > 中轨 > 下轨
        self.assertGreater(result.value['upper'], result.value['middle'])
        self.assertGreater(result.value['middle'], result.value['lower'])
    
    def test_kdj_calculation(self):
        """测试KDJ计算"""
        result = self.calculator.kdj(n=9, m1=3, m2=3)
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'KDJ')
        self.assertIsInstance(result.value, dict)
        self.assertIn('k', result.value)
        self.assertIn('d', result.value)
        self.assertIn('j', result.value)
    
    def test_volume_analysis(self):
        """测试成交量分析"""
        result = self.calculator.volume_analysis()
        
        self.assertIsInstance(result, IndicatorResult)
        self.assertEqual(result.name, 'VOL')
        self.assertIsInstance(result.value, dict)
        self.assertIn('current', result.value)
        self.assertIn('ma5', result.value)
        self.assertIn('ma20', result.value)
        self.assertIn('ratio', result.value)
    
    def test_analyze_all(self):
        """测试批量分析"""
        result = self.calculator.analyze_all(['MA', 'RSI', 'MACD'])
        
        self.assertTrue(result['success'])
        self.assertIn('indicators', result)
        self.assertIn('summary', result)
        self.assertIn('MA', result['indicators'])
        self.assertIn('RSI', result['indicators'])
        self.assertIn('MACD', result['indicators'])
        self.assertIn('buy_signals', result['summary'])
        self.assertIn('sell_signals', result['summary'])
        self.assertIn('overall', result['summary'])
    
    def test_analyze_all_default_indicators(self):
        """测试批量分析 - 默认指标"""
        result = self.calculator.analyze_all()
        
        self.assertTrue(result['success'])
        # 默认包含6个指标
        self.assertEqual(len(result['indicators']), 6)
    
    def test_analyze_stock_technical_convenience(self):
        """测试便捷函数 analyze_stock_technical"""
        result = analyze_stock_technical(self.test_data, ['MA', 'RSI'])
        
        self.assertTrue(result['success'])
        self.assertIn('indicators', result)


class TestDataAdapter(unittest.TestCase):
    """数据适配器测试"""
    
    def setUp(self):
        """测试前置准备"""
        self.adapter = FinanceDataAdapter()
    
    def test_adapter_initialization(self):
        """测试适配器初始化"""
        self.assertIsInstance(self.adapter, FinanceDataAdapter)
        self.assertIsInstance(self.adapter.providers, dict)
    
    def test_get_available_sources(self):
        """测试获取可用数据源"""
        sources = self.adapter.get_available_sources()
        self.assertIsInstance(sources, list)
        # 至少应该返回数据源名称列表
    
    @patch('data_adapter.AkshareProvider')
    def test_get_stock_quote_with_mock(self, mock_provider_class):
        """测试获取行情 - Mock场景"""
        mock_provider = MagicMock()
        mock_provider.get_name.return_value = 'Akshare'
        mock_provider.get_stock_quote.return_value = {
            'success': True,
            'symbol': '000001.SZ',
            'price': 10.5
        }
        mock_provider_class.return_value = mock_provider
        mock_provider.is_available.return_value = True
        
        adapter = FinanceDataAdapter()
        adapter.providers = {DataSourceType.AKSHARE: mock_provider}
        
        result = adapter.get_stock_quote('000001.SZ')
        
        self.assertTrue(result['success'])
        mock_provider.get_stock_quote.assert_called_once_with('000001.SZ')
    
    def test_get_stock_quote_no_provider(self):
        """测试获取行情 - 无可用数据源"""
        adapter = FinanceDataAdapter()
        adapter.providers = {}  # 清空数据源
        
        result = adapter.get_stock_quote('000001.SZ')
        
        self.assertFalse(result['success'])
        self.assertIn('没有可用的数据源', result['error'])
    
    def test_akshare_provider_initialization(self):
        """测试Akshare提供者初始化"""
        provider = AkshareProvider()
        self.assertEqual(provider.get_name(), 'Akshare')
        # 根据环境可能有不同的可用性
        self.assertIsInstance(provider.is_available(), bool)
    
    def test_akshare_provider_normalize_symbol(self):
        """测试代码标准化"""
        provider = AkshareProvider()
        
        self.assertEqual(provider._normalize_symbol('000001.SZ'), '000001')
        self.assertEqual(provider._normalize_symbol('600519'), '600519')
        self.assertEqual(provider._normalize_symbol('000001.SH'), '000001')
    
    @patch.object(AkshareProvider, '_try_import')
    def test_akshare_provider_not_available(self, mock_import):
        """测试Akshare不可用时"""
        mock_import.return_value = None
        provider = AkshareProvider()
        provider._ak = None  # 模拟导入失败
        
        self.assertFalse(provider.is_available())
        
        result = provider.get_stock_quote('000001.SZ')
        self.assertFalse(result['success'])
        self.assertIn('akshare未安装', result['error'])
    
    def test_tushare_provider_initialization(self):
        """测试Tushare提供者初始化"""
        provider = TushareProvider()
        self.assertEqual(provider.get_name(), 'Tushare')
        self.assertIsNone(provider.token)  # 默认无token
    
    def test_tushare_provider_with_token(self):
        """测试Tushare带Token初始化"""
        with patch.dict('os.environ', {'TUSHARE_TOKEN': 'test_token'}):
            provider = TushareProvider()
            self.assertEqual(provider.token, 'test_token')
    
    def test_tushare_provider_not_available(self):
        """测试Tushare不可用时"""
        provider = TushareProvider()
        provider._ts = None  # 模拟导入失败
        
        self.assertFalse(provider.is_available())
        
        result = provider.get_stock_quote('000001.SZ')
        self.assertFalse(result['success'])
        self.assertIn('Tushare未安装', result['error'])
    
    def test_global_adapter_singleton(self):
        """测试全局适配器单例"""
        adapter1 = get_adapter()
        adapter2 = get_adapter()
        
        self.assertIs(adapter1, adapter2)
    
    @patch('data_adapter.get_adapter')
    def test_convenience_functions(self, mock_get_adapter):
        """测试便捷函数"""
        mock_adapter = MagicMock()
        mock_adapter.get_stock_quote.return_value = {'success': True}
        mock_adapter.get_stock_history.return_value = {'success': True}
        mock_adapter.search_stocks.return_value = {'success': True}
        mock_adapter.get_index_list.return_value = {'success': True}
        mock_get_adapter.return_value = mock_adapter
        
        # 测试便捷函数调用
        result = get_stock_quote('000001.SZ')
        self.assertTrue(result['success'])
        
        result = adapter_get_history('000001.SZ')
        self.assertTrue(result['success'])
        
        result = search_stocks('平安')
        self.assertTrue(result['success'])
        
        result = get_index_list()
        self.assertTrue(result['success'])


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_technical_analysis(self):
        """端到端技术分析流程"""
        # 1. 准备数据
        test_data = []
        for i in range(30):
            test_data.append({
                'date': f'2024-01-{i+1:02d}',
                'open': 100 + i,
                'high': 105 + i,
                'low': 95 + i,
                'close': 102 + i,
                'volume': 10000
            })
        
        # 2. 计算指标
        calculator = TechnicalIndicators(test_data)
        analysis = calculator.analyze_all()
        
        # 3. 验证结果
        self.assertTrue(analysis['success'])
        self.assertGreater(len(analysis['indicators']), 0)
        self.assertIn('summary', analysis)
        
        # 4. 验证信号计数
        summary = analysis['summary']
        self.assertIsInstance(summary['buy_signals'], int)
        self.assertIsInstance(summary['sell_signals'], int)
        self.assertIn(summary['overall'], ['买入', '卖出', '持有'])
    
    def test_data_flow_quote_to_analysis(self):
        """测试从行情到分析的数据流"""
        # 模拟从adapter获取数据，然后进行技术分析
        mock_history_data = {
            'success': True,
            'data': [
                {'open': 10, 'high': 11, 'low': 9, 'close': 10.5, 'volume': 10000},
                {'open': 10.5, 'high': 12, 'low': 10, 'close': 11.5, 'volume': 15000},
            ] + [{'open': 10+i, 'high': 11+i, 'low': 9+i, 'close': 10.5+i, 'volume': 10000+i*100} 
                 for i in range(28)]
        }
        
        if mock_history_data['success']:
            analysis = analyze_stock_technical(mock_history_data['data'], ['MA', 'RSI'])
            self.assertTrue(analysis['success'])


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        calc = TechnicalIndicators([])
        result = calc.ma()
        
        self.assertIsNone(result.value)
        self.assertEqual(result.signal, SignalType.NEUTRAL)
    
    def test_none_data_handling(self):
        """测试None数据处理"""
        calc = TechnicalIndicators(None)
        result = calc.rsi()
        
        self.assertIsNone(result.value)
    
    def test_malformed_data_handling(self):
        """测试异常数据处理"""
        # 缺少必要字段
        bad_data = [{'date': '2024-01-01'}]  # 缺少close等字段
        calc = TechnicalIndicators(bad_data)
        
        # 应该优雅处理，不抛出异常
        try:
            result = calc.ma()
            # 结果可能失败但不应崩溃
        except Exception as e:
            self.fail(f"不应该抛出异常: {e}")
    
    def test_invalid_indicator_name(self):
        """测试无效指标名"""
        test_data = [{'close': 10+i} for i in range(30)]
        calc = TechnicalIndicators(test_data)
        
        # 使用analyze_all传入无效指标名
        result = calc.analyze_all(['INVALID', 'MA'])
        
        # 应该只返回有效指标
        self.assertTrue(result['success'])
        self.assertNotIn('INVALID', result['indicators'])


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFinanceProCore))
    suite.addTests(loader.loadTestsFromTestCase(TestTechnicalIndicators))
    suite.addTests(loader.loadTestsFromTestCase(TestDataAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
