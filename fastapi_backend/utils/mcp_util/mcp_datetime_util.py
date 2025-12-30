from core.configure import conf
from pydantic_ai import FunctionToolset
from models.domains import llm_domain
from typing import List, Union
from typing_extensions import TypedDict
from loguru import logger
from utils import llm_util
from pydantic_ai import RunContext
from datetime import datetime


toolset = FunctionToolset()


@toolset.tool
async def get_now_datetime(ctx: RunContext[llm_domain.DepsType]) -> str:
    """
    Get the current date and time as a formatted string.
    Returns:
        str: The current date and time formatted as 'YYYY-MM-DD HH:MM:SS'.
    """
    return f'{datetime.now():%Y-%m-%d %H:%M:%S}'


mcp_datetime = llm_domain.Mcp(
    tool_prefix=(i := '<datetime>'),
    mcp=toolset.prefixed(f'{i}_{conf.mcp_split_string}'),
    parser_tool_call_result=None,
)
