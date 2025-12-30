from dash import set_props, ClientsideFunction, Patch
import feffery_antd_components as fac
from dash.dependencies import Input, Output, State, ALL, MATCH
from server import app
import dash
import feffery_utils_components as fuc
from typing import Optional, List
from components.message_box import user_box
from configure import conf
from utils.digest_auth import digest_auth
from feffery_dash_utils.style_utils import style

### 对话配置回调

# 初始化模型选项
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='init_llm_select_options',
    ),
    [
        Output({'type': 'llm-model-select-dropdown', 'index': MATCH}, 'options'),
        Output({'type': 'llm-model-select-dropdown', 'index': MATCH}, 'value'),
        Output({'type': 'llm-model-style-dropdown', 'index': MATCH}, 'value'),
        Output({'type': conf.suffix_llm_model_selected, 'index': MATCH}, 'data'),
    ],
    Input({'type': 'llm-model-style-dropdown', 'index': MATCH}, 'options'),
    State({'type': conf.suffix_llm_model_selected, 'index': MATCH}, 'data'),
)

# 初始化对话dash历史记录
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='recoverHistoryConversationAreaList',
    ),
    Output({'type': 'conversation-area-list', 'index': MATCH}, 'children'),
    Input({'type': 'recover-istory-conversation-area-list-trigger', 'index': MATCH}, 'timeoutCount'),
    State({'type': conf.suffix_llm_dash_history_message_keyword, 'index': MATCH}, 'data'),
)


# 实时保存选择模型
app.clientside_callback(
    r"""(selected_model, selected_style) => {
        return {selected_model: selected_model, selected_style: selected_style};
    }""",
    Output({'type': conf.suffix_llm_model_selected, 'index': MATCH}, 'data', allow_duplicate=True),
    [
        Input({'type': 'llm-model-select-dropdown', 'index': MATCH}, 'value'),
        Input({'type': 'llm-model-style-dropdown', 'index': MATCH}, 'value'),
    ],
    prevent_initial_call=True,
)


# 弹出修改对话的modal
@app.callback(
    Output('container-modal', 'children', allow_duplicate=True),
    Input('op-classification-conversation', 'nClicks'),
    [
        State(conf.suffix_llm_store_map_user_id_last_classification_conversation_name, 'data'),
        State(conf.llm_store_classification_names, 'data'),
    ],
    prevent_initial_call=True,
)
def popup_op_classification_conversation_modal(nClicks, map_user_id_last_classification_conversation_name, classification_names):
    if nClicks is None:
        return dash.no_update
    user_id = digest_auth.user_id
    classification_conversation_name = map_user_id_last_classification_conversation_name[user_id]
    temp = conf.split_classification_conversation_name(classification_conversation_name)
    return fac.AntdModal(
        fac.AntdSpace(
            [
                fac.AntdSpace(
                    [
                        fac.AntdText('修改对话名: '),
                        fac.AntdInput(id={'type': 'op-classification-conversation-rename-new-name', 'index': classification_conversation_name}, value=''),
                        fac.AntdButton('修改', id={'type': 'op-classification-conversation-rename-btn', 'index': classification_conversation_name}, type='primary'),
                    ],
                    style=style(marginTop='10px'),
                ),
                fac.AntdSpace(
                    [
                        fac.AntdText('修改对话分类: '),
                        fac.AntdSelect(
                            options=[
                                {'label': '无分类', 'value': (i := digest_auth.user_id + conf.separator_user + conf.default_show_classification_name)},
                                *[{'label': conf.split_classification_name(i)['show_classification_name'], 'value': i} for i in classification_names],
                            ],
                            value=i,
                            style={'width': 150},
                            id={'type': 'op-classification-conversation-change-classification-name-tarage-classification-name', 'index': classification_conversation_name},
                        ),
                        fac.AntdButton(
                            '修改', id={'type': 'op-classification-conversation-change-classification-name-btn', 'index': classification_conversation_name}, type='primary'
                        ),
                    ],
                    style=style(marginTop='10px'),
                ),
                fac.AntdSpace(
                    [
                        fac.AntdPopconfirm(
                            fac.AntdButton('删除对话', danger=True, type='primary'),
                            id={'type': 'op-classification-conversation-remove-btn', 'index': classification_conversation_name},
                            description=f'对话名: {conf.split_classification_conversation_name(classification_conversation_name)["conversation_name"]}',
                            title='确切要删除吗',
                        ),
                    ],
                ),
            ],
            direction='vertical',
            addSplitLine=True,
        ),
        id={'type': 'modal-op-conversation-classification', 'index': classification_conversation_name},
        title=f'对话设置: {temp["conversation_name"]}',
        visible=True,
    )


