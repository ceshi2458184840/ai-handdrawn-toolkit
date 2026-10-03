#!/usr/bin/env python3
"""生成手绘风格图片 - 使用免费 API"""
import urllib.parse
import urllib.request
import sys
import os

def generate_handdrawn_image(prompt, width=800, height=600, output_path=None):
    """
    使用 Pollinations.ai 生成手绘风格图片（完全免费）
    
    Args:
        prompt: 图片描述（英文）
        width: 宽度
        height: 高度
        output_path: 输出路径
    
    Returns:
        输出文件路径
    """
    if output_path is None:
        # 创建输出目录
        os.makedirs("generated", exist_ok=True)
        filename = prompt.replace(" ", "_")[:50] + ".png"
        output_path = f"generated/{filename}"
    
    # URL 编码 prompt
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    
    print(f"🎨 正在生成手绘风格图片...")
    print(f"   Prompt: {prompt}")
    print(f"   URL: {url[:80]}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; AI-HandDrawn-Toolkit/1.0)'
        }
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            print(f"✅ 图片已保存: {output_path}")
            print(f"   大小: {len(data)} bytes")
            
            return output_path
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_sketch.py <prompt> [width] [height] [output]")
        print("示例: python3 generate_sketch.py 'hand-drawn monkey sketch' 1200 800 monkey.png")
        sys.exit(1)
    
    prompt = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    height = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    output = sys.argv[4] if len(sys.argv) > 4 else None
    
    result = generate_handdrawn_image(prompt, width, height, output)
    
    if result:
        print(f"\n🎉 成功! 图片路径: {result}")
    else:
        print("\n💔 生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
