import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from configure import conf


def render_conversation_input_content(classification_conversation_name):
    """渲染用户输入区域"""

    return fuc.FefferyDiv(
        [
            fac.Fragment(
                [
                    # ctrl+enter事件监听
                    fuc.FefferyKeyPress(id={'type': 'ctrl-enter-keypress', 'index': classification_conversation_name}, keys='ctrl.enter'),
                    # enter事件监听
                    fuc.FefferyKeyPress(id={'type': 'enter-keypress', 'index': classification_conversation_name}, keys='enter'),
                ]
            ),
            fac.AntdSpace(
                [
                    fac.AntdText('长期记忆：', strong=True),
                    fac.AntdCheckableTag(
                        id={'type': 'activate-long-memory', 'index': classification_conversation_name},
                        checkedContent=fac.AntdSpace([fac.AntdIcon(icon='md-cloud-upload'), '已激活'], align='center'),
                        unCheckedContent=fac.AntdSpace([fac.AntdIcon(icon='antd-api'), '未激活'], align='center'),
                        style=style(border='1px solid #7f8c8d'),
                        checked=True,
                    ),
                    fac.AntdText('工具：', strong=True),
                    fac.AntdSelect(
                        id={'type': 'activate-toolsets', 'index': classification_conversation_name},
                        options=[
                            {'label': '联网搜索', 'value': 'serper_search'},
                        ],
                        mode='multiple',
                        style={
                            'height': '17%',
                            'width': 250,
                        },
                    ),
                ]
            ),
            # 对话输入框
            fac.AntdInput(
                id={'type': 'input-text', 'index': classification_conversation_name},
                placeholder='Enter 发送，Ctrl + Enter 换行',
                mode='text-area',
                style={
                    'height': '70%',
                    'position': 'absolute',
                    'bottom': 8,
                    'right': 20,
                    'width': 'calc(100% - 40px)',
                },
            ),
            # 对话发送按钮
            fac.AntdButton(
                '发送',
                id={'type': 'btn-send-input-text', 'index': classification_conversation_name},
                debounceWait=1000,
                icon=fac.AntdIcon(icon='antd-export'),
                type='primary',
                size='large',
                loadingChildren='输出中',
                style={
                    'position': 'absolute',
                    'right': 78,
                    'bottom': 20,
                },
            ),
            # 对话强行停止按钮
            fac.AntdButton(
                id={'type': 'btn-stop-input-text', 'index': classification_conversation_name},
                disabled=True,
                debounceWait=1000,
                icon=fac.AntdIcon(icon='antd-stop'),
                variant='solid',
                color='danger',
                size='large',
                style={
                    'position': 'absolute',
                    'right': 36,
                    'bottom': 20,
                },
            ),
        ],
        className={
            'borderTop': '1px solid #e5e5e5',
            'height': '200px',
            'boxSizing': 'border-box',
            'position': 'relative',
            'padding': '8px 20px',
            '& textarea': style(padding='10px 110px 10px 14px'),
            '& .ant-btn-icon': style(marginRight='2px !important'),
        },
    )
