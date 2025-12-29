import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from configure import conf


def render_conversation_header_content(classification_conversation_name, show_add_instruction: bool):
    i = conf.split_classification_conversation_name(classification_conversation_name)
    classification_name, conversation_name = i['classification_name'], i['conversation_name']
    return fac.AntdRow(
        [
            fac.AntdCol(
                fac.AntdSpace(
                    [
                        fac.AntdBreadcrumb(items=[{'title': i} for i in conf.readable_classification_conversation_name(classification_conversation_name)]),
                        fac.AntdSpace(
                            [
                                fac.AntdText(
                                    '模型选择：',
                                    italic=True,
                                    style={
                                        'fontSize': 16,
                                        'marginLeft': '16px',
                                    },
                                ),
                                fac.AntdCompact(
                                    [
                                        # 选择模型
                                        fac.AntdSelect(
                                            variant='filled',
                                            id={'type': 'llm-model-select-dropdown', 'index': classification_conversation_name},
                                            prefix=fac.AntdIcon(icon='antd-openai'),
                                            popupMatchSelectWidth=False,
                                            style={'width': '200px'},
                                            allowClear=False,
                                        ),
                                        # 风格设定
                                        fac.AntdSelect(
                                            variant='filled',
                                            id={'type': 'llm-model-style-dropdown', 'index': classification_conversation_name},
                                            options=[
                                                {'label': '平衡', 'value': '平衡'},
                                                {'label': '严谨', 'value': '严谨'},
                                                {'label': '创意', 'value': '创意'},
                                                {'label': '自由', 'value': '自由'},
                                            ],
                                            popupMatchSelectWidth=False,
                                            style={'width': '80px'},
                                            allowClear=False,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className=style(
                        height='60px',
                        paddingLeft='60px',  # 根折叠按钮错开
                    ),
                )
            ),
            fac.AntdCol(
                fac.AntdSpace(
                    [
                        # 分类的设置
                        fac.AntdButton('设置分类指令', id={'type': 'set-classification-instruction', 'index': classification_name}) if show_add_instruction else fac.Fragment(),
                        fac.AntdButton(
                            fac.AntdIcon(icon='antd-setting', style=style(fontSize=20)),
                            id='op-classification-conversation',
                            style=style(width=30, height=30),
                            type='text',
                        ),
                    ],
                    style=style(height='100%', paddingRight=20),
                )
            ),
        ],
        wrap=False,
        justify='space-between',
        align='middle',
        className=style(borderBottom='1px solid #dfe4ea'),
    )
