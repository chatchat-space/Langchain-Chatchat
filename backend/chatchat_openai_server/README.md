celery 使用
set PTYTHONPATH=D:\job\kaiyuan\Langchain-Chatchat\backend\chatchat_openai_server
celery -A app.main.task_app worker -l info -P eventlet

alembic 数据表管理

Generic single-database configuration.
alembic revision --autogenerate -m "init"

# Apply the changes

alembic upgrade head

alembic revision --autogenerate -m "first add commit"