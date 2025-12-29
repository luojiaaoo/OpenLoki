from dash import html, dcc
from datetime import datetime
import feffery_antd_components as fac
import feffery_utils_components as fuc
from utils import dash_util
import uuid
import feffery_markdown_components as fmc
import json


def render(data):
    status = data['status']
    if status:
        json_data = json.loads(data['output'])
        count_content = len(json_data)
        uuids = [uuid.uuid4().hex for i in range(0, count_content)]
        temp = [
            fac.Fragment(
                [
                    fuc.FefferyExecuteJs(
                        id={'type': 'serper-search-exec-js', 'index': uuids[i]},
                    )
                    for i in range(0, count_content)
                ],
            ),
            fac.Fragment(
                [
                    dcc.Store(
                        id={'type': 'serper-search-store-link', 'index': uuids[i]},
                        data=json_data[i]['link'],
                    )
                    for i in range(0, count_content)
                ],
            ),
            fac.AntdCard(
                [
                    fac.AntdCardGrid(
                        json_data[i]['title'],
                        id={'type': 'serper-search-card-grid-btn', 'index': uuids[i]},
                        style={'cursor': 'pointer'},
                    )
                    for i in range(0, count_content)
                ],
                style={
                    'background': 'transparent',
                    'fontSize': 12,
                    'fontStyle': 'italic',
                    'minWidth': '60px',
                    'maxWidth': '100%',
                    'marginBottom': 10,
                },
                title='联网搜索结果',
            ),
        ]
    else:
        temp = [fac.AntdResult(title='联网搜索执行失败', subTitle=data['output'], status='error')]
    return dash_util.process_object(
        html.Div(
            fac.AntdRow(
                fac.AntdCol(
                    fac.AntdFlex(
                        [
                            fac.AntdAvatar(
                                mode='icon',
                                icon='im-sphere',
                                style={'background': '#acadaf'},
                            ),
                            html.Div(
                                [
                                    *temp,
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
