import feffery_antd_components as fac
from feffery_dash_utils.style_utils import style
from components import conversation_header, conversation_area, conversation_input
import callbacks.conversation_c  # noqa: F401
import callbacks.tool_c  # noqa: F401


def render_conversation_interface_content(classification_conversation_name, show_add_instruction: bool):
    return fac.AntdFlex(
        [
            conversation_header.render_conversation_header_content(
                classification_conversation_name=classification_conversation_name,
                show_add_instruction=show_add_instruction,
            ),
            conversation_area.render_conversation_area_content(
                classification_conversation_name=classification_conversation_name,
            ),
            conversation_input.render_conversation_input_content(classification_conversation_name=classification_conversation_name),
        ],
        vertical=True,
        wrap=False,
        className=style(height='100%', width='100%'),
    )
