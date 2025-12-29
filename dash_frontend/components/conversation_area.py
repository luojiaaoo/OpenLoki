from dash import Input, MATCH, Output, State
import feffery_antd_components as fac
import feffery_utils_components as fuc
from server import app
from dash._utils import stringify_id


def render_conversation_area_content(classification_conversation_name):
    """渲染对话区域"""

    return fuc.FefferyDiv(
        [
            fac.AntdFlex(
                children=[],
                id={'type': 'conversation-area-list', 'index': classification_conversation_name},
                className={'width': '100%'},
                vertical=True,
                gap=10,
            ),
            # 聊天消息列表像素高度监听
            fuc.FefferyListenElementSize(
                id={'type': 'listen-conversation-area-list-height', 'index': classification_conversation_name},
                target=stringify_id({'type': 'conversation-area-list', 'index': classification_conversation_name}),
            ),
        ],
        id={'type': 'conversation-area', 'index': classification_conversation_name},
        className={
            '&': {
                'overflowY': 'auto',
                'padding': '20px 20px 30px',
                'scrollbar-width': 'thin',
                'scrollbar-color': 'rgba(144,147,153,.2) #fff',
                'flex': 1,
            },
        },
    )


app.clientside_callback(
    # 聊天区域的自动滚动
    """(height, area_id) => {
        let scrollTarget = document.getElementById(dash_component_api.stringifyId(area_id))
        scrollTarget.scrollTo({
            top: scrollTarget.scrollHeight
        });
        return window.dash_clientside.no_update;
    }""",
    Output({'type': 'listen-conversation-area-list-height', 'index': MATCH}, 'id'),
    Input({'type': 'listen-conversation-area-list-height', 'index': MATCH}, 'height'),
    State({'type': 'conversation-area', 'index': MATCH}, 'id'),
    prevent_initial_call=True,
)
