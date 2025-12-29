from configure import conf
import feffery_utils_components as fuc
from dash import ClientsideFunction, set_props
from dash.dependencies import Input, Output, State
from server import app
import dash
from utils.digest_auth import digest_auth
from datetime import datetime, timezone, timedelta
import jwt

# 折叠菜单
app.clientside_callback(
    ClientsideFunction(
        namespace='app_clientside',
        function_name='collapse_menu',
    ),
    [
        Output('menu-collapse-sider', 'collapsed', allow_duplicate=True),
        Output('btn-menu-collapse-sider-menu-icon', 'icon'),
        Output('logo-text', 'style'),
    ],
    Input('btn-menu-collapse-sider-menu', 'nClicks'),
    State('menu-collapse-sider', 'collapsed'),
    prevent_initial_call=True,
)


@app.callback(
    Output('store-bearer-token', 'data'),
    [
        Input('interval-for-set-bearer-token', 'n_intervals'),
        Input('timeout-for-set-bearer-token', 'timeoutCount'),
    ],
)
def set_token(n_intervals, timeout_count):
    to_encode = {'user_id': digest_auth.user_id}
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)  # 要大于interval-for-set-bearer-token的周期
    to_encode.update({'exp': expire})
    access_token = jwt.encode(to_encode, conf.jwt_secret_key, algorithm='HS256')
    return access_token


# 加载欢迎界面
@app.callback(
    Output('container-conversation', 'children'),
    Input('init-container-conversation', 'data'),
    State(conf.suffix_llm_store_map_user_id_last_classification_conversation_name, 'data'),
)
def welcome(_, map_user_id_last_classification_conversation_name):
    map_user_id_last_classification_conversation_name = map_user_id_last_classification_conversation_name or {}
    if digest_auth.user_id in map_user_id_last_classification_conversation_name:
        set_props('main-menu', {'currentKey': map_user_id_last_classification_conversation_name[digest_auth.user_id]})
    return [
        fuc.FefferyRawHTML(
            htmlString=f"""
<div class="welcome_container">
    <div class="header">
        欢迎{digest_auth.user_id}使用 DeepLoki {conf.app_version} AI 助手
    </div>
    <div class="intro">
        我是一个智能助手，随时为您提供帮助！点击新建对话，开始探索我的能力吧！
    </div>
</div>
"""
        ),
        fuc.FefferyStyle(
            rawStyle="""
/* 标题样式 */
.welcome_container .header {
    background: rgba(0, 0, 0, 0.3);
    color: white;
    font-size: 3em;
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    margin-bottom: 30px;
    letter-spacing: 2px;
}

/* 内容容器样式 */
.welcome_container {
    background: white;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    text-align: center;
    width: 70%;
    max-width: 800px;
    transition: transform 0.3s ease-in-out;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

/* 鼠标悬停时的动画效果 */
.welcome_container:hover {
    transform: translate(-50%, -50%) scale(1.05);
}

/* 简介文本样式，加入打字机效果 */
.welcome_container .intro {
    font-size: 1.1em;
    color: #666;
    margin: 20px 0;
    line-height: 1.6;
    letter-spacing: 0.5px;
    overflow: hidden; /* 隐藏多余文本 */
    white-space: nowrap; /* 禁止换行 */
    width: 0;
    animation: typing 2s steps(50) 0.2s forwards, blink 0.75s step-end infinite;
}

/* 打字机效果的关键帧动画 */
@keyframes typing {
    to {
        width: 100%;
    }
}

/* 光标闪烁效果 */
@keyframes blink {
    50% {
        border-color: transparent;
    }
}
"""
        ),
    ]
