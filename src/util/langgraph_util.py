# python -m src.util.langgraph_util
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from typing import List
from src.util.chatgpt_util import get_response


# LangChain 互換のクラス
class CustomChatGPTModel(BaseChatModel):
    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "custom-chatgpt"

    def _convert_messages_to_openai_format(self, messages: List[BaseMessage]) -> List[dict]:
        openai_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
            openai_messages.append({
                "role": role,
                "content": message.content
            })
        return openai_messages

    from langchain_core.outputs import ChatGeneration, ChatResult

    def _generate(self, messages: List[BaseMessage], stop: List[str] = None) -> ChatResult:
        openai_messages = self._convert_messages_to_openai_format(messages)
        response = get_response(openai_messages)
        content = response.choices[0].message.content
        ai_message = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=ai_message)])


def get_output_with_schema(llm, name, description, template, input_variables, input_values):
    """
      プロンプトに対する応答を特定のjson formatで受け取る。
    """

    # ここでスキーマを定義。
    response_schemas = [
        ResponseSchema(
            name=name,
            description=description
        )
    ]

    # スキーマを元に、「出力はJSON形式でお願いします」的なプロンプトを考えてくれる。
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=template,
        input_variables=input_variables,
        # フォーマット指示をプロンプトへ差し込む
        partial_variables={"format_instructions": format_instructions} #かならず元promptに{format_instructions}を入れること！
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt
    )


    dic = {}
    for name, val in zip(input_variables, input_values):
      dic[name] = val

    raw_output = chain.invoke(dic)["text"]

    # 事前定義したスキーマを元に、json⇒辞書の変換を勝手にやってくれる。
    parsed_output = output_parser.parse(raw_output)

    return parsed_output


if __name__ == "__main__":
    llm = CustomChatGPTModel()

    # テスト用のプロンプト
    name = "test"
    description = "test"
    template = "{format_instructions}\nあなたは{role}です。あなたの名前は{user_name}です。"
    input_variables = ["role", "user_name"]
    input_values = ["assistant", "test_user"]

    # プロンプトを実行して、応答を取得
    response = get_output_with_schema(llm, name, description, template, input_variables, input_values)
    print(response)