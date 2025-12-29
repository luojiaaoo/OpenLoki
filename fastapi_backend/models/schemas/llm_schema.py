from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union, Literal
from models.domains import llm_domain


class ModelSettings(BaseModel):
    sampling: Literal['平衡', '严谨', '创意', '自由']


class CallLLM(BaseModel):
    model_abbr: str = Field(examples=['Qwen3_32B'], description='服务端配置文件的模型缩写')
    user_prompt: str = Field(examples=['写一首关于AI的诗'], description='用户提示词')
    message_history: Optional[List] = Field(default=None, description='历史消息的Json字符串')
    document: Optional[str] = Field(default=None, description='用户上传的文档内容')
    output_enum: llm_domain.LITERAL_OUTPUT_ENUM = Field(examples=[0], description='输出类型')
    instructions: Optional[str] = Field(default=None, description='指令')
    deps: Optional[Dict] = Field(default=None, description='依赖的值')
    toolsets: Optional[List[str]] = Field(default=None, description='工具调用')
    conversation_id: str = Field(examples=['1233'], description='会话ID')
    user_id: str = Field(examples=['luojiaao'], description='用户ID')
    model_settings: ModelSettings = Field(default=ModelSettings(sampling='平衡'), description='大模型参数')
    retries: int = Field(default=3, description='重试次数')
    activate_long_memory: bool = Field(examples=False, description='是否激活长期记忆')
    debounce_by: float = Field(examples=0.1, description='流式返回抖动')
