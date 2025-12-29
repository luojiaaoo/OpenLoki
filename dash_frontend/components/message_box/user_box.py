from dash import html
from datetime import datetime
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
import uuid
from typing import Dict, List
from configure import conf
import json
from utils import dash_util


def render(
    bearer_token: str,  # 新的Bearer Token
    model_abbr: str,  # 使用模型
    user_prompt: str,  # 用户提示词
    message_history: List,  # 历史会话
    document: str,  # 文本
    output_enum: int,  # 返回值的枚举
    instructions: str,  # 指令
    deps: Dict,  # 工具依赖设置
    toolsets: List,  # 使用哪些工具
    conversation_id: str,  # 会话名字
    user_id: str,  # 用户名
    model_settings: Dict,  # 模型参数
    activate_long_memory:bool, # 是否激活长期记忆
    retries: int = 3,
    debounce_by: float = 0.1,
):
    parameters = dict(
        model_abbr=model_abbr,
        user_prompt=user_prompt,
        message_history=message_history,
        document=document,
        output_enum=output_enum,
        instructions=instructions,
        deps=deps,
        toolsets=toolsets,
        conversation_id=conversation_id,
        user_id=user_id,
        model_settings=model_settings,
        activate_long_memory=activate_long_memory,
        retries=retries,
        debounce_by=debounce_by,
    )
    # 本轮对话的uuid

    return fuc.FefferyPostEventSource(
        id={'type': 'conversation-sse', 'index': conversation_id},
        headers={
            'Authorization': f'Bearer {bearer_token}',  # 使用最新的Bearer Token
        },
        key=uuid.uuid4().hex,
        url=f'{conf.backend_url}/llm/stream-general-agent',
        body=json.dumps(parameters),
        autoReconnect=dict(retries=3, delay=1),
    ).to_plotly_json(), dash_util.process_object(
        fac.AntdRow(
            fac.AntdCol(
                fac.AntdFlex(
                    [
                        fac.AntdAvatar(
                            mode='icon',
                            icon='antd-user',
                            style={'background': '#1677ff'},
                        ),
                        html.Div(
                            [
                                fac.AntdText(user_prompt, copyable=True),
                                html.Div(
                                    datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                                    className='conversation-message-box-datetime-right',
                                ),
                            ],
                            className='conversation-message-box',
                            style=style(backgroundColor='#e6f7ff'),
                        ),
                    ],
                    vertical=True,
                    align='end',
                    gap=8,
                    style={'width': '100%'},
                ),
                span=20,
                style={'position': 'relative'},
            ),
            justify='end',
        ),
    )
