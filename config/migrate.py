"""
配置迁移脚本 - 从 ~/.bashrc 迁移现有配置
"""
import os
import re
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager


def extract_env_from_bashrc(bashrc_path: str = None) -> dict:
    """
    从 ~/.bashrc 提取环境变量
    
    Returns:
        {服务名: {键名: 值}}
    """
    if not bashrc_path:
        bashrc_path = Path.home() / '.bashrc'
    else:
        bashrc_path = Path(bashrc_path)
    
    if not bashrc_path.exists():
        print(f"[Migrate] 未找到 {bashrc_path}")
        return {}
    
    env_vars = {}
    
    with open(bashrc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 export KEY="value" 格式
    pattern = r'export\s+(\w+)="([^"]*)"'
    matches = re.findall(pattern, content)
    
    for key, value in matches:
        # 映射到服务结构
        if 'VERCEL' in key.upper():
            if 'vercel' not in env_vars:
                env_vars['vercel'] = {}
            env_vars['vercel']['token'] = value
        elif 'GITHUB' in key.upper() or 'GH_' in key.upper():
            if 'github' not in env_vars:
                env_vars['github'] = {}
            if 'TOKEN' in key.upper():
                env_vars['github']['token'] = value
        elif 'FEISHU' in key.upper():
            if 'feishu' not in env_vars:
                env_vars['feishu'] = {}
            if 'APP_ID' in key.upper():
                env_vars['feishu']['app_id'] = value
            elif 'APP_SECRET' in key.upper():
                env_vars['feishu']['app_secret'] = value
        elif 'OPENAI' in key.upper() or 'ANTHROPIC' in key.upper():
            if 'ai' not in env_vars:
                env_vars['ai'] = {}
            if 'KEY' in key.upper() or 'API_KEY' in key.upper():
                env_vars['ai']['api_key'] = value
    
    return env_vars


def migrate_config(dry_run: bool = False) -> dict:
    """
    执行配置迁移
    
    Args:
        dry_run: 如果为 True，只显示将要迁移的内容而不实际执行
        
    Returns:
        迁移结果统计
    """
    print("[Migrate] 开始从 ~/.bashrc 迁移配置...")
    
    # 提取环境变量
    env_vars = extract_env_from_bashrc()
    
    if not env_vars:
        print("[Migrate] 未找到可迁移的配置")
        return {'migrated': 0, 'services': []}
    
    print(f"[Migrate] 发现 {len(env_vars)} 个服务的配置")
    
    if dry_run:
        print("\n[DRY RUN] 将要迁移以下内容：")
        for service, keys in env_vars.items():
            print(f"  {service}:")
            for key in keys:
                print(f"    - {key}")
        return {'migrated': 0, 'services': list(env_vars.keys())}
    
    # 执行迁移
    config = ConfigManager()
    migrated_count = 0
    
    for service, keys in env_vars.items():
        for key, value in keys.items():
            if value:  # 只迁移非空值
                config.set_credential(service, key, value)
                migrated_count += 1
                print(f"[Migrate] 已迁移 {service}.{key}")
    
    print(f"\n[Migrate] 完成！共迁移 {migrated_count} 个凭证")
    return {
        'migrated': migrated_count,
        'services': list(env_vars.keys())
    }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='迁移配置到统一管理系统')
    parser.add_argument('--dry-run', action='store_true', 
                        help='仅显示将要迁移的内容，不实际执行')
    parser.add_argument('--bashrc', type=str, default=None,
                        help='指定 bashrc 文件路径')
    
    args = parser.parse_args()
    
    result = migrate_config(dry_run=args.dry_run)
    
    if result['migrated'] > 0 or args.dry_run:
        print(f"\n服务列表: {', '.join(result['services'])}")


if __name__ == '__main__':
    main()
