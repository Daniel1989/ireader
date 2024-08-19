import subprocess
import os
model_name = "Qwen/Qwen2-1.5B-Instruct-AWQ"

api_server_command = [
    "python",
    "-m",
    "vllm.entrypoints.openai.api_server",
    "--model",
    model_name,
    "--dtype",
    "float16",
    "--api-key",
    "",
    "--tensor-parallel-size",
    "1",
    "--trust-remote-code",
    "--gpu-memory-utilization",
    "0.9",
    "--disable-log-requests",
    "--disable-log-stats",
    "--port",
    "8000",
]
api_process = subprocess.Popen(
    api_server_command, text=True)

print("开始启动 api 服务")
chainlit_ui_process = subprocess.Popen(
    ['python', 'manage.py', 'runserver', '0.0.0.0:7860'])
playwright_download = subprocess.Popen(
    ['playwright', 'install'])
task_process = subprocess.Popen(
    ['python', 'task.py'])

try:
    api_process.wait()
    chainlit_ui_process.wait()
    playwright_download.wait()
    task_process.wait()
finally:
    api_process.kill()
    chainlit_ui_process.kill()
    playwright_download.wait()
    task_process.kill()
    print("Servers shut down.")