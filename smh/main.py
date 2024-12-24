import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import asyncio
from typing import List
from langchain_community.chat_models import ChatOllama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 정적 파일 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Streaming 콜백 핸들러
class StreamingCallback(StreamingStdOutCallbackHandler):
    def __init__(self, websocket):
        super().__init__()
        self.websocket = websocket
        self.buffer = ""
        
    def on_llm_start(self, *args, **kwargs):
        print("AI가 대화를 시작합니다.")
        
    def on_llm_end(self, *args, **kwargs):
        print("AI가 대화를 종료합니다.")

    async def on_llm_new_token(self, token: str, **kwargs):
        print(f"New token: {token}")
        self.buffer += token
        # 토큰을 즉시 전송하도록 수정
        chunk_message = {
            "type": "assistant",
            "content": token,
            "streaming": True
        }
        try:
            await self.websocket.send_text(json.dumps(chunk_message))
        except Exception as e:
            print(f"Error sending message: {str(e)}")

# # Ollama 모델 초기화
# try:
#     llm = ChatOllama(
#         model="EEVE-Korean-10.8B:latest",
#         callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
#         temperature=0.8,
#         max_tokens=1000
#     )
#     logger.info("Ollama 모델 초기화 성공")
# except Exception as e:
#     logger.error(f"Ollama 모델 초기화 실패: {str(e)}")
#     raise

def create_assistant_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", """당신은 아래의 특성을 가진 도움이 되는 AI 조수입니다:
            1. 사용자의 질문에 직접적으로 답변하기
            2. 필요한 경우에만 부가 설명 제공하기
            3. 모호한 경우 구체적인 질문하기"""),
        ("system", "대화 맥락:\n{chat_history}"),
        ("human", "{input}")
    ])

# 프롬프트 템플릿 생성
assistant_prompt = create_assistant_prompt()

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversation_histories: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.conversation_histories[websocket] = []

    def disconnect(self, websocket: WebSocket):
        if websocket in self.conversation_histories:
            del self.conversation_histories[websocket]
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def get_conversation_history(self, websocket: WebSocket) -> List[dict]:
        return self.conversation_histories.get(websocket, [])

    def add_to_history(self, websocket: WebSocket, message: dict):
        if websocket not in self.conversation_histories:
            self.conversation_histories[websocket] = []
        self.conversation_histories[websocket].append(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(static_dir, "home.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# generate_ai_response 함수에서 streaming_llm 부분만 사용
async def generate_ai_response(prompt: str, history: List[dict], callback_handler) -> str:
    try:
        formatted_messages = [
            SystemMessage(content="""1. 사용자의 질문에 직접적으로 답변하기
                2. 필요한 경우에만 부가 설명 제공하기
                3. 모호한 경우 구체적인 질문하기"""),
        ]
        
        # 대화 이력 추가
        for msg in history[-5:]:  # 최근 5개 메시지만
            if msg["type"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            else:
                formatted_messages.append(AIMessage(content=msg["content"]))
                
        # 현재 질문 추가
        formatted_messages.append(HumanMessage(content=prompt))
        
        streaming_llm = ChatOllama(
            model="EEVE-Korean-10.8B:latest",
            callback_manager=CallbackManager([callback_handler]),
            temperature=0.7,
            num_predict=1000  # max_tokens 대신 num_predict 사용
        )
        
        response = await asyncio.to_thread(
            lambda: streaming_llm.invoke(formatted_messages)
        )
        
        return response.content
        
    except Exception as e:
        logger.error(f"AI 응답 생성 중 오류 발생: {str(e)}")
        raise

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("content", "")

            user_message_dict = {"type": "user", "content": user_message}
            manager.add_to_history(websocket, user_message_dict)

            try:
                history = manager.get_conversation_history(websocket)
                streaming_callback = StreamingCallback(websocket)
                
                # AI 응답 생성
                ai_response = await generate_ai_response(
                    user_message,
                    history,
                    streaming_callback
                )
                
                # 남은 버퍼 내용 전송
                if streaming_callback.buffer:
                    final_chunk = {
                        "type": "assistant",
                        "content": streaming_callback.buffer,
                        "streaming": True
                    }
                    await websocket.send_text(json.dumps(final_chunk))

                # 완료 메시지 전송
                complete_message = {
                    "type": "assistant",
                    "content": "",
                    "streaming": False
                }
                await websocket.send_text(json.dumps(complete_message))

                # 전체 응답을 히스토리에 추가
                ai_message = {
                    "type": "assistant",
                    "content": ai_response
                }
                manager.add_to_history(websocket, ai_message)

            except Exception as e:
                error_message = {
                    "type": "assistant",
                    "content": f"죄송합니다. 오류가 발생했습니다: {str(e)}"
                }
                await manager.send_message(json.dumps(error_message), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)