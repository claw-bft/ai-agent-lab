#!/usr/bin/env python3
"""
AI代码生成器 - 示例演示脚本
展示coding-pro技能包的能力，无需真实API密钥
"""

import sys
import os

# 添加技能包到路径
sys.path.insert(0, '/root/.openclaw/workspace/skills/coding-pro')

from ai_code_generator import AICodeGenerator, CodeGenerationRequest


def demo_template_generation():
    """演示模板代码生成功能（无需API密钥）"""
    print("=" * 60)
    print("🚀 Coding-Pro AI代码生成器演示")
    print("=" * 60)

    generator = AICodeGenerator()

    # 示例1: FastAPI用户认证服务
    print("\n📦 示例1: FastAPI用户认证服务")
    print("-" * 40)

    request1 = CodeGenerationRequest(
        prompt="创建一个FastAPI用户认证服务，包含注册、登录、JWT token验证",
        language="python",
        framework="fastapi",
        output_dir="./generated_examples/auth_service",
        include_tests=True,
        include_docs=True
    )

    # 使用模板生成（无需API）
    result1 = generator.generate(request1)

    if result1.success:
        print(f"✅ 生成成功！")
        print(f"   生成文件数: {len(result1.files)}")
        print(f"   依赖项: {', '.join(result1.dependencies[:5])}...")
        print(f"   输出目录: {request1.output_dir}")

        # 写入文件
        for file in result1.files:
            filepath = os.path.join(request1.output_dir, file.path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(file.content)
        print(f"   文件已写入: {request1.output_dir}")
    else:
        print(f"❌ 生成失败: {result1.error}")

    # 示例2: React组件
    print("\n📦 示例2: React待办事项组件")
    print("-" * 40)

    request2 = CodeGenerationRequest(
        prompt="创建一个React待办事项组件，支持添加、删除、标记完成",
        language="typescript",
        framework="react",
        output_dir="./generated_examples/todo_component",
        include_tests=True,
        include_docs=True
    )

    result2 = generator.generate(request2)

    if result2.success:
        print(f"✅ 生成成功！")
        print(f"   生成文件数: {len(result2.files)}")
        print(f"   依赖项: {', '.join(result2.dependencies[:5])}...")
        print(f"   输出目录: {request2.output_dir}")

        for file in result2.files:
            filepath = os.path.join(request2.output_dir, file.path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(file.content)
        print(f"   文件已写入: {request2.output_dir}")
    else:
        print(f"❌ 生成失败: {result2.error}")

    # 示例3: CLI工具
    print("\n📦 示例3: Python CLI文件处理工具")
    print("-" * 40)

    request3 = CodeGenerationRequest(
        prompt="创建一个命令行文件批量重命名工具，支持正则表达式",
        language="python",
        framework=None,
        output_dir="./generated_examples/cli_tool",
        include_tests=True,
        include_docs=True
    )

    result3 = generator.generate(request3)

    if result3.success:
        print(f"✅ 生成成功！")
        print(f"   生成文件数: {len(result3.files)}")
        print(f"   输出目录: {request3.output_dir}")

        for file in result3.files:
            filepath = os.path.join(request3.output_dir, file.path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(file.content)
        print(f"   文件已写入: {request3.output_dir}")
    else:
        print(f"❌ 生成失败: {result3.error}")

    print("\n" + "=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)
    print("\n📋 生成的示例项目:")
    print("   1. ./generated_examples/auth_service/ - FastAPI认证服务")
    print("   2. ./generated_examples/todo_component/ - React组件")
    print("   3. ./generated_examples/cli_tool/ - CLI工具")
    print("\n🔑 启用AI增强生成:")
    print("   设置环境变量: ANTHROPIC_API_KEY, OPENAI_API_KEY, 或 KIMI_API_KEY")
    print("   然后调用 generate_with_ai() 方法获取AI优化的代码")
    print("\n📖 更多信息: /root/.openclaw/workspace/skills/coding-pro/SKILL.md")


if __name__ == "__main__":
    demo_template_generation()
