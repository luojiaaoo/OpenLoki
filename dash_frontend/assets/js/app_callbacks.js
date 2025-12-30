window.dash_clientside = Object.assign({}, window.dash_clientside, {
    app_clientside: {
        collapse_menu: (nClicks, collapsed) => {
            if (collapsed) {
                return [!collapsed, 'antd-menu-fold', { 'display': 'block' }];
            } else {
                return [!collapsed, 'antd-menu-unfold', { 'display': 'None' }];
            }
        },
        RenameClassificationName: async (nClicks, target_name, op_id) => {
            const original_name = op_id.index
            // 预处理
            target_name = target_name.trim()
            if (target_name === '') {
                return window.dash_clientside.no_update;
            }
            let classification_names = dash_component_api.getLayout('llm-store-classification-names').props.data;
            const userId = dash_component_api.getLayout('store-user-id').props.data;
            const separator_user = dash_component_api.getLayout('store-separator-user').props.data;
            const separator_cls_conv = dash_component_api.getLayout('store-separator-cls-conv').props.data;
            target_name = userId + separator_user + target_name // 传过来的值不带，用户名，需要在前面加上用户名
            if (classification_names.includes(target_name)) {
                return window.dash_clientside.no_update;
            }
            console.debug('更新分类名', original_name, target_name)
            original_name_sep = original_name + separator_cls_conv
            target_name_sep = target_name + separator_cls_conv
            // suffix_llm_store_map_user_id_last_classification_conversation_name
            let map_user_id_last_classification_conversation_name = dash_component_api.getLayout('llm-store-map-user-id-last-classification-conversation-name').props.data;
            const currentName = map_user_id_last_classification_conversation_name?.[userId];
            if (currentName?.startsWith(original_name_sep)) {
                const newName = target_name_sep + currentName.slice(original_name_sep.length);
                map_user_id_last_classification_conversation_name[userId] = newName;
                dash_clientside.set_props('llm-store-map-user-id-last-classification-conversation-name', {
                    data: map_user_id_last_classification_conversation_name
                });
            }
            // llm_store_classification_names
            dash_clientside.set_props('llm-store-classification-names', {
                data: classification_names.map(item =>
                    item === original_name ? target_name : item
                )
            });
            // llm_store_classification_conversation_names
            let classification_conversation_names = dash_component_api.getLayout('llm-store-classification-conversation-names').props.data;
            if (classification_conversation_names) {
                dash_clientside.set_props('llm-store-classification-conversation-names', {
                    data: classification_conversation_names.map(item => item.split(original_name_sep).join(target_name_sep))
                });
            }
            // suffix_llm_dash_history_message_keyword  suffix_llm_history_message_keyword
            await changeLocalLargeStorage('update_by_prefix', original_name_sep, target_name_sep)
            // suffix_llm_instruction_keyword
            await changeLocalLargeStorage('update_by_match', original_name, target_name)
            // suffix_llm_model_selected
            await changeLocalStore('update_by_prefix', original_name_sep, target_name_sep)
            dash_clientside.set_props('flush-main-menu-menu-items', { data: Date.now().toString() });
            return false;
        },
        RemoveClassificationName: async (confirmCounts, op_id) => {
            classification_name = op_id.index
            const last_classification_name = dash_component_api.getLayout('store-last-classification-name').props.data;
            const userId = dash_component_api.getLayout('store-user-id').props.data;
            const separator_cls_conv = dash_component_api.getLayout('store-separator-cls-conv').props.data;
            classification_name_sep = classification_name + separator_cls_conv
            // suffix_llm_store_map_user_id_last_classification_conversation_name
            let map_user_id_last_classification_conversation_name = dash_component_api.getLayout('llm-store-map-user-id-last-classification-conversation-name').props.data;
            const currentName = map_user_id_last_classification_conversation_name?.[userId];
            if (currentName?.startsWith(classification_name_sep)) {
                delete map_user_id_last_classification_conversation_name[userId];
                dash_clientside.set_props('llm-store-map-user-id-last-classification-conversation-name', {
                    data: map_user_id_last_classification_conversation_name
                });
            }
            // llm_store_classification_names
            let classification_names = dash_component_api.getLayout('llm-store-classification-names').props.data;
            dash_clientside.set_props('llm-store-classification-names', {
                data: classification_names.filter(item => item !== classification_name)
            });
            // llm_store_classification_conversation_names
            let classification_conversation_names = dash_component_api.getLayout('llm-store-classification-conversation-names').props.data;
            if (classification_conversation_names) {
                dash_clientside.set_props('llm-store-classification-conversation-names', {
                    data: classification_conversation_names.filter(item => !item.startsWith(classification_name_sep))
                });
            }
            // suffix_llm_dash_history_message_keyword  suffix_llm_history_message_keyword
            await changeLocalLargeStorage('remove_by_prefix', classification_name_sep)
            // suffix_llm_instruction_keyword
            await changeLocalLargeStorage('remove_by_match', classification_name)
            // suffix_llm_model_selected
            await changeLocalStore('remove_by_prefix', classification_name_sep)
            dash_clientside.set_props('flush-main-menu-menu-items', { data: Date.now().toString() });
            if (last_classification_name === classification_name) {
                dash_clientside.set_props('init-container-conversation', { data: Date.now().toString() });
            }
            return false
        },
        renameClassificationConversationName: async (nClicks, target_name, op_id) => {
            const original_name = op_id.index
            target_name = target_name.trim()
            if (target_name === '') {
                return window.dash_clientside.no_update;
            }
            const userId = dash_component_api.getLayout('store-user-id').props.data;
            const separator_cls_conv = dash_component_api.getLayout('store-separator-cls-conv').props.data;
            const last_classification_name = dash_component_api.getLayout('store-last-classification-name').props.data;
            target_name = last_classification_name + separator_cls_conv + target_name
            let classification_conversation_names = dash_component_api.getLayout('llm-store-classification-conversation-names').props.data;
            if (classification_conversation_names.includes(target_name)) { // 已经有这个名字了
                return window.dash_clientside.no_update;
            }
            // suffix_llm_store_map_user_id_last_classification_conversation_name
            let map_user_id_last_classification_conversation_name = dash_component_api.getLayout('llm-store-map-user-id-last-classification-conversation-name').props.data;
            map_user_id_last_classification_conversation_name[userId] = target_name
            dash_clientside.set_props('llm-store-map-user-id-last-classification-conversation-name', {
                data: map_user_id_last_classification_conversation_name
            });
            // llm_store_classification_conversation_names
            dash_clientside.set_props('llm-store-classification-conversation-names', {
                data: classification_conversation_names.map(item => item === original_name ? target_name : item)
            });
            // suffix_llm_dash_history_message_keyword  suffix_llm_history_message_keyword
            await changeLocalLargeStorage('update_by_match', original_name, target_name)
            // suffix_llm_model_selected
            await changeLocalStore('update_by_match', original_name, target_name)
            dash_clientside.set_props('flush-main-menu-menu-items', { data: Date.now().toString() });
            dash_clientside.set_props('init-container-conversation', { data: Date.now().toString() });
            return false
        },
        removeClassificationConversation: async (confirmCounts, op_id) => {
            const classification_conversation_name = op_id.index
            const userId = dash_component_api.getLayout('store-user-id').props.data;
            const separator_cls_conv = dash_component_api.getLayout('store-separator-cls-conv').props.data;
            const last_classification_name = dash_component_api.getLayout('store-last-classification-name').props.data;
            // suffix_llm_store_map_user_id_last_classification_conversation_name
            let map_user_id_last_classification_conversation_name = dash_component_api.getLayout('llm-store-map-user-id-last-classification-conversation-name').props.data;
            delete map_user_id_last_classification_conversation_name[userId];
            dash_clientside.set_props('llm-store-map-user-id-last-classification-conversation-name', {
                data: map_user_id_last_classification_conversation_name
            });
            // llm_store_classification_conversation_names
            let classification_conversation_names = dash_component_api.getLayout('llm-store-classification-conversation-names').props.data;
            dash_clientside.set_props('llm-store-classification-conversation-names', {
                data: classification_conversation_names.filter(item => item !== classification_conversation_name)
            });
            // suffix_llm_dash_history_message_keyword  suffix_llm_history_message_keyword
            await changeLocalLargeStorage('remove_by_match', classification_conversation_name)
            // suffix_llm_model_selected
            await changeLocalStore('remove_by_match', classification_conversation_name)
            dash_clientside.set_props('flush-main-menu-menu-items', { data: Date.now().toString() });
            dash_clientside.set_props('init-container-conversation', { data: Date.now().toString() });
            return false
        },
        changeClassificationNameOfClassificationConversation: async (nClicks, new_classification_name, op_id) => {
            const original_name = op_id.index
            const userId = dash_component_api.getLayout('store-user-id').props.data;
            const separator_cls_conv = dash_component_api.getLayout('store-separator-cls-conv').props.data;
            let parts_temp = original_name.split(separator_cls_conv)
            target_name = new_classification_name + separator_cls_conv + parts_temp[parts_temp.length - 1]
            let classification_conversation_names = dash_component_api.getLayout('llm-store-classification-conversation-names').props.data;
            if (classification_conversation_names.includes(target_name)) { // 已经有这个名字了
                return window.dash_clientside.no_update;
            }
            // suffix_llm_store_map_user_id_last_classification_conversation_name
            let map_user_id_last_classification_conversation_name = dash_component_api.getLayout('llm-store-map-user-id-last-classification-conversation-name').props.data;
            map_user_id_last_classification_conversation_name[userId] = target_name
            dash_clientside.set_props('llm-store-map-user-id-last-classification-conversation-name', {
                data: map_user_id_last_classification_conversation_name
            });
            // llm_store_classification_conversation_names
            dash_clientside.set_props('llm-store-classification-conversation-names', {
                data: classification_conversation_names.map(item => item === original_name ? target_name : item)
            });
            // suffix_llm_dash_history_message_keyword  suffix_llm_history_message_keyword
            await changeLocalLargeStorage('update_by_match', original_name, target_name)
            // suffix_llm_model_selected
            await changeLocalStore('update_by_match', original_name, target_name)
            dash_clientside.set_props('flush-main-menu-menu-items', { data: Date.now().toString() });
            dash_clientside.set_props('init-container-conversation', { data: Date.now().toString() });
            return false
        },
        init_llm_select_options: async (style_options, value) => {
            try {
                value = value || { selected_model: null, selected_style: null };
                console.debug("之前保存的配置:", value);
                let selected_model = value.selected_model;
                let selected_style = value.selected_style;
                console.debug("之前保存的模型名:", selected_model);
                console.debug("之前保存的风格:", selected_style);
                const llm_names = await getData(window.fastapi_backend_url + '/llm/llm-names');
                console.debug("已配置的模型名:", llm_names);
                const optionsArray = llm_names.map(name => ({ label: name, value: name }));
                selected_model = selected_model || (llm_names.length > 0 ? llm_names[0] : null);
                console.debug('模型默认值:', selected_model);
                selected_style = selected_style || (style_options.length > 0 ? style_options[0]['value'] : null);
                console.debug('模型默认风格:', selected_style);
                return [optionsArray, selected_model, selected_style, { selected_model: selected_model, selected_style: selected_style }];
            } catch (err) {
                console.error("获取模型名失败:", err);
                throw err;
            }
        },
        recoverHistoryConversationAreaList: (_, data) => {
            if (data === undefined) { // 阻止初始回调，或者没有历史记录
                return window.dash_clientside.no_update;
            }
            return data
        },
        handleUserNewMessageEdit: (_, focusing, value) => {
            // 不在聚焦状态下，不进行任何更新
            if (!focusing) {
                return window.dash_clientside.no_update;
            }
            // 换行逻辑处理
            if (window.dash_clientside.callback_context.triggered_id.type === 'ctrl-enter-keypress') {
                return `${value}\n` // 为value追加换行符
            }
        },
        handleUserNewMessageSend: async (pressedCounts, nClicks, input_text, focusing, selected_model, selected_style, activate_long_memory, toolsets, history_message, loading) => {
            // 按按钮，但是是初始化回调触发的，忽略
            if (dash_clientside.callback_context.triggered_id.type === 'btn-send-input-text' && nClicks === undefined) {
                return window.dash_clientside.no_update;
            }
            // 不在聚焦状态下，按enter也没用
            if (dash_clientside.callback_context.triggered_id.type === 'enter-keypress' && !focusing) {
                return window.dash_clientside.no_update;
            }
            // loading是否正在上一步对话发生中
            if (loading) {
                return window.dash_clientside.no_update;
            }
            let toolsets_ = toolsets !== undefined ? toolsets : null
            let user_id = dash_component_api.getLayout('store-user-id').props.data
            let last_classification_conversation_name = dash_component_api.getLayout('llm-store-map-user-id-last-classification-conversation-name').props.data[user_id];
            let last_classification_name = dash_component_api.getLayout('store-last-classification-name').props.data
            let now_user_id = dash_component_api.getLayout('store-user-id').props.data
            let instructions_id = { 'type': 'instruction-store', 'index': last_classification_name }
            let instructions_comp = dash_component_api.getLayout(instructions_id)
            if (instructions_comp === undefined) {
                console.error(`找不到${last_classification_name}，对应的指令`)
            }
            let instructions = instructions_comp.props.data !== undefined ? instructions_comp.props.data : null;
            let history_message_ = history_message !== undefined ? history_message : null;
            let data = {
                'bearer_token': dash_component_api.getLayout('store-bearer-token').props.data,
                'model_abbr': selected_model,
                'user_prompt': input_text,
                'message_history': history_message_,
                'document': null,
                'output_enum': 0,
                'instructions': instructions,
                'deps': null,
                'toolsets': toolsets_,
                'conversation_id': last_classification_conversation_name,
                'user_id': now_user_id,
                'model_settings': {
                    'sampling': selected_style
                },
                'activate_long_memory': activate_long_memory
            }
            console.debug('请求参数', data)
            let { sse, component } = await postData(
                url = '/component/user_box',
                data = data,
                with_token = false
            )
            let patch = new dash_clientside.Patch;
            return ['', patch.append([], component).build(), sse, true, false]
        },
        SaveConversationAreaList: (conversation_area_list) => {
            if (conversation_area_list.length === 0) { // fix: 搞不懂，popup_conversation_modal回调把currentKey还原的时候，触发了初始回调，按理应该拦截的
                return window.dash_clientside.no_update;
            }
            let flag_finish = conversation_area_list[conversation_area_list.length - 1]
            if (flag_finish.props.id === 'finish') {
                console.debug('触发dashUI历史记录保存')
                return conversation_area_list
            }
            return window.dash_clientside.no_update;
        },
        handleAssistantMessageYield: (data, history_id, btn_send_id, btn_stop_id) => {
            // 将新任务加入队列
            if (data === null) {
                return window.dash_clientside.no_update;
            }
            const json_data = JSON.parse(data);
            const task = lock_sse
                .then(() =>
                    _handleAssistantMessageYield(json_data, history_id, btn_send_id, btn_stop_id)
                )
            lock_sse = task.catch(err => {
                console.error('SSE任务失败:', err);
                // 即使失败，也要继续执行后续任务
            });

            // 返回当前任务的Promise，这样调用者可以await获取结果
            return task;
        },
        handleStopAssistantMessage: (nClicks) => {
            return ['close', false, true]
        }
    }
});