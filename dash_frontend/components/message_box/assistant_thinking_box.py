from dash import html
from datetime import datetime
import feffery_antd_components as fac
import feffery_utils_components as fuc
import feffery_markdown_components as fmc
from utils import dash_util
import uuid


def render():
    new_uuid = uuid.uuid4().hex
    id_markdown = {'type': 'assistant-output-markdown', 'index': new_uuid}
    return id_markdown, dash_util.process_object(
        html.Div(
            fac.AntdRow(
                fac.AntdCol(
                    fac.AntdFlex(
                        [
                            fac.AntdAvatar(
                                mode='icon',
                                icon='fc-idea',
                                style={'background': '#acadaf'},
                            ),
                            html.Div(
                                [
                                    # sse组件根据new_uuid找到这个markdown输出框
                                    fmc.FefferyMarkdown(
                                        id=id_markdown,
                                        markdownStr='',
                                        placeholder=fuc.FefferyExtraSpinner(type='ball').to_plotly_json(),
                                        codeTheme='coldark-cold',
                                        renderHtml=True,  # 支持html渲染
                                        codeBlockStyle={
                                            'overflowX': 'auto',
                                        },
                                        style={
                                            'background': 'transparent',
                                            'fontSize': 12,
                                            'fontStyle': 'italic',
                                        },
                                    ),
                                    fac.AntdSpace(
                                        [
                                            html.Div(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), className='conversation-message-box-datetime'),
                                        ],
                                        className='conversation-message-box-left',
                                    ),
                                ],
                                style={
                                    'background': '#ffffffff',
                                },
                                className='conversation-message-box',
                            ),
                        ],
                        vertical=True,
                        align='start',
                        gap=8,
                        style={'width': '100%'},
                    ),
                    span=20,
                    style={'position': 'relative'},
                ),
                justify='start',
            ),
        )
    )
