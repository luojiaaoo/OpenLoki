from dash import ClientsideFunction, set_props, dcc, ctx, html
import feffery_antd_components as fac
from dash.dependencies import Input, Output, State, MATCH
from server import app
import dash
from views import conversation_interface
import feffery_utils_components as fuc
from typing import Optional, List, Dict
from configure import conf
import uuid
from utils.digest_auth import digest_auth
from feffery_dash_utils.style_utils import style


# 加载菜单
@app.callback(
    [
        Output('main-menu', 'menuItems'),
        Output('store-user-id', 'data'),
    ],
    Input('flush-main-menu-menu-items', 'data'),
    [
        State(conf.llm_store_classification_conversation_names, 'data'),
        State(conf.llm_store_classification_names, 'data'),
    ],
)
def add_menu_items(_, llm_store_classification_conversation_names: Optional[List], llm_store_classification_names: Optional[List]):
    ## 选出当前用户的
    # 对话
    llm_store_classification_conversation_names = llm_store_classification_conversation_names or []
    llm_store_classification_conversation_names = [i for i in llm_store_classification_conversation_names if i.startswith(digest_auth.user_id + conf.separator_user)]
    # 分类
    llm_store_classification_names = llm_store_classification_names or []
    classification_names = [i for i in llm_store_classification_names if i.startswith(digest_auth.user_id + conf.separator_user)] or []

    ## 区分独立和分类会话
    # 独立对话
    classification_conversation_names_of_default = [
        ((j := conf.split_classification_conversation_name(i))['classification_name'], j['conversation_name'], i)
        for i in llm_store_classification_conversation_names
        if conf.is_default_classification(i)
    ]
    # 分类对话
    classification_conversation_names_of_classification = [
        ((j := conf.split_classification_conversation_name(i))['classification_name'], j['conversation_name'], i)
        for i in llm_store_classification_conversation_names
        if not conf.is_default_classification(i)
    ]
    return (
        [
            {
                'component': 'Item',
                'props': {
                    'key': 'function: add_conversation',
                    'title': '新建对话',
                    'icon': 'antd-form',
                },
            },
            {
                'component': 'Item',
                'props': {
                    'key': 'function: add_classification',
                    'title': '新建分类',
                    'icon': 'antd-import',
                },
            },
            *[
                {
                    'component': 'SubMenu',
                    'props': {
                        'key': 'classification_' + classification_name,  # 分类
                        'title': conf.split_classification_name(classification_name)['show_classification_name'],
                        'icon': 'antd-block',
                    },
                    # 子对话
                    'children': [
                        {
                            'component': 'Item',
                            'props': {
                                'key': f'function: setting_classification_{classification_name}',  # 添加分类的对话
                                'title': '分类设置',
                                'icon': 'antd-setting',
                            },
                        },
                        {
                            'component': 'Item',
                            'props': {
                                'key': f'function: add_conversation_for_classification_{classification_name}',  # 添加分类的对话
                                'title': '添加对话',
                                'icon': 'pi-plus',
                            },
                        },
                        *[
                            {
                                'component': 'Item',
                                'props': {
                                    'key': classification_conversation_name_of_classification[-1],
                                    'title': classification_conversation_name_of_classification[1],
                                    'icon': 'fc-faq',
                                },
                            }
                            for classification_conversation_name_of_classification in classification_conversation_names_of_classification
                            if classification_conversation_name_of_classification[0] == classification_name
                        ],
                    ],
                }
                for classification_name in classification_names
            ],
            # 独立对话
            *[
                {
                    'component': 'Item',
                    'props': {
                        'key': classification_conversation_name_of_default[-1],  # 完整分类会话名
                        'title': classification_conversation_name_of_default[1],  # 会话名
                        'icon': 'antd-wechat-work',
                    },
                }
                for classification_conversation_name_of_default in classification_conversation_names_of_default
            ],
        ],  # 目录结构
        digest_auth.user_id,
    )


