import tomllib
import os


class Config:
    def __init__(self, toml_filepath):
        with open(toml_filepath, 'rb') as config_file:
            self.config = tomllib.load(config_file)

    @property
    def jwt_secret_key(self):
        return self.config['config']['jwt_secret_key']

    # 获取大模型配置
    def llm_get_model_name(self, model_abbr):
        t = self.config['llm'][model_abbr]
        return dict(
            model_name=t['model_name'],
            model_url=t['model_url'],
            api_key=t['api_key'],
            max_tokens=t['max_tokens'],
            context_length=t['context_length'],
        )

    @property
    def is_launch_prod(self):
        return self.config['config']['launch_mode'] == 'prod'

    @property
    def backend_bind_host(self):
        return self.config['config']['backend_bind_host']

    @property
    def backend_port(self):
        return self.config['config']['backend_port']

    ##### 日志配置
    @property
    def log_level(self):
        return self.config['config']['log_level']

    @property
    def log_filepath(self):
        t = self.config['config']['backend_log_filepath']
        os.makedirs(os.path.dirname(t), exist_ok=True)
        return t

    # 上传路径配置
    @property
    def upload_dirpath(self):
        t = self.config['config']['backend_upload_dirpath']
        os.makedirs(t, exist_ok=True)
        return t

    @property
    def upload_url_prefix(self):
        return self.config['config']['backend_upload_url_prefix']

    @property
    def llm_names(self):
        return list(self.config['llm'].keys())

    ##### 子智能体
    @property
    def summarize_model_name(self):
        return self.config['subagent']['summarize']['summarize_model_name']

    @property
    def summarize_api_key(self):
        return self.config['subagent']['summarize']['summarize_api_key']

    @property
    def summarize_url(self):
        return self.config['subagent']['summarize']['summarize_url']

    ##### 短期记忆配置
    @property
    def short_memory_len_message_history(self):
        return self.config['short_memory']['len_message_history']

    ##### 长期记忆配置
    @property
    def long_memory_memos_api_key(self):
        return self.config['long_memory']['memos_api_key']

    @property
    def long_memory_memos_url(self):
        return self.config['long_memory']['memos_url']

    @property
    def long_memory_memos_timeout(self):
        return self.config['long_memory']['memos_timeout']

    #### MCP配置
    @property
    def mcp_split_string(self):
        return self.config['mcp']['split_string']

    @property
    def mcp_search_serper_api_key(self):
        return self.config['mcp']['search']['serper_api_key']

    @property
    def mcp_search_serper_timeout(self):
        return self.config['mcp']['search']['serper_timeout']


conf = Config('../config.toml')
