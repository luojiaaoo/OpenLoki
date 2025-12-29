from enum import StrEnum
from typing import Literal, Callable, Union
from pydantic_ai.mcp import MCPServerStdio, MCPServerStreamableHTTP, MCPServerSSE
import uuid
from dataclasses import dataclass, field
from pydantic import BaseModel


# 模型返回值类型
class ChatType(StrEnum):
    START_OUTPUT = 'start_output'
    DELTA_OUTPUT = 'delta_optput'
    OUTPUT = 'output'
    START_THINKING = 'start_thinking'
    THINKING = 'thinking'
    FINAL_OUTPUT = 'final_output'
    START_TOOL_CALL = 'start_tool_call'
    TOOL_CALL = 'tool_call'
    TOOL_CALL_RETURN = 'tool_call_return'
    HISTORY_MESSAGES = 'history_messages'
    FINISH = 'finish'


# 模型返回值结构
# 1 代表 str
LITERAL_OUTPUT_ENUM = Literal[0,]
OUTPUT_ENUM_MAPPING = {
    0: dict(output_type=str, is_delta=True),
}


class DepsType(BaseModel):
    model_abbr: str


MAPPING_SAMPLING = {
    '严谨': dict(temperature=0.2, top_p=0.6),
    '平衡': dict(temperature=0.5, top_p=0.9),
    '创意': dict(temperature=0.9, top_p=0.95),
    '自由': dict(temperature=0.3, top_p=1.0),
}


# mcp
@dataclass
class Mcp:
    tool_prefix: str
    mcp: Union[MCPServerStdio, MCPServerStreamableHTTP, MCPServerSSE]
    parser_tool_call_result: Callable


@dataclass
class ReturnMcp:
    status: bool
    output: str


@dataclass
class Doc:
    """文档数据类"""

    doc_type: Literal['web_page']
    snippet: str
    title: str
    link: str = ''
    content: str = ''
    unique_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_markdown(self):
        markdown = f"""## {self.title}

**文档类型:** {self.doc_type}  
**文档链接:** [{self.link}]({self.link})  
**文档片段:** {self.snippet}  

### 文档内容
{self.content}
"""
        return markdown
