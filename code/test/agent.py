from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware


from model.llm import llm
from utils.get_time import get_current_time
from utils.get_wether import get_city_weather


checkpointer = InMemorySaver()

config = {
    "configurable": {
        "thread_id": "thread_1"
    }
}
SummarizationMiddleware = SummarizationMiddleware(
            model = llm,                    # 用于 summary 的模型
            trigger = ("tokens", 4000),     # 当历史 token >= 4000 时触发 summarize
            keep = ("messages", 400),        # 摘要后保留最近 20 条消息 + summary
        )

agent = create_agent(
    model = llm,
    tools = [get_current_time,get_city_weather],
    system_prompt = "你是一个有帮助的助手。",
    checkpointer=checkpointer,
    middleware=[SummarizationMiddleware]
)


response = agent.invoke({
    "messages": [
        {"role": "user", "content": "请问北京市现在的时间和天气怎么样？"}
    ]},
    config
)

#print (response)
#print (response["messages"][-1]["content"])
final_answer = response["messages"][-1].content
print("北京查询的回答：")
print(final_answer)


response1 = agent.invoke({
    "messages": [
        {"role": "user", "content": "长沙呢？"}
    ]},
    config
)

#print (response1)

final_answer1 = response1["messages"][-1].content
print("长沙查询的回答：")
print(final_answer1)
