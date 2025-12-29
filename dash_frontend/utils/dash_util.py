import json


def process_object(obj):
    """
    先递归处理所有 children，然后处理当前对象
    """
    result = None

    # 如果是列表，处理每个元素
    if isinstance(obj, list):
        result = []
        for item in obj:
            result.append(process_object(item))
        return result

    # 如果有 children 属性，先处理 children
    if hasattr(obj, 'children'):
        children = obj.children

        if isinstance(children, list):
            new_children = []
            for child in children:
                new_children.append(process_object(child))
            obj.children = new_children

        elif children is not None:  # 单个 child
            obj.children = process_object(children)

    # 处理完 children 后，处理当前对象
    if hasattr(obj, 'to_plotly_json'):
        return obj.to_plotly_json()

    return obj


def stringify_id(id_) -> str:
    def _json(k, v):
        vstr = v.to_json() if hasattr(v, 'to_json') else json.dumps(v, ensure_ascii=False)
        return f'{json.dumps(k)}:{vstr}'

    if isinstance(id_, dict):
        return '{' + ','.join(_json(k, id_[k]) for k in sorted(id_)) + '}'
    return id_
