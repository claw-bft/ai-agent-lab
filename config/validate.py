"""
配置验证脚本 - 检查配置完整性和有效性
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager


def validate_config() -> dict:
    """
    验证配置完整性
    
    Returns:
        验证结果
    """
    print("[Validate] 开始验证配置...\n")
    
    config = ConfigManager()
    
    # 基础验证
    result = config.validate()
    
    print("=" * 50)
    print("配置验证结果")
    print("=" * 50)
    
    # 有效配置
    if result['valid']:
        print(f"\n✅ 有效配置 ({len(result['valid'])}):")
        for item in result['valid']:
            print(f"   - {item}")
    
    # 无效配置
    if result['invalid']:
        print(f"\n❌ 无效配置 ({len(result['invalid'])}):")
        for item in result['invalid']:
            print(f"   - {item}")
    
    # 缺失配置
    if result['missing']:
        print(f"\n⚠️ 缺失配置 ({len(result['missing'])}):")
        for item in result['missing']:
            print(f"   - {item}")
    
    # 已配置的服务列表
    all_creds = config.get_all_credentials()
    if all_creds:
        print(f"\n📋 已配置服务 ({len(all_creds)}):")
        for service, keys in all_creds.items():
            print(f"   - {service}: {', '.join(keys)}")
    
    # 设置项
    all_settings = config.get_all_settings()
    if all_settings:
        print(f"\n⚙️ 普通配置 ({len(all_settings)} 个分区):")
        for section, keys in all_settings.items():
            print(f"   - {section}: {len(keys)} 项")
    
    print("\n" + "=" * 50)
    
    # 总体状态
    is_healthy = len(result['valid']) > 0 and len(result['missing']) == 0
    
    if is_healthy:
        print("✅ 配置健康")
    elif result['valid']:
        print("⚠️ 配置部分有效，存在缺失项")
    else:
        print("❌ 配置异常，需要修复")
    
    return {
        'healthy': is_healthy,
        'valid_count': len(result['valid']),
        'missing_count': len(result['missing']),
        'invalid_count': len(result['invalid']),
        'services': list(all_creds.keys())
    }


def check_specific_service(service: str, key: str = None) -> bool:
    """
    检查特定服务配置
    
    Args:
        service: 服务名称
        key: 特定键名（可选）
        
    Returns:
        是否存在
    """
    config = ConfigManager()
    
    if key:
        value = config.get_credential(service, key)
        exists = value is not None and value != ""
        status = "✅" if exists else "❌"
        print(f"{status} {service}.{key}: {'已配置' if exists else '未配置'}")
        return exists
    else:
        all_creds = config.get_all_credentials()
        exists = service in all_creds
        status = "✅" if exists else "❌"
        print(f"{status} {service}: {'已配置' if exists else '未配置'}")
        if exists:
            print(f"   包含: {', '.join(all_creds[service])}")
        return exists


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='验证配置')
    parser.add_argument('--service', type=str, help='检查特定服务')
    parser.add_argument('--key', type=str, help='检查特定键')
    
    args = parser.parse_args()
    
    if args.service:
        check_specific_service(args.service, args.key)
    else:
        result = validate_config()
        sys.exit(0 if result['healthy'] else 1)


if __name__ == '__main__':
    main()