# 新建的对话框
@app.callback(
    [
        Output('container-modal', 'children'),
        Output('main-menu', 'currentKey'),
    ],
    Input('main-menu', 'currentKey'),
    prevent_initial_call=True,
)
def popup_conversation_modal(current_key: str):
    if not current_key or (current_key and not current_key.startswith('function: ')):
        return dash.no_update
    if current_key == 'function: add_conversation':
        return fac.AntdModal(
            fac.AntdInput(id='add-conversation-name', value=''),
            id='modal-add-conversation',
            title='新建对话',
            renderFooter=True,
            visible=True,
        ), None
    elif current_key == 'function: add_classification':
        return fac.AntdModal(
            fac.AntdInput(id='add-classification-name', value=''),
            id='modal-add-classification',
            title='新建分类',
            renderFooter=True,
            visible=True,
        ), None
    elif current_key.startswith(i := 'function: add_conversation_for_classification_'):  # 新建分类会话
        classification_name = current_key.replace(i, '')
        return [
            [
                dcc.Store(id='store-add-conversation-name-for-classification', data=classification_name),
                fac.AntdModal(
                    fac.AntdInput(id='add-conversation-name-for-classification', value=''),
                    id='modal-add-conversation-for-classification',
                    title='添加对话',
                    renderFooter=True,
                    visible=True,
                ),
            ],
            None,
        ]
    elif current_key.startswith(i := 'function: setting_classification_'):  # 修改分类名
        classification_name = current_key.replace(i, '')
        show_classification_name = conf.split_classification_name(classification_name)['show_classification_name']
        return [
            [
                fac.AntdModal(
                    fac.AntdSpace(
                        [
                            fac.AntdSpace(
                                [
                                    fac.AntdText('修改分类名: '),
                                    fac.AntdInput(id={'type': 'op-classification-rename-new-name', 'index': classification_name}, value=''),
                                    fac.AntdButton('修改', id={'type': 'op-classification-rename-btn', 'index': classification_name}, type='primary'),
                                ],
                                style=style(marginTop='10px'),
                            ),
                            fac.AntdSpace(
                                [
                                    fac.AntdPopconfirm(
                                        fac.AntdButton('删除分类', danger=True, type='primary'),
                                        id={'type': 'op-classification-remove-btn', 'index': classification_name},
                                        description=f'分类: {show_classification_name}',
                                        title='确切要删除吗',
                                    ),
                                ],
                            ),
                        ],
                        direction='vertical',
                        addSplitLine=True,
                    ),
                    id={'type': 'modal-op-classification', 'index': classification_name},
                    title=f'分类设置: {show_classification_name}',
                    visible=True,
                ),
            ],
            None,
        ]
    return dash.no_update


# 新建默认分类的对话，激活新建的菜单item
@app.callback(
    [
        Output('flush-main-menu-menu-items', 'data'),
        Output('main-menu', 'currentKey', allow_duplicate=True),
        Output(conf.llm_store_classification_conversation_names, 'data'),
    ],
    [
        Input('modal-add-conversation', 'okCounts', allow_optional=True),
        Input('modal-add-conversation-for-classification', 'okCounts', allow_optional=True),
    ],
    [
        State('add-conversation-name', 'value', allow_optional=True),
        State('store-add-conversation-name-for-classification', 'data', allow_optional=True),
        State('add-conversation-name-for-classification', 'value', allow_optional=True),
        State(conf.llm_store_classification_conversation_names, 'data'),
    ],
    prevent_initial_call=True,
)
def new_conversation(
    okCounts,
    okCounts_,
    add_conversation_name_default: str,
    store_add_conversation_name_for_classification: str,
    add_conversation_name_for_classification: str,
    llm_store_classification_conversation_names: Optional[List],
):
    user_id = digest_auth.user_id
    if okCounts is None and ctx.triggered_id == 'modal-add-conversation':  # Input比Output后产生，避免不了初始化回调，需要条件过滤
        return dash.no_update
    if okCounts_ is None and ctx.triggered_id == 'modal-add-conversation-for-classification':  # Input比Output后产生，避免不了初始化回调，需要条件过滤
        return dash.no_update
    llm_store_classification_conversation_names = llm_store_classification_conversation_names or []
    if ctx.triggered_id == 'modal-add-conversation':
        # 检查名字的合法性
        add_conversation_name_default = add_conversation_name_default.strip()
        if not add_conversation_name_default or not conf.is_valid_name(add_conversation_name_default):
            set_props('global-message', {'children': fac.AntdMessage(content='对话名不能为空', type='error')})
            return dash.no_update
        classification_conversation_name = user_id + conf.separator_user + conf.default_show_classification_name + conf.separator_cls_conv + add_conversation_name_default
    elif ctx.triggered_id == 'modal-add-conversation-for-classification':
        # 检查名字的合法性
        add_conversation_name_for_classification = add_conversation_name_for_classification.strip()
        if not add_conversation_name_for_classification or not conf.is_valid_name(add_conversation_name_for_classification):
            set_props('global-message', {'children': fac.AntdMessage(content='对话名不能为空', type='error')})
            return dash.no_update
        classification_conversation_name = store_add_conversation_name_for_classification + conf.separator_cls_conv + add_conversation_name_for_classification
    # 检查是否创建过
    if classification_conversation_name in llm_store_classification_conversation_names:
        set_props(
            'global-message',
            {
                'children': fac.AntdMessage(
                    content=f'{"/".join(conf.readable_classification_conversation_name(classification_conversation_name))} 已经创建过，请更换对话名', type='error'
                )
            },
        )
        return dash.no_update
    llm_store_classification_conversation_names.append(classification_conversation_name)
    return (
        uuid.uuid4().hex,  # 刷新菜单
        classification_conversation_name,  # 当前激活的菜单
        llm_store_classification_conversation_names,  # 保存当前的分类会话名
    )


