from fastapi import FastAPI, Request
import subprocess
import json

app = FastAPI()

# MCP Server 的配置
MCP_SERVER_COMMAND = ["uvx", "mcp-server-fetch", "--ignore-robots-txt"]

@app.post("/api/fetch")
async def fetch(request: Request):
    # 从客户端接收请求数据
    request_data = await request.json()

    # 调用 MCP Server
    process = subprocess.Popen(
        MCP_SERVER_COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # 将请求数据发送到 MCP Server
    stdout, stderr = process.communicate(json.dumps(request_data))

    # 检查 MCP Server 的输出
    if process.returncode != 0:
        return {"error": stderr}

    # 返回 MCP Server 的响应
    response_data = json.loads(stdout)
    return response_data
