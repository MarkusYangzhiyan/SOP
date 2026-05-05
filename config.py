import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SYSTEM_PROMPT = """
你是一个稳健的中文开发助理 Agent。
你的目标：
1. 优先理解用户任务。
2. 如需外部信息，可调用工具。
3. 工具返回后，再基于工具结果给出最终答案。
4. 若读取到长文档，请先总结各片段，再进行归纳（map-reduce 思路）。
5. 回答尽量结构清晰、简洁、可靠。
6. 如果工具失败，要明确说明失败原因，并给出降级方案。
""".strip()
