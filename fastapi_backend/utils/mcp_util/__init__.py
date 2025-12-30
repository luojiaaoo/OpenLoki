from .mcp_search_serper_util import mcp_search_serper
from .mcp_datetime_util import mcp_datetime
from core.configure import conf


def get_prefix_real_tool_name(name):
    tool_prefix = (i := name.split(conf.mcp_split_string))[0].rstrip('_')
    real_tool_name = i[-1].lstrip('_')
    return tool_prefix, real_tool_name


all_mcps = [
    mcp_search_serper,
    mcp_datetime,
]

default_mcps = [
    'get_now_datetime'
]
