from pydantic_core import to_jsonable_python
from pydantic_ai import ModelMessagesTypeAdapter, ModelSettings, format_as_xml
from core.configure import conf
from loguru import logger
from typing import Dict
import httpx
from core.llm import prompt
from pydantic_ai.result import RunUsage
import tiktoken
import json
import yaml


async def async_iter_get_nth(async_iterator, n=-1):
    items = []
    async for item in async_iterator:
        items.append(item)
    if n >= len(items):
        raise IndexError('n超过迭代器长度')
    return items[n]


class UtilHistoryMessage:
    @classmethod
    def messages2json(cls, messages) -> str:
        """Convert ModelMessage list to JSON-serializable format."""
        return to_jsonable_python(messages)

    @classmethod
    def json2messages(cls, json_data: str):
        """Convert JSON-serializable format back to ModelMessage list."""
        return ModelMessagesTypeAdapter.validate_python(json_data)


# 判断token使用量
class UsageStats:
    def __init__(self, usage: RunUsage):
        self.usage = usage

    def get_total_tokens_used(self) -> int:
        """计算已使用的总令牌数"""
        total = self.usage.input_tokens + self.usage.output_tokens
        return total

    @classmethod
    def estimate_tokens(cls, text: str):
        """
        简单估算 token 数 - 使用 GPT-4 的分词器作为基准
        """
        # 使用 GPT-4 的分词器
        encoding = tiktoken.get_encoding('cl100k_base')
        # 计算实际 token 数
        token_count = len(encoding.encode(text))
        return token_count

    def can_add_ratio(self, estimated_query: str, max_context_length: int, buffer_percentage: float = 0.1) -> float:
        """
        检查是否可以添加更多内容

        Args:
            estimated_tokens: 预计要添加的令牌数
            max_context_length: 最大上下文长度
            buffer_percentage: 安全缓冲区百分比（默认为10%）
        """
        estimated_tokens = self.estimate_tokens(estimated_query)
        total_used = self.get_total_tokens_used()
        buffer_tokens = int(max_context_length * buffer_percentage)
        need_del_percent = max(0, ((total_used + estimated_tokens + buffer_tokens) - max_context_length) / estimated_tokens)
        # 传入内容可以保留的百分比，全保留为1
        return 1 - need_del_percent

    def get_detailed_usage(self, max_context_length: int) -> Dict:
        """获取详细使用情况报告"""
        total_used = self.get_total_tokens_used()

        return {
            'total_used': total_used,
            'remaining': max_context_length - total_used,
            'percentage_used': (total_used / max_context_length) * 100,
            'max_context_length': max_context_length,
            'breakdown': {
                'input_tokens': self.usage.input_tokens,
                'output_tokens': self.usage.output_tokens,
                'input_audio_tokens': self.usage.input_audio_tokens,
                'cache_audio_read_tokens': self.usage.cache_audio_read_tokens,
            },
        }


class FormatPrompt:
    @classmethod
    def dict_to_json(cls, obj) -> str:
        return json.dumps(obj, ensure_ascii=False, indent=2)

    @classmethod
    def json_to_dict(cls, json_str) -> Dict:
        return json.loads(json_str)

    @classmethod
    def yaml_to_dict(cls, yaml_str) -> Dict:
        return yaml.safe_load(yaml_str)

    @classmethod
    def dict_to_yaml(cls, obj) -> str:
        return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False, indent=2, explicit_end=True)


# 短期记忆
class ShortMemory:
    @classmethod
    async def summarize(cls, history_messages):
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider

        agent = Agent(
            OpenAIChatModel(
                conf.short_memory_summarize_model_name,
                provider=OpenAIProvider(
                    base_url=conf.short_memory_summarize_url,
                    api_key=conf.short_memory_summarize_api_key,
                ),
                settings=ModelSettings(top_p=0.4),
            ),
            instructions=prompt.prompt_short_memory_summarize,
            output_type=str,
        )
        result = await agent.run('如果要总结之前的历史对话，找哪些角色比较合适？他们总结的内容会是什么样？', message_history=history_messages)
        return result.new_messages()


# 长期记忆
class LongMemory:
    @classmethod
    async def add_memory(cls, user_id: str, conversation_id: str, user_ask: str, assistant_answer: str):
        data = {
            'user_id': user_id,
            'conversation_id': conversation_id,
            'messages': [
                {'role': 'user', 'content': user_ask},
                {'role': 'assistant', 'content': assistant_answer},
            ],
        }
        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {conf.long_memory_memos_api_key}'}
        url = f'{conf.long_memory_memos_url}/add/message'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=conf.long_memory_memos_timeout)
            response.raise_for_status()
            result: Dict = response.json()
            if result.get('code') != 0:
                logger.error(f'[user_id: {user_id} | conversation_id: {conversation_id} | 长期记忆添加失败] {result.get("message")!r}')
            else:
                logger.info(f'[user_id: {user_id} | conversation_id: {conversation_id} | 长期记忆添加成功] {str(data)!r}')

    @classmethod
    async def recall_memory(cls, user_id, query, conversation_id=None):
        data = {'query': query, 'user_id': user_id, **({'conversation_id': '0928'} if conversation_id else {})}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {conf.long_memory_memos_api_key}'}
        url = f'{conf.long_memory_memos_url}/search/memory'
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=conf.long_memory_memos_timeout)
            response.raise_for_status()
            result: Dict = response.json()
        if result.get('code') != 0:
            logger.error(f'[user_id: {user_id} | conversation_id: {conversation_id} | 长期记忆召回失败] {result.get("message")!r}')
        else:
            logger.info(f'[user_id: {user_id} | conversation_id: {conversation_id} | 长期记忆召回成功] {str(json_data := (result["data"]))!r}')
            return format_as_xml(json_data)
