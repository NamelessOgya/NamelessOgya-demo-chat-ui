
参考[https://github.com/yamato0811/streamlit-langgraph-HITL-copy-generator]のコードを参考にしつつ理解  
  
# グラフcompile時
checkpointerとinterrupt_beforeを渡す。  
  
## checkpointer  
処理が中断しても、あとから復元できるようになる。  
```
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

```  
ref: [Langgraphに入門する](https://zenn.dev/zerebom/scraps/50f099327d26d7)    
  
## interrupt_before  
指定したノードの実行時にグラフを一時停止する。  
```
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["sensitive_tools"]
)

```
ref: [LangGraphのexamplesからエージェントの作り方を学ぶ](https://zenn.dev/zenkigen_tech/articles/536801e61d0689)