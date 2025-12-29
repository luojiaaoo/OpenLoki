import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import dcc
from views import aside
from feffery_dash_utils.style_utils import style
from server import app, server  # noqa: F401
import callbacks.app_c  # noqa: F401
from configure import conf


def render_layout():
    collapse_btn = fac.AntdButton(
        id='btn-menu-collapse-sider-menu',
        color='default',
        variant='link',
        icon=fac.AntdIcon(
            id='btn-menu-collapse-sider-menu-icon',
            icon='antd-menu-fold',
        ),
        debounceWait=300,
        className={
            '&': style(
                position='absolute',  # 相对AntdSider绝对定位，脱离文档流
                top=0,
                right='-2em',  # 突出2个字体大小
                zIndex=9999,  # 绝对大的层叠高度
                fontSize='1.7em',
                marginTop='15px',
            )
        },
    )
    layout = fac.AntdConfigProvider(
        [
            # 特殊用途
            fac.Fragment(
                [
                    fuc.FefferySetFavicon(favicon='/assets/logo.ico'),  # 设置favicon
                    fuc.FefferyExecuteJs(id='global-exec-js'),
                    # 当前选中的对话名字, 为下次登录直接切换到最后访问的对话做准备
                    dcc.Store(id=conf.suffix_llm_store_map_user_id_last_classification_conversation_name, storage_type='local'),
                    # 保存登录用户名
                    dcc.Store(id='store-user-id'),
                    # 当前的分类名
                    dcc.Store(id='store-last-classification-name'),
                    # 保存用户名和分类对话名的分隔符
                    dcc.Store(id='store-separator-user', data=conf.separator_user),
                    # 保存分类和对话名的分隔符
                    dcc.Store(id='store-separator-cls-conv', data=conf.separator_cls_conv),
                ]
            ),
            # 定时生成Bearer Token组件
            fac.Fragment(
                [
                    fuc.FefferyTimeout(delay=1, id='timeout-for-set-bearer-token'),  # 马上触发一次
                    dcc.Interval(id='interval-for-set-bearer-token', interval=1000 * 60),  # 每60秒生成授权token，用于后端的鉴权
                    dcc.Store(id='store-bearer-token', storage_type='session'),  # 存储最新的Bearer Token
                ]
            ),
            # 对话存储组件
            fac.Fragment(
                [
                    # 存储LLM所有分类名
                    dcc.Store(id=conf.llm_store_classification_names, storage_type='local'),
                    # 存储LLM所有有会话名
                    dcc.Store(id=conf.llm_store_classification_conversation_names, storage_type='local'),
                    # LLM当前会话的的存储组件的容器
                    fac.Fragment(id='container-llm-things'),
                ]
            ),
            # 刷新菜单页
            dcc.Store(id='flush-main-menu-menu-items'),
            # 页面重载或关闭事件监听
            fuc.FefferyListenUnload(id='listen-unload'),
            # 全局消息提示
            fac.Fragment(id='global-message'),
            # 对话框容器
            fac.Fragment(id='container-modal'),
            # 内容页
            fac.AntdRow(
                [
                    # 菜单列
                    fac.AntdCol(
                        fac.AntdSider(
                            [
                                aside.render_aside_content(),
                                collapse_btn,
                            ],
                            collapsed=False,  # 默认不折叠
                            collapsible=True,  # 可折叠
                            collapsedWidth=60,  # 折叠宽度
                            width=225,  # 不折叠宽度
                            trigger=None,
                            id='menu-collapse-sider',
                            className={
                                '&': {
                                    'position': 'relative',
                                    'height': '100%',
                                }  # 相对定位
                            },
                        ),
                        flex='None',
                    ),
                    dcc.Store(id='init-container-conversation'),
                    fac.AntdCol(
                        id='container-conversation',
                        className=style(flexGrow=1, height='100vh'),
                    ),
                ],
                className={'width': '100vw', 'height': '100vh'},
                wrap=False,
            ),
        ]
    )
    return layout


app.layout = render_layout


if __name__ == '__main__':
    app.run(debug=not conf.is_launch_prod, host=conf.frontend_bind_host, port=conf.frontend_port)
