'''
from model_components.deepseek_model import DeepSeekLLM
deepseek_client = DeepSeekLLM()
llm = deepseek_client.llm
prompt = "你好，DeepSeek！请介绍一下你自己。"
response = llm.invoke(prompt)
print(response.content)
'''

from graph import Graph

graph1 = Graph()

workflow = graph1.get_graph()

print(workflow.compile().invoke({"text": "1"}))