# 添加自定义分类
@app.callback(
    [
        Output('flush-main-menu-menu-items', 'data', allow_duplicate=True),
        Output(conf.llm_store_classification_names, 'data'),
    ],
    Input('modal-add-classification', 'okCounts'),
    [
        State('add-classification-name', 'value'),
        State(conf.llm_store_classification_names, 'data'),
    ],
    prevent_initial_call=True,
)
def new_classification(okCounts, add_classification_name: str, llm_store_classification_names: Optional[List]):
    if okCounts is None:  # Input比Output后产生，避免不了初始化回调，需要条件过滤
        return dash.no_update
    llm_store_classification_names = llm_store_classification_names or []
    # 检查名字的合法性
    add_classification_name = add_classification_name.strip()
    if not add_classification_name or add_classification_name == conf.default_show_classification_name or not conf.is_valid_name(add_classification_name):
        set_props('global-message', {'children': fac.AntdMessage(content='分类名不能为空', type='error')})
        return dash.no_update
    # 检查是否创建过
    classification_name = digest_auth.user_id + conf.separator_user + add_classification_name
    if classification_name in llm_store_classification_names:
        set_props(
            'global-message',
            {'children': fac.AntdMessage(content=f'{add_classification_name} 已经创建过，请更换分类名', type='error')},
        )
        return dash.no_update
    llm_store_classification_names.append(classification_name)
    return (
        uuid.uuid4().hex,  # 刷新菜单
        llm_store_classification_names,  # 保存当前的分类会话名
    )


# 更新分类名
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='RenameClassificationName',
    ),
    Output({'type': 'modal-op-classification', 'index': MATCH}, 'visible'),
    Input({'type': 'op-classification-rename-btn', 'index': MATCH}, 'nClicks'),
    [
        State({'type': 'op-classification-rename-new-name', 'index': MATCH}, 'value'),
        State({'type': 'op-classification-rename-new-name', 'index': MATCH}, 'id'),
    ],
    prevent_initial_call=True,
)

# 删除分类
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='RemoveClassificationName',
    ),
    Output({'type': 'modal-op-classification', 'index': MATCH}, 'visible', allow_duplicate=True),
    Input({'type': 'op-classification-remove-btn', 'index': MATCH}, 'confirmCounts'),
    State({'type': 'op-classification-rename-new-name', 'index': MATCH}, 'id'),
    prevent_initial_call=True,
)


# 根据菜单的激活，渲染不同的对话窗口
@app.callback(
    [
        Output('container-conversation', 'children', allow_duplicate=True),  # 渲染聊天窗口
        Output(conf.suffix_llm_store_map_user_id_last_classification_conversation_name, 'data'),  # 当前选中的分类对话名字
        Output('store-last-classification-name', 'data'),  # 当前选中的对话名字
        Output('container-llm-things', 'children'),
    ],
    Input('main-menu', 'currentKey'),
    State(conf.suffix_llm_store_map_user_id_last_classification_conversation_name, 'data'),
    prevent_initial_call=True,
)
def select_conversation_name(current_key: str, map_user_id_last_classification_conversation_name):
    map_user_id_last_classification_conversation_name = map_user_id_last_classification_conversation_name or {}
    current_key = current_key or ''
    if conf.separator_cls_conv in current_key:  # 判断是对话key
        classification_conversation_name = current_key
        is_default_classification = conf.is_default_classification(classification_conversation_name)
        i = conf.split_classification_conversation_name(classification_conversation_name)
        classification_name, conversation_name = i['classification_name'], i['conversation_name']
        return (
            conversation_interface.render_conversation_interface_content(
                classification_conversation_name=classification_conversation_name,
                show_add_instruction=not is_default_classification,
            ),
            {**map_user_id_last_classification_conversation_name, digest_auth.user_id: classification_conversation_name},
            conf.split_classification_conversation_name(classification_conversation_name)['classification_name'],
            [
                fuc.FefferyLocalLargeStorage(
                    id={'type': conf.suffix_llm_dash_history_message_keyword, 'index': classification_conversation_name},
                    initialSync=True,
                    key=uuid.uuid4().hex,
                ),
                fuc.FefferyLocalLargeStorage(
                    id={'type': conf.suffix_llm_history_message_keyword, 'index': classification_conversation_name},
                    initialSync=True,
                    key=uuid.uuid4().hex,
                ),
                dcc.Store(id={'type': conf.suffix_llm_model_selected, 'index': classification_conversation_name}, storage_type='local'),
                fuc.FefferyLocalLargeStorage(
                    id={'type': conf.suffix_llm_instruction_keyword, 'index': classification_name},
                    initialSync=True,
                    key=uuid.uuid4().hex,
                ),
                fac.Fragment(id={'type': 'container-sse', 'index': classification_conversation_name}),
                fuc.FefferyTimeout(id={'type': 'recover-istory-conversation-area-list-trigger', 'index': classification_conversation_name}, delay=500),
            ],
        )
    return dash.no_update
