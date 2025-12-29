from core.configure import conf
from pydantic_ai import FunctionToolset
from models.domains import llm_domain
from typing import List, Union
from typing_extensions import TypedDict
import json
import asyncio
import httpx
from loguru import logger
from utils.log_util import TimeMonitor
from bs4 import BeautifulSoup
from utils import llm_util
from pydantic_ai import RunContext


class SerperSearch:
    def __init__(self, model_abbr, count=10):
        self._engine = 'serper'
        self._url = 'https://google.serper.dev/search'
        self._api_key = conf.mcp_search_serper_api_key
        self.timeout = conf.mcp_search_serper_timeout
        self.count = count
        self.max_tokens = int(conf.llm_get_model_name(model_abbr=model_abbr)['context_length'] * 0.7)
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.set_auth()

    def set_auth(self):
        self.headers['X-API-KEY'] = self._api_key

    def construct_body(self, query: str):
        return {
            'q': query,
            'count': self.count,
        }

    async def search(self, query: str) -> List[llm_domain.Doc]:
        body = self.construct_body(query)
        async with httpx.AsyncClient() as client:
            response = await client.post(self._url, json=body, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            rt = []
            for item in result.get('organic', []):
                if 'link' not in item:
                    continue
                rt.append(
                    llm_domain.Doc(
                        doc_type='web_page',
                        snippet=item.get('snippet', ''),
                        title=item.get('title', ''),
                        link=item['link'],
                    )
                )
            return await self.parser(rt)

    @TimeMonitor('爬取网页内容')
    async def parser(self, docs: List[llm_domain.Doc]) -> List[llm_domain.Doc]:
        async def _parser(source_url):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(source_url, timeout=self.timeout)
                    response.raise_for_status()
                    content_type = response.headers.get('content-type', '').lower()
                    if any(ct in content_type for ct in ['text/html', 'text/plain', 'text/xml', 'application/json', 'application/xml', 'application/octet-stream']):
                        return response.text
                    else:
                        logger.warning(f'parser content-type[{content_type}] not parser: url=[{source_url}]')
                        return ''
            except UnicodeDecodeError as ude:
                return ude.args[1].decode('gb2312', errors='ignore')
            except httpx.TimeoutException:
                logger.warning(f'parser timeout: url=[{source_url}]')
                return ''
            except httpx.RequestError as e:
                logger.warning(f'parser request error: url=[{source_url}] error={e}')
                return ''
            except Exception as e:
                logger.warning(f'parser error: url=[{source_url}] error={e}')
                return ''

        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(_parser(doc.link)) for doc in docs]
        results = [BeautifulSoup(task.result(), 'html.parser') for task in tasks]
        results = [soup.get_text() if soup.get_text() and len(soup.get_text().strip()) > 50 else str(soup.text) for soup in results]
        for doc, result in zip(docs[::-1], results[::-1]):
            if result:
                doc.content = result
            else:
                docs.remove(doc)
        return self.truncate_docs(docs[::-1])

    @TimeMonitor('截断网页的内容，避免超过最大上下文')
    def truncate_docs(self, docs: List[llm_domain.Doc], max_tokens=None):
        if max_tokens is None:
            max_tokens = self.max_tokens
        truncated_docs = []
        token_size = 0
        for doc in docs:
            if token_size >= max_tokens:
                break
            doc.content = doc.content[: max_tokens - token_size]
            token_size += llm_util.UsageStats.estimate_tokens(doc.content)
            truncated_docs.append(doc)
        return truncated_docs


def parser_tool_call_result(result_content: str):
    result_content = llm_util.FormatPrompt.yaml_to_dict(result_content)
    if result_content['success']:
        output = llm_util.FormatPrompt.dict_to_json(result_content['message'])
        return llm_domain.ReturnMcp(status=True, output=output)
    else:
        return llm_domain.ReturnMcp(status=False, output=result_content['message'])


datetime_toolset = FunctionToolset()


class SerperSearchResult(TypedDict):
    success: bool
    message: Union[List[str], str]


@datetime_toolset.tool
async def serper_search(ctx: RunContext[llm_domain.DepsType], query: str) -> str:
    """
    通过Serper搜索引擎API进行网页的搜索。
    参数：
        query (str): 搜索的自然语言查询内容。
    返回：
        str: yaml格式的搜索结果
    """
    try:
        rt = llm_util.FormatPrompt.dict_to_yaml(
            SerperSearchResult(
                success=True,
                message=[
                    dict(
                        doc_type=i.doc_type,
                        title=i.title,
                        snippet=i.snippet,
                        link=i.link,
                        markdown=i.to_markdown(),
                    )
                    for i in await SerperSearch(model_abbr=ctx.deps.model_abbr).search(query=query)
                ],
            ),
        )
        context_length = conf.llm_get_model_name(model_abbr=ctx.deps.model_abbr)['context_length']
        if llm_util.UsageStats(ctx.usage).can_add_ratio(rt, max_context_length=context_length) == 1:
            return rt
        else:
            return llm_util.FormatPrompt.dict_to_yaml(SerperSearchResult(success=False, message='本次返回的文本太长，模型上下文不足，主动拒绝本次的联网搜索'))
    except Exception as e:
        logger.exception('Serper搜索错误')
        return llm_util.FormatPrompt.dict_to_yaml(SerperSearchResult(success=False, message=str(e)))


mcp_search_serper = llm_domain.Mcp(
    tool_prefix=(i := 'serper_search'),
    mcp=datetime_toolset.prefixed(f'{i}_{conf.mcp_split_string}'),
    parser_tool_call_result=parser_tool_call_result,
)
