from pydantic_ai import (
    Agent,
    ModelSettings,
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPartDelta,
    ThinkingPartDelta,
    ToolCallPartDelta,
    TextPart,
    ToolCallPart,
    ThinkingPart,
    ModelMessage,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from loguru import logger
from models.domains import llm_domain
from utils import llm_util
from core.configure import conf
import asyncio
from utils import mcp_util
from typing import Optional, Dict


async def run(
    user_id,
    conversation_id,
    model_abbr,
    user_prompt,
    document,
    message_history,
    output_type,
    is_delta,
    instructions,
    deps: Optional[Dict],
    toolsets,
    parseres_tool_call_result,
    sampling,
    retries,
    activate_long_memory,
    debounce_by,
):
    # 注入模型的上下文
    if deps is None:
        deps = llm_domain.DepsType(model_abbr=model_abbr)
    else:
        for k, v in deps.items():
            # 根据值填充依赖
            deps = llm_domain.DepsType(model_abbr=model_abbr)
            setattr(deps, k, v)
    temp_ = conf.llm_get_model_name(model_abbr)
    model_name = temp_['model_name']
    model_url = temp_['model_url']
    api_key = temp_['api_key']
    max_tokens = temp_['max_tokens']
    context_length = temp_['context_length']

    def logger_info(msg: str):
        return logger.info(f'[user_id: {user_id} | conversation_id: {conversation_id} | LLM调用] {repr(msg)}')

    common_model_settings = dict(max_tokens=max_tokens)

    # 核采样
    model_settings = ModelSettings(**llm_domain.MAPPING_SAMPLING[sampling], **common_model_settings)

    logger_info(f'【指令】{instructions};【用户输入】{user_prompt};【调用模型】{model_name};【长期记忆】{activate_long_memory};【响应token数】{max_tokens}')

    # 长期记忆召回
    if activate_long_memory:
        long_mem = await llm_util.LongMemory.recall_memory(user_id=user_id, query=user_prompt)
    else:
        long_mem = None

    # 生成指令
    instructions = (
        (f'# Role & Policies\n{instructions}\n\n' if instructions else '')
        + (f'# Evidence\n{document}\n\n' if document else '')
        + (f'# Context\n{long_mem}\n\n' if long_mem else '')
        + '# Output\n请基于以上信息,提供准确、有据的回答。\n上一次工具调用失败可能是暂时的，你可以重试一次。'
    )

    # 如果太长需要一个高保真的总结
    async def summarize_history_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
        if (
            llm_util.UsageStats.estimate_tokens(str(messages)) > context_length / 2 or len(messages) / 2 > conf.short_memory_len_message_history
        ):  # 超过一半的上下文长度 或者 对话次数超过限制，就进行总结
            return (await llm_util.ShortMemory.summarize(messages[:-20])) + messages[-20:]
        else:
            return messages

    model = OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=model_url, api_key=api_key), settings=model_settings)
    agent = Agent(
        model,
        instructions=instructions,
        output_type=output_type,
        deps_type=llm_domain.DepsType,
        retries=retries,
        history_processors=[summarize_history_messages],
    )

    async with agent.iter(
        user_prompt,
        toolsets=toolsets,
        message_history=message_history,
        deps=deps,
    ) as run:
        async for node in run:
            if Agent.is_user_prompt_node(node):
                # A user prompt node => The user has provided input
                logger_info(f'=== UserPromptNode: {node.user_prompt} ===')
            elif Agent.is_model_request_node(node):
                # A model request node => We can stream tokens from the model's request
                logger_info('=== ModelRequestNode: streaming partial request tokens ===')
                async with node.stream(run.ctx) as request_stream:
                    final_result_found = False
                    thinking_cache = ''  # thinking发的太快了，必须做一个缓冲，才行，不然sse总丢帧
                    async for event in request_stream:
                        if isinstance(event, PartStartEvent):
                            logger_info(f'[Request] Starting part {event.index}: {event.part!r}')
                            if isinstance(event.part, ThinkingPart):
                                yield dict(type=llm_domain.ChatType.START_THINKING)
                                await asyncio.sleep(1)
                                thinking_cache += event.part.content
                            else:
                                if thinking_cache:  # 如果缓冲还有，就一次性发完
                                    yield dict(type=llm_domain.ChatType.THINKING, data=thinking_cache)
                                if isinstance(event.part, TextPart):
                                    yield dict(type=llm_domain.ChatType.START_OUTPUT)
                                    await asyncio.sleep(1)
                                elif isinstance(event.part, ToolCallPart):
                                    ...  # # 可能参数都不是流式返回，starting part就一次性说了
                        elif isinstance(event, PartDeltaEvent):
                            if isinstance(event.delta, TextPartDelta):  # 只有run_stream_events才会把Output当成TextPartDelta输出
                                logger_info(f'[Request] Part {event.index} text delta: {event.delta.content_delta!r}')
                            elif isinstance(event.delta, ThinkingPartDelta):
                                logger_info(f'[Request] Part {event.index} thinking delta: {event.delta.content_delta!r}')
                                thinking_cache += event.delta.content_delta
                                if len(thinking_cache) >= 32:  # 一次发32个字符
                                    temp, thinking_cache = thinking_cache[:32], thinking_cache[32:]
                                    yield dict(type=llm_domain.ChatType.THINKING, data=temp)
                            elif isinstance(event.delta, ToolCallPartDelta):  # 可能参数都不是流式返回，starting part就一次性说了
                                logger_info(f'[Request] Part {event.index} args delta: {event.delta.args_delta}')
                        elif isinstance(event, FinalResultEvent):
                            logger_info(f'[Result] The model started producing a final result (tool_name={event.tool_name})')
                            final_result_found = True
                            break

                    if final_result_found:
                        # Once the final result is found, we can call `AgentStream.stream_text()` to stream the text.
                        # A similar `AgentStream.stream_output()` method is available to stream structured output.
                        if is_delta:
                            async for output in request_stream.stream_text(delta=True, debounce_by=debounce_by):
                                logger_info(f'[Output] [Delta] {output}')
                                yield dict(type=llm_domain.ChatType.DELTA_OUTPUT, data=output)
                        else:
                            async for output in request_stream.stream_output(debounce_by=debounce_by):
                                logger_info(f'[Output] {output}')
                                yield dict(type=llm_domain.ChatType.OUTPUT, data=output)
            elif Agent.is_call_tools_node(node):
                # A handle-response node => The model returned some data, potentially calls a tool
                logger_info('=== CallToolsNode: streaming partial response & tool usage ===')
                async with node.stream(run.ctx) as handle_stream:
                    tool_prefix = None
                    async for event in handle_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            tool_prefix, real_tool_name = mcp_util.get_prefix_real_tool_name(event.part.tool_name)
                            logger_info(f'[Tools] The LLM calls tool={event.part.tool_name!r} with args={event.part.args} (tool_call_id={event.part.tool_call_id!r})')
                            yield dict(type=llm_domain.ChatType.START_TOOL_CALL)
                            await asyncio.sleep(1)
                            yield dict(type=llm_domain.ChatType.TOOL_CALL, data=dict(tool_name=real_tool_name, args=event.part.args))
                        elif isinstance(event, FunctionToolResultEvent):
                            logger_info(
                                f'[Tools] Tool call {event.tool_call_id!r} returned => {event.result.content[:100] + "..." + event.result.content[-100:] if len(event.result.content) > 300 else event.result.content}'
                            )
                            return_mcp: llm_domain.ReturnMcp = parseres_tool_call_result[tool_prefix](event.result.content)
                            yield dict(type=llm_domain.ChatType.TOOL_CALL_RETURN, data=dict(status=return_mcp.status, output=return_mcp.output))
            elif Agent.is_end_node(node):
                # Once an End node is reached, the agent run is complete
                assert run.result is not None
                assert run.result.output == node.data.output
                # 最后一次就把历史信息、token消耗等信息也传回去
                logger_info(f'=== Final Agent Output: {run.result.output} ===\n')
                logger_info(
                    f'=== Token Usage ===\n'
                    f'{
                        dict(
                            output_tokens=(i := run.usage()).output_tokens,
                            input_tokens=i.input_tokens,
                            total_tokens=i.total_tokens,
                        )
                    }'
                )
                yield dict(
                    type=llm_domain.ChatType.FINAL_OUTPUT,
                    data=node.data.output,
                    **dict(
                        output_tokens=(i := run.usage()).output_tokens,
                        input_tokens=i.input_tokens,
                        total_tokens=i.total_tokens,
                    ),
                )
                yield dict(
                    type=llm_domain.ChatType.HISTORY_MESSAGES,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    json=llm_util.UtilHistoryMessage.messages2json(run.all_messages()),
                )
                if activate_long_memory:
                    # 长期记忆，保存对话
                    asyncio.create_task(
                        llm_util.LongMemory.add_memory(
                            user_id=user_id,
                            conversation_id=conversation_id,
                            user_ask=user_prompt,
                            assistant_answer=node.data.output,
                        )
                    )
                yield dict(
                    type=llm_domain.ChatType.FINISH,
                )
