import asyncio
import json
import websockets
import csv
import os
import time

WS_URL = "ws://localhost:3782/api/v1/ws"
TOTAL_TIMEOUT_SECONDS = 600

CSV_FILE = "./data/level4-result_tree.csv"
OUTPUT_DIR = "./data/chat_results"


def read_csv_from_chapter2(csv_path):
    all_rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            parts = [p for p in row if p.strip()]
            if parts:
                level1 = parts[0]
                if level1.startswith("第"):
                    question_text = " > ".join(parts)
                    all_rows.append(question_text)

    return all_rows


def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    filename = filename.strip()
    if len(filename) > 200:
        filename = filename[:200]
    return filename


async def chat_via_websocket(message: str):
    full_response = ""

    async with websockets.connect(WS_URL) as websocket:
        request = {
            "type": "start_turn",
            "content": message,
            "capability": "chat",
            "session_id": None,
            "language": "zh",
            "knowledge_bases": ["知识清单"],
            "llmSelection": {
                "profile_id": "llm-profile-default",
                "model_id": "llm-model-1783146188844"
            }
        }
        await websocket.send(json.dumps(request))

        async for msg in websocket:
            data = json.loads(msg)
            msg_type = data.get("type")

            if msg_type == "content":
                content = data.get("content", "")
                full_response += content
                print(content, end="", flush=True)

            elif msg_type == "stream_event":
                event = data.get("event", {})
                if event.get("type") == "content":
                    content = event.get("content", "")
                    full_response += content
                    print(content, end="", flush=True)

            elif msg_type == "error":
                print(f"\n[错误] {data.get('content', '未知错误')}")
                break

            elif msg_type == "stream_end":
                print("\n流结束")
                break
            elif msg_type == "done":
                print("\n对话完成")
                break

    return full_response


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    questions = read_csv_from_chapter2(CSV_FILE)
    print(f"找到 {len(questions)} 条问题")

    for idx, question_text in enumerate(questions, 1):
        full_question = f"查阅知识库，输出{question_text} 的解法与考法以表格形式显示，每个考法给一个简短的例题，例题里内容紧贴考法和解法，不要综合性的题目，整体篇幅不超过3000字。请直接输出解法与考法内容，不要在开头和结尾添加任何引导性语句、继续提问的邀请或附加请求。"
        filename = sanitize_filename(question_text)
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.md")

        if os.path.exists(output_path):
            print(f"\n[{idx}/{len(questions)}] 跳过已存在: {question_text[:50]}...")
            continue

        print(f"\n{'='*60}")
        print(f"[{idx}/{len(questions)}] 问题: {full_question}")
        print(f"{'='*60}")

        start_time = time.time()
        response = ""

        try:
            response = await asyncio.wait_for(chat_via_websocket(full_question), timeout=TOTAL_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            print("\n[总超时] 对话超过10分钟，强制结束")

        end_time = time.time()
        elapsed = end_time - start_time

        if response:
            response = response.strip()
            lines = response.split('\n')
            if lines:
                last_line = lines[-1].strip()
                keywords = ['保存到笔记本', '转成', 'HTML', '请告诉我', '需要我', '如需我', '方便复习', '如需进一步', '可以继续提问', '换元法', '配凑法']
                if any(kw in last_line for kw in keywords):
                    response = '\n'.join(lines[:-1]).strip()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {question_text}\n\n")
            f.write(response)

        print(f"\n结果已保存: {output_path} | 耗时: {elapsed:.2f}秒")

        await asyncio.sleep(1)

    print("\n批量对话完成！")


if __name__ == "__main__":
    asyncio.run(main())