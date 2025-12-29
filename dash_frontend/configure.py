import tomllib
import os


class Config:
    def __init__(self, toml_filepath):
        with open(toml_filepath, 'rb') as config_file:
            self.config = tomllib.load(config_file)

    @property
    def jwt_secret_key(self):
        return self.config['config']['jwt_secret_key']

    @property
    def digest_user_auth_filepath(self):
        return self.config['config']['digest_user_auth_filepath']

    @property
    def frontend_bind_host(self):
        return self.config['config']['frontend_bind_host']

    @property
    def frontend_port(self):
        return self.config['config']['frontend_port']

    @property
    def backend_url(self):
        return self.config['config']['backend_url']

    @property
    def is_launch_prod(self):
        return self.config['config']['launch_mode'] == 'prod'

    @property
    def app_title(self):
        return self.config['config']['app_title']

    @property
    def app_version(self):
        return self.config['config']['app_version']

    @property
    def default_show_classification_name(self):
        return 'default'

    @property
    def separator_user(self):
        return ']@['

    @property
    def separator_cls_conv(self):
        return ']|['

    def is_valid_name(self, name):
        return not (self.separator_user in name or self.separator_cls_conv in name)

    def readable_classification_conversation_name(self, classification_conversation_name: str):
        i = conf.split_classification_conversation_name(classification_conversation_name)
        classification_name, conversation_name = i['classification_name'], i['conversation_name']
        user_id, show_classification_name = classification_name.split(self.separator_user)
        if show_classification_name == self.default_show_classification_name:
            return [user_id, conversation_name]
        else:
            return [user_id, show_classification_name, conversation_name]

    def split_classification_conversation_name(self, classification_conversation_name: str):
        i = classification_conversation_name.split(self.separator_cls_conv)
        return dict(classification_name=i[0], conversation_name=i[1])

    def split_classification_name(self, classification_name: str):
        i = classification_name.split(self.separator_user)
        return dict(user_id=i[0], show_classification_name=i[1])

    def is_default_classification(self, classification_conversation_name: str) -> bool:
        i = conf.split_classification_conversation_name(classification_conversation_name)
        classification_name, conversation_name = i['classification_name'], i['conversation_name']
        return self.split_classification_name(classification_name)['show_classification_name'] == self.default_show_classification_name

    @property
    def suffix_llm_store_map_user_id_last_classification_conversation_name(self):  # 存储选择的id
        return 'llm-store-map-user-id-last-classification-conversation-name'

    @property
    def llm_store_classification_names(self):  # 存储所有的分类名
        return 'llm-store-classification-names'

    @property
    def llm_store_classification_conversation_names(self):  # 存储分类对话名
        return 'llm-store-classification-conversation-names'

    @property
    def suffix_llm_dash_history_message_keyword(self):  # 存储dash历史消息，重新打开保留UI
        return 'dash-history-message-store'

    @property
    def suffix_llm_history_message_keyword(self):  # 存储历史消息用于短期记忆
        return 'history-message-store'

    @property
    def suffix_llm_instruction_keyword(self):  # 存储分类指令
        return 'instruction-store'

    @property
    def suffix_llm_model_selected(self):  # 存储已选择的模型配置
        return 'model-selected'

    ##### 日志配置
    @property
    def log_level(self):
        return self.config['config']['log_level']

    @property
    def log_filepath(self):
        t = self.config['config']['frontend_log_filepath']
        os.makedirs(os.path.dirname(t), exist_ok=True)
        return t


conf = Config('../config.toml')
