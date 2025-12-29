import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import get_asset_url
from configure import conf
from feffery_dash_utils.style_utils import style
import callbacks.aside_c  # noqa: F401


def render_aside_content():
    return fuc.FefferyDiv(
        [
            # logo 和 app名
            fac.AntdFlex(
                fac.AntdSpace(
                    [
                        fac.AntdImage(
                            width=40,
                            height=40,
                            src=get_asset_url('imgs/logo.png'),
                            preview=False,
                        ),
                        fac.AntdText(
                            conf.app_title,
                            id='logo-text',
                            ellipsis=True,
                            className={
                                'fontSize': '20px',
                                'fontWeight': 'bold',
                            },
                        ),
                    ],
                    style=style(height=60),
                ),
                className={
                    # 'height': '60px',
                    'background': 'rgb(249,249,249)',
                    'position': 'sticky',
                    'top': 0,
                    'zIndex': 999,
                    'paddingTop': '8px',
                    'paddingLeft': '12px',
                    # 'paddingRight': '20px',
                    # 'paddingBottom': '12px',
                },
            ),
            # 目录
            fac.AntdRow(
                fac.AntdMenu(
                    id='main-menu',
                    menuItems=[],
                    menuItemKeyToTitle={},
                    mode='inline',
                    currentKey=None,
                    # defaultOpenKeys=['classification'],
                    onlyExpandCurrentSubMenu=True,
                    inlineIndent=16,
                    expandIcon={
                        'expand': fac.AntdIcon(icon='antd-right'),
                        'collapse': fac.AntdIcon(icon='antd-down'),
                    },
                    style=style(border=0),
                ),
                style=style(flex=1),
            ),
        ],
        # 修改目录的样式
        className={
            '.ant-menu': {'backgroundColor': 'rgb(249,249,249)', 'overflow': 'hidden'},
            '.ant-menu-item-selected': {
                'color': 'black',
                'backgroundColor': 'rgb(231,231,231)',
                'borderRadius': '0em',
            },
            '.ant-menu-root > .ant-menu-item:nth-child(1)': style(
                borderRadius=0,
            ),
            '.ant-menu-root > .ant-menu-item:nth-child(2)': style(  # 新建会话下面的分割线
                borderBottom='2px solid #7f8c8d',
                borderRadius=0,
            ),
            '.ant-menu-sub .ant-menu-item:nth-child(1)': style(  # 降低高度
                height='25px',
                borderRadius='0',
                borderTop='1px dashed #7f8c8d',
                borderLeft='1px dashed #7f8c8d',
                borderRight='1px dashed #7f8c8d',
                margin='0 0 0 10',
            ),
            '.ant-menu-sub .ant-menu-item:nth-child(2)': style(  # 分类下面创建会话的分割线
                height='25px',
                borderBottom='1px dashed #7f8c8d',
                borderLeft='1px dashed #7f8c8d',
                borderRight='1px dashed #7f8c8d',
                borderRadius='0',
                margin='0 0 0 10',
            ),
            '&': {
                'background': 'rgb(249,249,249)',
                'borderRight': '2px solid #7f8c8d',
                'overflowY': 'auto',
                'overflowX': 'hidden',
                'scrollbar-width': 'thin',
                'scrollbar-color': 'rgba(144,147,153,.2) #fff',
                'height': '100%',
            },
        },
    )
