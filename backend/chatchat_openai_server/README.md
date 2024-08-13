set PTYTHONPATH=D:\job\kaiyuan\Langchain-Chatchat\backend\chatchat_openai_server
celery -A app.main.task_app worker -l info -P eventlet