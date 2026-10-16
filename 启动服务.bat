@echo off
chcp 65001 >nul
title Langchain-Chatchat 启动器

REM 前置：Ollama 需在运行（模型 qwen2.5:7b + bge-m3）
curl -s --noproxy "*" -o nul -m 3 http://127.0.0.1:11434/api/tags
if errorlevel 1 (
    echo [!] Ollama 未运行，正在启动...
    start "" "D:\ollama\ollama.exe" serve
    timeout /t 5 /nobreak >nul
)

cd /d D:\github_projects\Langchain-Chatchat
set CHATCHAT_ROOT=D:\github_projects\Langchain-Chatchat\data
set PYTHONUNBUFFERED=1

echo [*] 启动 chatchat（API:7861  WebUI:8501）...
".venv\Scripts\chatchat.exe" start -a