# 修改对话名
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='renameClassificationConversationName',
    ),
    Output({'type': 'modal-op-conversation-classification', 'index': MATCH}, 'visible'),
    Input({'type': 'op-classification-conversation-rename-btn', 'index': MATCH}, 'nClicks'),
    [
        State({'type': 'op-classification-conversation-rename-new-name', 'index': MATCH}, 'value'),
        State({'type': 'op-classification-conversation-rename-new-name', 'index': MATCH}, 'id'),
    ],
    prevent_initial_call=True,
)

# 删除对话
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='removeClassificationConversation',
    ),
    Output({'type': 'modal-op-conversation-classification', 'index': MATCH}, 'visible', allow_duplicate=True),
    Input({'type': 'op-classification-conversation-remove-btn', 'index': MATCH}, 'confirmCounts'),
    State({'type': 'op-classification-conversation-remove-btn', 'index': MATCH}, 'id'),
    prevent_initial_call=True,
)

# 修改对话分类
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='changeClassificationNameOfClassificationConversation',
    ),
    Output({'type': 'modal-op-conversation-classification', 'index': MATCH}, 'visible', allow_duplicate=True),
    Input({'type': 'op-classification-conversation-change-classification-name-btn', 'index': MATCH}, 'nClicks'),
    [
        State({'type': 'op-classification-conversation-change-classification-name-tarage-classification-name', 'index': MATCH}, 'value'),
        State({'type': 'op-classification-conversation-change-classification-name-tarage-classification-name', 'index': MATCH}, 'id'),
    ],
    prevent_initial_call=True,
)


# 弹出设置指令窗口
@app.callback(
    Output({'type': 'set-classification-instruction', 'index': MATCH}, 'id'),
    Input({'type': 'set-classification-instruction', 'index': MATCH}, 'nClicks'),
    State({'type': conf.suffix_llm_instruction_keyword, 'index': MATCH}, 'data'),
    prevent_initial_call=True,
)
def popup_instruction_set_modal(nClicks, llm_instruction):
    set_props(
        'container-modal',
        {
            'children': fac.AntdModal(
                fac.AntdInput(
                    id='classification-instruction',
                    value=llm_instruction,
                    mode='text-area',
                ),
                id='classification-set-instruction-modal',
                title='设置指令',
                renderFooter=True,
                visible=True,
            )
        },
    )
    return dash.no_update


# 保存指令到指令store组件
@app.callback(
    Input('classification-set-instruction-modal', 'okCounts'),
    [
        State('classification-instruction', 'value'),
        State(conf.suffix_llm_store_map_user_id_last_classification_conversation_name, 'data'),
    ],
    prevent_initial_call=True,
)
def add_instruction(okCounts, instruction, map_user_id_last_classification_conversation_name):
    classification_conversation_name = map_user_id_last_classification_conversation_name[digest_auth.user_id]
    i = conf.split_classification_conversation_name(classification_conversation_name)
    classification_name, conversation_name = i['classification_name'], i['conversation_name']
    instruction = instruction or ''
    set_props(
        {'type': conf.suffix_llm_instruction_keyword, 'index': classification_name},
        {'data': instruction},
    )


### 文本输入框回调

