import os
import openai
import argparse
from langdetect import detect
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# 配置OpenAI API密钥
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("请设置OPENAI_API_KEY环境变量")

# 支持的编程语言及其代码块标记
LANGUAGE_MAPPINGS = {
    "python": "python",
    "java": "java",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "c++": "cpp",
    "cpp": "cpp",
    "c#": "csharp",
    "go": "go",
    "rust": "rust",
    "php": "php",
    "ruby": "ruby",
    "swift": "swift",
    "kotlin": "kotlin",
    "html": "html",
    "css": "css",
    "sql": "sql",
}

console = Console()

def detect_language(code):
    """检测代码语言"""
    try:
        # 简单的启发式检测，优先基于文件扩展名或语言特定关键字
        for lang_key, lang_name in LANGUAGE_MAPPINGS.items():
            if lang_key in code.lower():
                return lang_name
        
        # 使用langdetect作为后备
        detected = detect(code)
        return LANGUAGE_MAPPINGS.get(detected, "python")  # 默认使用Python
    except Exception:
        return "python"  # 无法检测时默认使用Python

def generate_code_suggestion(code_context, language="python", instruction="优化这段代码"):
    """使用OpenAI API生成代码建议"""
    # 构建提示词
    prompt = f"""
你是一个专业的代码助手。请根据以下要求处理提供的代码:

{instruction}

代码语言: {language}

代码上下文:{code_context}
请只返回代码建议，不要包含解释。
"""
    
    try:
        # 调用OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",  # 可以更改为gpt-3.5-turbo以降低成本
            messages=[
                {"role": "system", "content": "你是一个专业的代码助手，提供高质量的代码建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # 较低的温度以获得更确定性的结果
            max_tokens=1000
        )
        
        # 提取建议代码
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        console.print(f"[red]API调用错误: {str(e)}[/red]")
        return None

def analyze_code_quality(code_context, language="python"):
    """分析代码质量并提供反馈"""
    prompt = f"""
你是一个专业的代码审查员。请分析以下代码的质量，包括但不限于:
- 潜在问题
- 可读性
- 性能
- 安全性
- 最佳实践

代码语言: {language}

代码上下文:{code_context}
请提供详细的分析和改进建议。
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个专业的代码审查员，提供详细的代码质量分析。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        analysis = response.choices[0].message.content.strip()
        return analysis
    except Exception as e:
        console.print(f"[red]API调用错误: {str(e)}[/red]")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI代码助手 - 基于OpenAI API的代码建议工具")
    parser.add_argument("--code", "-c", help="代码内容", required=True)
    parser.add_argument("--language", "-l", help="代码语言", default=None)
    parser.add_argument("--instruction", "-i", help="指令", default="优化这段代码")
    parser.add_argument("--analyze", "-a", action="store_true", help="分析代码质量")
    
    args = parser.parse_args()
    
    # 检测或使用指定的语言
    code_language = args.language or detect_language(args.code)
    
    # 确保语言在支持列表中
    if code_language not in LANGUAGE_MAPPINGS.values():
        code_language = "python"
        console.print(f"[yellow]警告: 不支持的语言。默认使用Python。[/yellow]")
    
    console.print(Panel(f"[bold blue]代码助手 - {code_language.upper()}[/bold blue]", expand=False))
    
    if args.analyze:
        # 分析代码质量
        console.print("[bold green]正在分析代码质量...[/bold green]")
        analysis = analyze_code_quality(args.code, code_language)
        
        if analysis:
            console.print(Markdown(analysis))
    else:
        # 生成代码建议
        console.print(f"[bold green]正在生成{args.instruction}...[/bold green]")
        suggestion = generate_code_suggestion(args.code, code_language, args.instruction)
        
        if suggestion:
            # 突出显示建议代码
            code_block = f"```python\n{suggestion}\n```"
            console.print(Markdown(code_block))

if __name__ == "__main__":
    main()
