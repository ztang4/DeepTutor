import asyncio  
import json  
import websockets  
  
class DeepTutorWSClient:  
    def __init__(self, uri="ws://localhost:8003/api/v1/ws"):  
        self.uri = uri  
        self.session_id = None  
      
    async def send_message(self, content: str, capability="chat"):  
        async with websockets.connect(self.uri) as websocket:  
            request = {  
                "type": "start_turn",  
                "content": content,  
                "capability": capability,  
                "session_id": self.session_id  
            }  
            await websocket.send(json.dumps(request))  
              
            full_content = ""  
            async for message in websocket:  
                data = json.loads(message)  
                msg_type = data.get("type")  
                  
                if msg_type == "content":  
                    # 最终完整内容  
                    full_content = data.get("content", "")  
                    self.session_id = data.get("session_id")  
                    print(f"\n完整回答: {full_content}")  
                    return full_content  
                elif msg_type == "stream_event":  
                    # 流式事件  
                    event = data.get("event", {})  
                    if event.get("type") == "content":  
                        content_piece = event.get("content", "")  
                        print(content_piece, end="", flush=True)  
                        full_content += content_piece  
                elif msg_type == "error":  
                    print(f"\n错误: {data.get('content')}")  
                    return None  
                elif msg_type == "stream_end":  
                    print("\n--- 流结束 ---")  
                    return full_content  
  
async def main():  
    client = DeepTutorWSClient()  
      
    # 第一轮对话  
    print("第一轮对话:")  
    result1 = await client.send_message("什么是机器学习？")  
    print(f"会话 ID: {client.session_id}")  
      
    # 第二轮对话（使用同一会话）  
    if client.session_id:  
        print("\n第二轮对话:")  
        result2 = await client.send_message("给我一个简单例子")  
  
asyncio.run(main())