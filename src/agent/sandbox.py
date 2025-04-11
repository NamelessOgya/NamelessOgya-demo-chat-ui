# python -m src.agent.sandbox

from src.util.file_util import read_yaml
from src.util.chatgpt_util import get_response
from src.util.langgraph_util import CustomChatGPTModel, get_output_with_schema

from typing import Annotated, Literal, List, Dict, Tuple
from typing_extensions import TypedDict

from langchain_core.runnables import RunnableConfig

import random
from langgraph.graph import StateGraph



class State(TypedDict):
    user_input: str
    current_node: str
    current_topic: str
    result: Dict[str, str] # ex: {"topic_x", "aaaaa"}
    history: str
    agent_reply: str

 
# サポート関数（ノードの中で使う関数）
def make_nonend_senario_list(state):
    """
    現在のトピックがNoneの場合、質問が終わっていないものをランダムに選ぶ
    """
    li = []
    for key, item in state["result"].items():
        if item is None:
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
        result[i["name"]] = None # 質問への返答結果をFalseで初期化
    
    # state = State()
    state["current_node"] = "init_state" 
    state["result"] = result

    state["current_topic"] = None # 現在のトピックをNoneで初期化

    state["history"] = "" # ヒアリング履歴を空で初期化
    
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

def set_topic(state: State, config: RunnableConfig):
    state["current_node"] = "set_topic"

    # まだ終わってないシナリオを名を取得
    nonend_senario = make_nonend_senario_list(state)

    if len(nonend_senario) == 0:
        return state # すべての質問が終わっているなら次へ

    # 話題が定義されていない（初回など）/ 話題が終了している場合⇒ 新たな話題を定義
    if state["current_topic"] is None or state["result"][state["current_topic"]]:
        state["current_topic"] = random.choice(nonend_senario)

        return state
    
    else:
        return state

def routing(state: State, config: RunnableConfig) -> Literal["generate_question", "end_node"]:
    # まだ終わってないシナリオを名を取得
    nonend_senario = make_nonend_senario_list(state)

    if len(nonend_senario) == 0:
        # 全ての質問が終わっている場合
        return "end_node"
    
    else:
        # まだ質問が残っている場合
        
        return "generate_question"


def generate_question(state: State, config: RunnableConfig):
    """
    ユーザに質問するための関数
    """
    state["current_node"] = "generate_question"
    llm = CustomChatGPTModel()

    topic = state["current_topic"]
    scenario = reformat_dict()
    prompt = scenario[topic]["hearing_prompt"]

    history = state["history"]
    end_conditions = scenario[topic]["end_conditions"]

    res = get_output_with_schema(
        llm = llm,
        name = "reply_to_user",
        description = "reply text to user",
        template = prompt,
        input_variables = ["role", "history", "end_conditions"],
        input_values = [scenario[topic]["description"], history, end_conditions]

    )["reply_to_user"]

    print(res) # UI表出

    # historyに追加  
    state["history"] += f"agent: {res}\n"
    # print("debug: generate_question")
    # print(state["result"])

    state["agent_reply"] = res # エージェントの発話を保存

    return state

def user_action(state: State, config: RunnableConfig):
    """
    Streamlit 実行時は「state["user_input"] に入ってきたテキスト」を
    history に追記する。
    """
    state["current_node"] = "user_action"

    # Streamlitからの入力は state["user_input"] に入れている想定
    user_input = state.get("user_input", "")
    print("=== state in user_action ===")
    print(state)

    if user_input:
        # historyに追加
        state["history"] += f"human: {user_input}\n"
        print("[user_action] 受け取ったユーザー入力:", user_input)

        # 使い終わったらクリアしておく（何度も追記されないように）
        state["user_input"] = ""

    else:
        print("[user_action] ユーザー入力は空でした。")

    # ※ コンソール実行 (__main__) 時には別途 input() を受け取ってもOKですが
    #   今回はStreamlitのみを想定するなら不要です。
    if __name__ == "__main__":
        pass

    return state


def judge_result(state: State, config: RunnableConfig):
    """
        対話履歴からヒアリングの終了条件を判断する。
    """
    print("====in judge node!!!===")
    print(state)
    state["current_node"] = "judge_result"
    
    llm = CustomChatGPTModel()

    topic = state["current_topic"]
    scenario = reformat_dict()
    prompt = scenario[topic]["judge_prompt"]

    question = scenario[topic]["question"]
    history = state["history"]
    end_conditions = scenario[topic]["end_conditions"]

    res = get_output_with_schema(
        llm = llm,
        name = "judge_result",
        description = "終了条件の判定",
        template = prompt,
        input_variables = ["history", "end_conditions", "question"],
        input_values = [history, end_conditions, question]

    )["judge_result"]


    print(f"judge result: {res}")


    if res != "未達":
        state["result"][topic] = res
        
        

    # print("debug: judge_result")
    # print(state["result"])
    return state

def end_node(state: State, config: RunnableConfig):
    state["current_node"] = "end_node"
    print("ヒアリング完了！")

    print("==============")
    print(state["result"])

    # print("debug: end_node")
    # print(state["result"])
    return state

def generate_graph():
# ノードを定義していく
    graph_builder = StateGraph(State)
    graph_builder.add_node("init_state", init_state)
    graph_builder.add_node("set_topic", set_topic)
    # graph_builder.add_node("routing", routing)
    graph_builder.add_node("generate_question", generate_question)
    graph_builder.add_node("user_action", user_action)
    graph_builder.add_node("judge_result", judge_result)
    graph_builder.add_node("end_node", end_node)

    graph_builder.set_entry_point("init_state")

    graph_builder.add_edge("init_state", "set_topic")
    # エッジを設置。遷移図を定義
    graph_builder.add_conditional_edges(
        "set_topic",# 遷移元
        routing
    )
    
    graph_builder.add_edge("generate_question", "user_action")
    graph_builder.add_edge("user_action", "judge_result")
    graph_builder.add_edge("judge_result", "set_topic")
    

    graph_builder.set_finish_point("end_node")

    # Graphをコンパイル
    graph = graph_builder.compile()
    # Graphの実行(引数にはStateの初期値を渡す)

    return graph

if __name__ == "__main__":
    graph = generate_graph()
    state = graph.invoke(
        {}, 
        debug=True
    )