from __future__ import annotations

import ast
import operator as op
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from pypdf import PdfReader


def tool_log(name: str, params: Dict[str, Any], result_preview: str) -> None:
    print("\n" + "=" * 80)
    print(f"[TOOL] {name}")
    print(f"[PARAMS] {params}")
    print(f"[RESULT PREVIEW] {result_preview[:300]}")
    print("=" * 80 + "\n")


def get_current_time() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tool_log("get_current_time", {}, now)
    return now


def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=3"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    result = resp.text.strip()
    tool_log("get_weather", {"city": city}, result)
    return result


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def _eval_expr(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return _ALLOWED_OPERATORS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp):
        return _ALLOWED_OPERATORS[type(node.op)](_eval_expr(node.operand))
    raise ValueError("不支持的表达式")


def simple_calculator(expression: str) -> str:
    tree = ast.parse(expression, mode="eval")
    result = str(_eval_expr(tree.body))
    tool_log("simple_calculator", {"expression": expression}, result)
    return result


def read_local_pdf(file_path: str, max_pages: int = 50) -> str:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("当前仅支持 PDF 文件")

    reader = PdfReader(str(path))
    texts: List[str] = []
    page_count = min(len(reader.pages), max_pages)

    for i in range(page_count):
        page_text = reader.pages[i].extract_text() or ""
        page_text = page_text.strip()
        if page_text:
            texts.append(f"\n--- 第 {i+1} 页 ---\n{page_text}")

    result = "\n".join(texts).strip()
    tool_log("read_local_pdf", {"file_path": str(path), "max_pages": max_pages}, result[:500])
    return result


TOOLS = {
    "get_current_time": get_current_time,
    "get_weather": get_weather,
    "simple_calculator": simple_calculator,
    "read_local_pdf": read_local_pdf,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前本地时间",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，例如 北京、上海、深圳"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simple_calculator",
            "description": "进行简单数学表达式计算，例如 12*(3+4)",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_local_pdf",
            "description": "读取本地 PDF 文件内容，适合后续摘要、问答和分析",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "本地 PDF 文件路径"},
                    "max_pages": {"type": "integer", "description": "最多读取多少页，默认 50"}
                },
                "required": ["file_path"],
            },
        },
    },
]
