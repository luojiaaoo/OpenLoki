from dash import html, dcc
from datetime import datetime
import feffery_antd_components as fac
import feffery_utils_components as fuc
from utils import dash_util
import uuid
import feffery_markdown_components as fmc
import json


def render(status, output):
    if status:
        json_data = json.loads(output)
        temp = fac.AntdTable(
            columns=[
                {
                    'title': '标题',
                    'dataIndex': '标题',
                    'width': '20%',
                },
                {
                    'title': '简介',
                    'dataIndex': '简介',
                    'width': '70%',
                },
                {
                    'title': '连接',
                    'dataIndex': '连接',
                    'renderOptions': {
                        'renderType': 'link',
                        'renderLinkText': '链接',
                    },
                    'width': '10%',
                },
            ],
            data=[
                {
                    '标题': i['title'],
                    '简介': i['snippet'],
                    '连接': {'href': i['link']},
                }
                for i in json_data
            ],
        )
    else:
        temp = fac.AntdResult(title='联网搜索执行失败', subTitle=output, status='error')
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
                                    temp,
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
