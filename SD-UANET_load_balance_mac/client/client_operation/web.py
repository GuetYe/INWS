# -*- coding: utf-8 -*-
import asyncio
import websockets


SERVER_IP = "10.0.0.1"  # 服务器IP
PORT = 8765             # 端口

async def communicate():
    uri = f"ws://{SERVER_IP}:{PORT}"
    print(f"尝试连接 WebSocket 服务器 {uri} ...")

    try:
        async with websockets.connect(uri) as websocket:
            print("连接成功！可发送消息，输入 'exit' 断开连接")
            while True:
                message = input("输入发送的消息: ")
                if message.lower() == "exit":
                    print("断开连接")
                    break
                
                await websocket.send(message)
                response = await websocket.recv()
                print(f"服务器响应: {response}")

    except Exception as e:
        print(f"连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(communicate())
