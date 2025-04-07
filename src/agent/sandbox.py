# python -m src.agent.sandbox

from src.util.file_util import read_yaml
from src.util.chatgpt_util import get_response
from src.util.langgraph_util import CustomChatGPTModel, get_output_with_schema

from typing import Annotated, Literal, List, Dict, Tuple
from typing_extensions import TypedDict

import random

class State(TypedDict):
    current_topic: str
    result: Dict[str, bool] # ex: {"topic_x", True}
 
# サポート関数（ノードの中で使う関数）
def pickup_nonend_senario(state):
    li = []
    for key, item in state["result"].items():
        if item:
            li.append(key)

    return li

# サポート関数（ノードの中で使う関数）
def reformat_dict():
    """
    後で使いやすいように"name"をキーとした辞書にフォーマット
    "name": {
        "name": "xxx"
        "question": "xxx",
        "end_conditions": "xxx",
        "hearing_prompt": "xxx",
        "judge_prompt": "xxx"
    }

    項目が増えてもいいように汎用的に作る。
    """

    senario = read_yaml("./src/agent/senario/senario.yaml")

    result = {}
    for i in senario:
        result[i["name"]] = i

    return result


def init_state(state: State, config:RunnableConfig):
    senario = read_yaml("./src/agent/senario/senario.yaml")

    result = {}
    for i in senario:
        result[i["name"]] = False # 質問への返答結果をFalseで初期化
    state = State()
    state["result"] = result

    state["current_topic"] = None # 現在のトピックをNoneで初期化
    
    return state

def reformat_dict():
    """
    後で使いやすいように"name"をキーとした辞書にフォーマット
    "name": {
        "name": "xxx"
        "question": "xxx",
        "end_conditions": "xxx",
        "hearing_prompt": "xxx",
        "judge_prompt": "xxx"
    }

    項目が増えてもいいように汎用的に作る。
    """

    senario = read_yaml("./src/agent/senario/senario.yaml")

    result = {}
    for i in senario:
        result[i["name"]] = i

    return result

def routing(state: State, config: RunnableConfig) -> Literal["loop", "end_node"]:

  if state["current_topic"] is None:
    nonend_senario = pickup_nonend_senario(state)

    if len(nonend_senario) == 0:
        # 全ての質問が終わっている場合
        return "end_node"
    
    else:
        # まだ質問が残っている場合
        state["current_topic"] = random.choice(nonend_senario)
        return "loop"


  else:
    # カウンターが負けなら次へ
    return "loop"

        

if __name__ == "__main__":
    h = HearinAgent()

    print(h.state["result"])
    print(h.pronmpt_dict.keys())

