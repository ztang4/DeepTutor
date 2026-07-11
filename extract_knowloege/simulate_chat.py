import asyncio  
import json  
import websockets  
  
async def chat_via_websocket(message: str):  
    #uri = "ws://localhost:8003/api/v1/ws"  
    #uri = "ws://192.168.110.167:8003/api/v1/ws"   
    #uri = "ws://192.168.1.18:8003/api/v1/ws"
    uri = "ws://tzqmjh.ddns.net:8003/api/v1/ws"
    async with websockets.connect(uri) as websocket:  
        # 发送 start_turn 消息  
        request = {  
            "type": "start_turn",  
            "content": message,  
            "capability": "chat",  
            "session_id": None,  # None 表示新会话  
            "language": "zh",
            "knowledge_bases": ["test1"]
        }  
        await websocket.send(json.dumps(request))  
          
        # 接收流式响应  
        async for message in websocket:  
            data = json.loads(message)  
            msg_type = data.get("type")  
              
            if msg_type == "content":  
                # 最终内容  
                print(f"回答: {data.get('content')}")  
                #print(data)
                #break  
            elif msg_type == "stream_event":  
                # 流式事件（思考过程、工具调用等）  
                event = data.get("event", {})  
                print(data)
                if event.get("type") == "content":  
                    print(f"流式内容: {event.get('content')}", end="", flush=True)  
            elif msg_type == "error":  
                print(f"错误: {data.get('content')}")  
                break  
            elif msg_type == "stream_end":  
                print("\n流结束")  
                break  
  
# 运行  
asyncio.run(chat_via_websocket("知识库内容有哪些章节"))