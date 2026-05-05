from __future__ import annotations

import json
from typing import Dict, List

from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SYSTEM_PROMPT
from tools import TOOLS, TOOL_SCHEMAS


class DeepSeekAgent:
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("未读取到 DEEPSEEK_API_KEY，请检查 .env 配置")
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        self.model = DEEPSEEK_MODEL
        self.messages: List[Dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def add_user_message(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def _summarize_long_text_map_reduce(self, text: str, chunk_size: int = 3500) -> str:
        if len(text) <= chunk_size:
            return text

        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        partial_summaries = []

        for idx, chunk in enumerate(chunks, start=1):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个文档摘要助手，请提炼关键信息。"},
                    {"role": "user", "content": f"请总结第 {idx} 个片段的要点：\n\n{chunk}"}
                ],
                stream=False,
            )
            partial_summaries.append(f"片段{idx}摘要：\n{resp.choices[0].message.content}")

        reduce_input = "\n\n".join(partial_summaries)
        final_resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个高级文档归纳助手，请综合多个摘要并输出最终总结。"},
                {"role": "user", "content": f"请将以下多个片段摘要综合为一份完整总结：\n\n{reduce_input}"}
            ],
            stream=False,
        )
        return final_resp.choices[0].message.content

    def run(self, user_input: str, max_tool_rounds: int = 5) -> str:
        self.add_user_message(user_input)

        for _ in range(max_tool_rounds):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                stream=False,
            )

            message = response.choices[0].message

            assistant_record = {
                "role": "assistant",
                "content": message.content or ""
            }

            if getattr(message, "tool_calls", None):
                assistant_record["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            self.messages.append(message.model_dump())

            if not getattr(message, "tool_calls", None):
                return message.content or ""

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                raw_args = tool_call.function.arguments or "{}"
                args = json.loads(raw_args)

                if fn_name not in TOOLS:
                    tool_result = f"工具 {fn_name} 不存在"
                else:
                    try:
                        tool_result = TOOLS[fn_name](**args)
                        if fn_name == "read_local_pdf" and len(tool_result) > 4000:
                            tool_result = self._summarize_long_text_map_reduce(tool_result)
                    except Exception as e:
                        tool_result = f"工具执行失败: {type(e).__name__}: {e}"

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )

        return "已达到最大工具调用轮数，停止执行。"
