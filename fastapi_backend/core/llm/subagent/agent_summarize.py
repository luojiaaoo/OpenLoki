from pydantic_ai import ModelSettings
from core.configure import conf
from core.llm import prompt
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


async def summarize(content):
    agent = Agent(
        OpenAIChatModel(
            conf.summarize_model_name,
            provider=OpenAIProvider(
                base_url=conf.summarize_url,
                api_key=conf.summarize_api_key,
            ),
            settings=ModelSettings(top_p=0.4),
        ),
        instructions=prompt.prompt_summarize,
        output_type=str,
    )
    result = await agent.run(f'# 需要总结的内容{content}\n\n # 如果要总结以上的文字，找哪些角色比较合适？他们总结的内容会是什么样？')
    return result.output
