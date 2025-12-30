from flask import Blueprint, render_template, redirect, url_for, request, jsonify
import traceback
from loguru import logger
from components.message_box import user_box, assistant_thinking_box, assistant_output_box, assistant_tool_call_box, tool_result_serper_search_box

component_bp = Blueprint('component', __name__)


# 获取用户消息盒子组件用于渲染，并且包含sse请求组件，开始请求大模型回复
@component_bp.route('/user_box', methods=['post'])
def get_user_box():
    try:
        data = request.json
        sse, component = user_box.render(**data)
        return jsonify(
            {
                'sse': sse,
                'component': component,
            }
        ), 200
    except Exception as e:
        logger.error(f'获取用户消息盒子组件失败: {e}\n{traceback.format_exc()}')


@component_bp.route('/assistant_thinking_box', methods=['post'])
def get_assistant_thinking_box():
    try:
        id_markdown, component = assistant_thinking_box.render()
        return jsonify(
            {
                'id_markdown': id_markdown,
                'component': component,
            }
        ), 200
    except Exception as e:
        logger.error(f'获取agent思考盒子组件失败: {e}\n{traceback.format_exc()}')


@component_bp.route('/assistant_output_box', methods=['post'])
def get_assistant_output_box():
    try:
        id_markdown, id_copy_markdown, component = assistant_output_box.render()
        return jsonify(
            {
                'id_copy_markdown': id_copy_markdown,
                'id_markdown': id_markdown,
                'component': component,
            }
        ), 200
    except Exception as e:
        logger.error(f'获取agent思考盒子组件失败: {e}\n{traceback.format_exc()}')


@component_bp.route('/assistant_tool_call_box', methods=['post'])
def get_assistant_tool_call_box():
    try:
        id_markdown, component = assistant_tool_call_box.render()
        return jsonify(
            {
                'id_markdown': id_markdown,
                'component': component,
            }
        ), 200
    except Exception as e:
        logger.error(f'获取agent请求工具调用盒子组件失败: {e}\n{traceback.format_exc()}')


@component_bp.route('/tool_result_serper_search_box', methods=['post'])
def get_tool_result_serper_search_box():
    try:
        status = request.json['status']
        output = request.json['output']
        component = tool_result_serper_search_box.render(status, output)
        return jsonify(
            {
                'component': component,
            }
        ), 200
    except Exception as e:
        logger.error(f'获取serper_search结果展示、盒子组件失败: {e}\n{traceback.format_exc()}')
