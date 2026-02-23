#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书文案生成器 v0.1 - 简单版本
使用 Kimi API 生成小红书风格文案
"""

import os
import json
import requests
from datetime import datetime

# Kimi API 配置
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_BASE_URL = "https://api.kimi.com/coding/"

def generate_xhs_content(product, style="种草"):
    """
    生成小红书文案
    
    Args:
        product: 产品或主题描述
        style: 文案风格（种草/测评/教程/日常）
    
    Returns:
        dict: 包含标题、正文、标签
    """
    
    # 构建 prompt
    prompt = f"""请为以下产品/主题生成一篇小红书风格的文案：

产品/主题：{product}
风格：{style}

要求：
1. 标题要吸引人，有 emoji，15-20字
2. 正文分段，每段简短，多用 emoji
3. 语气亲切，像朋友推荐
4. 结尾加 5-8 个相关标签

请按以下格式输出：

【标题】
（标题内容）

【正文】
（正文内容）

【标签】
（标签内容）
"""
    
    try:
        # 调用 Kimi API
        headers = {
            "Authorization": f"Bearer {KIMI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "k2p5",
            "messages": [
                {"role": "system", "content": "你是一位擅长写小红书文案的博主，熟悉各种产品的种草文案写法。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 1500
        }
        
        response = requests.post(
            f"{KIMI_BASE_URL}v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return parse_content(content)
        else:
            return {
                "error": f"API 错误: {response.status_code}",
                "title": "",
                "content": "",
                "tags": ""
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "title": "",
            "content": "",
            "tags": ""
        }

def parse_content(text):
    """解析 API 返回的内容"""
    lines = text.strip().split('\n')
    
    title = ""
    content_lines = []
    tags = ""
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "【标题】" in line or "标题：" in line:
            current_section = "title"
            continue
        elif "【正文】" in line or "正文：" in line:
            current_section = "content"
            continue
        elif "【标签】" in line or "标签：" in line:
            current_section = "tags"
            continue
        
        if current_section == "title":
            title = line
            current_section = None
        elif current_section == "content":
            content_lines.append(line)
        elif current_section == "tags":
            tags = line
    
    return {
        "title": title,
        "content": "\n".join(content_lines),
        "tags": tags,
        "error": None
    }

def save_history(product, result):
    """保存生成历史"""
    history_file = "history.json"
    
    # 读取现有历史
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    # 添加新记录
    history.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product": product,
        "result": result
    })
    
    # 保存（只保留最近 50 条）
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history[-50:], f, ensure_ascii=False, indent=2)

def main():
    """主函数 - 命令行交互"""
    print("=" * 50)
    print("📝 小红书文案生成器 v0.1")
    print("=" * 50)
    print()
    
    # 检查 API Key
    if not KIMI_API_KEY:
        print("❌ 错误：未设置 KIMI_API_KEY 环境变量")
        print("请先设置：export KIMI_API_KEY='your-api-key'")
        return
    
    # 输入产品信息
    product = input("请输入产品/主题：").strip()
    if not product:
        print("❌ 产品描述不能为空")
        return
    
    print()
    print("选择文案风格：")
    print("1. 种草（推荐好物）")
    print("2. 测评（使用体验）")
    print("3. 教程（教学分享）")
    print("4. 日常（生活分享）")
    
    style_choice = input("请输入数字 (1-4，默认1)：").strip() or "1"
    
    styles = {
        "1": "种草",
        "2": "测评",
        "3": "教程",
        "4": "日常"
    }
    style = styles.get(style_choice, "种草")
    
    print()
    print("🤖 正在生成文案，请稍候...")
    print()
    
    # 生成文案
    result = generate_xhs_content(product, style)
    
    if result.get("error"):
        print(f"❌ 生成失败: {result['error']}")
        return
    
    # 显示结果
    print("=" * 50)
    print("✅ 生成完成！")
    print("=" * 50)
    print()
    print("【标题】")
    print(result["title"])
    print()
    print("【正文】")
    print(result["content"])
    print()
    print("【标签】")
    print(result["tags"])
    print()
    print("=" * 50)
    
    # 保存历史
    save_history(product, result)
    print("💾 已保存到历史记录")
    print()
    
    # 是否复制到剪贴板
    copy_choice = input("是否复制到剪贴板？(y/n): ").strip().lower()
    if copy_choice == 'y':
        full_text = f"{result['title']}\n\n{result['content']}\n\n{result['tags']}"
        try:
            import pyperclip
            pyperclip.copy(full_text)
            print("✅ 已复制到剪贴板")
        except:
            print("⚠️ 剪贴板功能需要安装 pyperclip: pip install pyperclip")
            print("文本内容：")
            print(full_text)

if __name__ == "__main__":
    main()
