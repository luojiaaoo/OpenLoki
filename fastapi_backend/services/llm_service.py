from models.domains import llm_domain
from models.schemas import llm_schema
from utils import mcp_util, llm_util
from core.llm import general_agent
import json
import time
import asyncio
import uuid


async def service_general_agent(call_llm: llm_schema.CallLLM):
    # 参数解析
    toolset_names = [*(call_llm.toolsets or []), *mcp_util.default_mcps]
    toolsets = [mcp_.mcp.filtered(lambda ctx, tool_def: mcp_util.get_prefix_real_tool_name(tool_def.name)[-1] in toolset_names) for mcp_ in mcp_util.all_mcps]
    parseres_tool_call_result = {mcp_.tool_prefix: mcp_.parser_tool_call_result for mcp_ in mcp_util.all_mcps}

    sampling = call_llm.model_settings.sampling

    time_start = time.time()
    async for i in general_agent.run(
        user_id=call_llm.user_id,
        conversation_id=call_llm.conversation_id,
        model_abbr=call_llm.model_abbr,
        user_prompt=call_llm.user_prompt,
        document=call_llm.document,
        message_history=llm_util.UtilHistoryMessage.json2messages(call_llm.message_history) if call_llm.message_history else None,
        output_type=llm_domain.OUTPUT_ENUM_MAPPING[call_llm.output_enum]['output_type'],
        is_delta=llm_domain.OUTPUT_ENUM_MAPPING[call_llm.output_enum]['is_delta'],
        instructions=call_llm.instructions,
        deps=call_llm.deps,
        toolsets=toolsets,
        parseres_tool_call_result=parseres_tool_call_result,
        sampling=sampling,
        retries=call_llm.retries,
        activate_long_memory=call_llm.activate_long_memory,
        debounce_by=call_llm.debounce_by,
    ):
        if i['type'] == llm_domain.ChatType.THINKING:
            minimum_interval = 0.3
        else:
            minimum_interval = 0.2
        uuid_str = uuid.uuid4().hex  # 加上uuid，如果内容重复也能触发回调
        if str(i).startswith('start_'):
            for _ in range(3):
                await asyncio.sleep(0.1)
                yield f'data: {json.dumps({**i, "force_refresh": uuid_str}, ensure_ascii=False)}\n\n'  # start_开头是新建对话框的标识，千万不能丢包，多发几次降低丢包的概率
        else:
            yield f'data: {json.dumps({**i, "force_refresh": uuid_str}, ensure_ascii=False)}\n\n'
        remain_second = minimum_interval - (time.time() - time_start)
        if remain_second > 0:
            await asyncio.sleep(remain_second)
        time_start = time.time()