app.clientside_callback(
    # 处理聊天区域的自动滚动策略
    ClientsideFunction(namespace='clientside', function_name='handleChatAreaScroll'),
    Input('listen-conversation-area-list-height', 'height'),
)

# 编辑用户消息
app.clientside_callback(
    # 控制用户信息输入框内容的发送
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleUserNewMessageEdit',
    ),
    Output({'type': 'input-text', 'index': MATCH}, 'value'),
    # 换行行为触发
    Input({'type': 'ctrl-enter-keypress', 'index': MATCH}, 'pressedCounts'),
    [
        State({'type': 'input-text', 'index': MATCH}, 'focusing'),
        State({'type': 'input-text', 'index': MATCH}, 'value'),
    ],
    prevent_initial_call=True,
)


# 发送用户消息
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleUserNewMessageSend',
    ),
    [
        Output({'type': 'input-text', 'index': MATCH}, 'value', allow_duplicate=True),
        Output({'type': 'conversation-area-list', 'index': MATCH}, 'children', allow_duplicate=True),
        Output({'type': 'container-sse', 'index': MATCH}, 'children'),
        Output({'type': 'btn-send-input-text', 'index': MATCH}, 'loading'),
        Output({'type': 'btn-stop-input-text', 'index': MATCH}, 'disabled'),
    ],
    [
        # 发送行为触发
        Input({'type': 'enter-keypress', 'index': MATCH}, 'pressedCounts'),
        Input({'type': 'btn-send-input-text', 'index': MATCH}, 'nClicks'),
    ],
    [
        # 发送行为触发
        State({'type': 'input-text', 'index': MATCH}, 'value'),
        State({'type': 'input-text', 'index': MATCH}, 'focusing'),
        # 大模型配置
        State({'type': 'llm-model-select-dropdown', 'index': MATCH}, 'value'),
        State({'type': 'llm-model-style-dropdown', 'index': MATCH}, 'value'),
        # 长期记忆
        State({'type': 'activate-long-memory', 'index': MATCH}, 'checked'),
        # 工具调用
        State({'type': 'activate-toolsets', 'index': MATCH}, 'value'),
        # Store历史会话pydantic
        State({'type': conf.suffix_llm_history_message_keyword, 'index': MATCH}, 'data'),
        # 是否正在发生
        State({'type': 'btn-send-input-text', 'index': MATCH}, 'loading'),
        # bearer token
        State('store-bearer-token', 'data'),
    ],
    prevent_initial_call=True,
)

# 大模型响应sse的UI渲染
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleAssistantMessageYield',
    ),
    Output({'type': 'conversation-area-list', 'index': MATCH}, 'children', allow_duplicate=True),
    Input({'type': 'conversation-sse', 'index': MATCH}, 'data'),
    [
        State({'type': conf.suffix_llm_history_message_keyword, 'index': MATCH}, 'id'),
        State({'type': 'btn-send-input-text', 'index': MATCH}, 'id'),
        State({'type': 'btn-stop-input-text', 'index': MATCH}, 'id'),
    ],
    prevent_initial_call=True,
)

# 强行停止
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='handleStopAssistantMessage',
    ),
    [
        Output({'type': 'conversation-sse', 'index': MATCH}, 'operation'),
        Output({'type': 'btn-send-input-text', 'index': MATCH}, 'loading', allow_duplicate=True),
        Output({'type': 'btn-stop-input-text', 'index': MATCH}, 'disabled', allow_duplicate=True),
    ],
    Input({'type': 'btn-stop-input-text', 'index': MATCH}, 'nClicks'),
    prevent_initial_call=True,
)

# 实时保存dash的历史会话记录
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='SaveConversationAreaList',
    ),
    Output({'type': conf.suffix_llm_dash_history_message_keyword, 'index': MATCH}, 'data'),
    Input({'type': 'conversation-area-list', 'index': MATCH}, 'children'),
    prevent_initial_call=True,
)
