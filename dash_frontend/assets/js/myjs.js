async function getData(url, with_token=true) {
  try {
    const headers = {};
    // 从sessionStorage获取token
    if (with_token) {
        const token = sessionStorage.getItem('store-bearer-token').replace(/^"(.+)"$/, '$1');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }
    const res = await fetch(
        url, 
        {
            method: 'GET',
            headers: headers
        }
    );
    if (!res.ok) {
      throw new Error(res.status);
    }
    const jsonResponse = await res.json();
    return jsonResponse;
  } catch (error) {
      console.error('Error:', error);
      throw error;
  }
}

async function initializeBackendUrl() {
    console.debug('获取配置信息');
    window.fastapi_backend_url = (await getData("/export_data", with_token=false))["backend_url"]
    console.debug("后端的URL为：" + window.fastapi_backend_url);
}
initializeBackendUrl();

// 发送POST请求
async function postData(url, data, with_token=true) {
    try {
        const headers = {
                'Content-Type': 'application/json',
        };
        // 从sessionStorage获取token
        if (with_token) {
            const token = sessionStorage.getItem('store-bearer-token').replace(/^"(.+)"$/, '$1');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 解析JSON响应
        const jsonResponse = await response.json();
        return jsonResponse;
        
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

let lock_sse = Promise.resolve();

async function changeLocalLargeStorage(type_op, name, new_name='') {
    const db = localforage.createInstance({
        name: 'localforage',
        storeName: 'keyvaluepairs'
    });
    const keys = await db.keys();
    for (const key of keys) {
        json_key = JSON.parse(key)
        if (type_op === 'update_by_prefix'){
            if (json_key.index.startsWith(name)) {
                const value = await db.getItem(key);
                json_key.index = new_name + json_key.index.slice(name.length)
                await db.setItem(JSON.stringify(json_key), value);
                await db.removeItem(key);
            }
        } else if (type_op == 'update_by_match'){
            if (json_key.index === name) {
                const value = await db.getItem(key);
                json_key.index = new_name
                await db.setItem(JSON.stringify(json_key), value);
                await db.removeItem(key);
            }
        } else if (type_op === 'remove_by_prefix'){
            if (json_key.index.startsWith(name)) {
                await db.removeItem(key);
            }
        } else if (type_op === 'remove_by_match'){
            if (json_key.index === name) {
                await db.removeItem(key);
            }
        }
    }
}

async function changeLocalStore(type_op, name, new_name='') {
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        let json_key;
        try {
            json_key = JSON.parse(key);
        } catch (error) {
            continue;
        }
        if (!json_key || !json_key.index) {
            continue;
        }
        if (type_op === 'update_by_prefix'){
            if (json_key.index.startsWith(name)) {
                const value = localStorage.getItem(key);
                const new_json_key = { ...json_key };
                new_json_key.index = new_name +
                    json_key.index.slice(name.length);
                localStorage.setItem(JSON.stringify(new_json_key), value);
                localStorage.removeItem(key);
                // 还有一个timestamp伴生参数
                const key_timestamp = key+'-timestamp'
                const value_timestamp = localStorage.getItem(key_timestamp);
                localStorage.setItem(JSON.stringify(new_json_key)+'-timestamp', value_timestamp);
                localStorage.removeItem(key_timestamp);
            }
        } else if (type_op == 'update_by_match'){
            if (json_key.index===name) {
                const value = localStorage.getItem(key);
                const new_json_key = { ...json_key };
                new_json_key.index = new_name;
                localStorage.setItem(JSON.stringify(new_json_key), value);
                localStorage.removeItem(key);
                // 还有一个timestamp伴生参数
                const key_timestamp = key+'-timestamp'
                const value_timestamp = localStorage.getItem(key_timestamp);
                localStorage.setItem(JSON.stringify(new_json_key)+'-timestamp', value_timestamp);
                localStorage.removeItem(key_timestamp);
            }
        } else if (type_op === 'remove_by_prefix'){
            if (json_key.index.startsWith(name)) {
                localStorage.removeItem(key);
                // 还有一个timestamp伴生参数
                const key_timestamp = key+'-timestamp'
                localStorage.removeItem(key_timestamp);
            }
        } else if (type_op === 'remove_by_match'){
            if (json_key.index===name) {
                localStorage.removeItem(key);
                // 还有一个timestamp伴生参数
                const key_timestamp = key+'-timestamp'
                localStorage.removeItem(key_timestamp);
            }
        }
    }
}

async function _handleAssistantMessageYield(data, history_id, btn_send_id, btn_stop_id) {
    if (data === null) {
        return window.dash_clientside.no_update;
    }
    let json_data = JSON.parse(data)
    console.debug('原始内容', json_data.type)
    let patch = new dash_clientside.Patch;
    if (json_data.type === 'start_thinking') {
        let { id_markdown, component } = await getData(
            url = '/component/assistant_thinking_box',
            with_token = false
        )
        window.last_thinking_id_for_dash = id_markdown
        // console.debug('保存thinking box id', window.last_thinking_id_for_dash)
        return patch.append([], component).build();
    }
    if (json_data.type === 'thinking') {
        let delta = json_data.data
        let markdownStr = dash_component_api.getLayout(window.last_thinking_id_for_dash).props.markdownStr
        // console.debug('获取thinking box id', window.last_thinking_id_for_dash)
        dash_clientside.set_props(window.last_thinking_id_for_dash, { markdownStr: markdownStr + delta })
        return window.dash_clientside.no_update;
    }
    if (json_data.type === 'start_output') {
        let { id_markdown, id_copy_markdown, component } = await getData(
            url = '/component/assistant_output_box',
            with_token = false
        )
        window.last_output_id_for_dash = id_markdown
        window.last_output_id_copy_markdown_for_dash = id_copy_markdown // 用于复制markdown内容
        // console.debug('保存output box id', window.last_id_for_dash)
        return patch.append([], component).build();
    }
    if (json_data.type === 'delta_optput') {
        let delta = json_data.data
        let markdownStr = dash_component_api.getLayout(window.last_output_id_for_dash).props.markdownStr
        let copy_markdownStr = dash_component_api.getLayout(window.last_output_id_copy_markdown_for_dash).props.text
        // console.debug('获取output box id', window.last_id_for_dash)
        dash_clientside.set_props(window.last_output_id_for_dash, { markdownStr: markdownStr + delta })
        dash_clientside.set_props(window.last_output_id_copy_markdown_for_dash, { text: copy_markdownStr + delta })
        return window.dash_clientside.no_update;
    }
    if (json_data.type === 'final_output') {
        let data_ = json_data.data
        dash_clientside.set_props(window.last_output_id_copy_markdown_for_dash, { text: data_ })
        return window.dash_clientside.no_update;
    }
    if (json_data.type === 'history_messages') {
        let json_history = json_data.json
        dash_clientside.set_props(history_id, { data: json_history })
        return window.dash_clientside.no_update;
    }
    if (json_data.type === 'start_tool_call') {
        let { id_markdown, component } = await getData(
            url = '/component/assistant_tool_call_box',
            with_token = false
        )
        window.last_tool_call_id_for_dash = id_markdown
        return patch.append([], component).build();
    }
    if (json_data.type === 'tool_call') {
        let args = json_data.data
        window.tool_type_for_dash = args.tool_name // 保存工具调用类型
        dash_clientside.set_props(window.last_tool_call_id_for_dash, { markdownStr: JSON.stringify(args, null, 4) })
        return window.dash_clientside.no_update;
    }
    if (json_data.type === 'tool_call_return') {
        if (window.tool_type_for_dash === 'serper_search') {
            let { component } = await postData(
                url = '/component/tool_result_serper_search_box',
                data = { 'data': json_data.data },
                with_token = false
            )
            return patch.append([], component).build();
        }
        return window.dash_clientside.no_update;
    }
    if (json_data.type === 'finish') {
        dash_clientside.set_props(btn_send_id, { loading: false })
        dash_clientside.set_props(btn_stop_id, { disabled: true })
        let finish_component = { 'props': { 'id': 'finish', 'children': null }, 'type': 'Fragment', 'namespace': 'feffery_antd_components' }
        return patch.append([], finish_component).build(); // 打一个结束标记，触发存储dash UI持久化的标记，SaveConversationAreaList自动持久化
    }
    console.debug('不能解析：', json_data.type)
    return window.dash_clientside.no_update;
}

// // 使用示例
// const postDataExample = async () => {
//     const data = {
//         name: "John Doe",
//         email: "john@example.com",
//         age: 25
//     };

//     try {
//         const result = await postData('http://localhost:5000/api/data', data);
//         console.debug('Success:', result);
//     } catch (error) {
//         console.error('Request failed:', error);
//     }
// };

// postDataExample();

// function getCookie(name) {
//     const cookies = document.cookie.split(';');
//     for (const cookie of cookies) {
//       const [cookieName, cookieValue] = cookie.trim().split('=');
//       if (cookieName === name) {
//         return decodeURIComponent(cookieValue); // 解码特殊字符（如空格、中文）
//       }
//     }
//     return null; // 未找到返回 null
//   }
  
//   document.addEventListener('DOMContentLoaded', function() {
//     const originalFetch = window.fetch;
//     window.fetch = function(url, config) {
//         // if (url.includes('/_dash-update-component')) {
//             config = config || {};
//             let authToken = null;
//             // 检查授权 cookie
//             authToken = getCookie("access_token");
//             // 如果存在 Token，添加 Header
//             if (authToken !== null && authToken !== '' && authToken != '""') {
//                 authToken = authToken.replace(/"/g, '')
//                 if (!authToken.startsWith('Bearer ')) {
//                     authToken = 'Bearer ' + authToken;
//                 }
//                 config.headers = {
//                     ...(config.headers || {}),
//                     Authorization: authToken // 添加 Authorization 
//                 };
//             }
//         // }
//         return originalFetch(url, config);
//     };
// });