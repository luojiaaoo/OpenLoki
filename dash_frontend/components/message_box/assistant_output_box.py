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
    id_copy_markdown = {'type': 'assistant-output-copy-markdown', 'index': new_uuid}
    return (
        id_markdown,
        id_copy_markdown,
        dash_util.process_object(
            html.Div(
                fac.AntdRow(
                    fac.AntdCol(
                        fac.AntdFlex(
                            [
                                fac.AntdAvatar(
                                    mode='icon',
                                    icon='antd-robot',
                                    style={'background': '#1677ff'},
                                ),
                                html.Div(
                                    [
                                        # sse组件根据new_uuid找到这个markdown输出框
                                        fmc.FefferyMarkdown(
                                            id=id_markdown,
                                            markdownStr='',
                                            placeholder=fuc.FefferyExtraSpinner(type='ball').to_plotly_json(),
                                            codeTheme='dracula',
                                            renderHtml=True,  # 支持html渲染
                                            codeBlockStyle={
                                                'overflowX': 'auto',
                                            },
                                            style={
                                                'background': 'transparent',
                                                'fontSize': 14,
                                            },
                                        ),
                                        fac.AntdSpace(
                                            [
                                                html.Div(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), className='conversation-message-box-datetime'),
                                                fac.AntdCopyText(id=id_copy_markdown, text=''),
                                            ],
                                            className='conversation-message-box-left',
                                        ),
                                    ],
                                    style={
                                        'background': '#f2f2f2',
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
        ),
    )
