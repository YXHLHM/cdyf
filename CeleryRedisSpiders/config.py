import os

# redis
redis_url = os.getenv("redis_url", "redis://127.0.0.1:6379/0")
result_redis_url = os.getenv("result_redis_url", "redis://127.0.0.1:6379/1")

# 配置 Redis 客户端用于暂存详情数据（使用与 Celery 相同的 Redis，但使用不同的 db），
DETAIL_BUFFER_REDIS_URL = os.getenv("DETAIL_BUFFER_REDIS_URL", "redis://127.0.0.1:6379/2")

# 数据库连接配置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/smzdm?charset=utf8mb4")


class CeleryConfig:
    """Celery 配置"""
    broker_url = redis_url  # 消息队列
    result_backend = result_redis_url  # 存储任务执行的结果状态，比如任务是否成功、返回值或异常信息。

    # 序列化设置
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']

    # 时区配置
    enable_utc = False  # 关闭 UTC，启用本地时区
    timezone = 'Asia/Shanghai'  # 设置时区为上海时间

    # 任务路由（不同任务分配到不同队列）
    task_routes = {
        'tasks.process_list_page': {'queue': 'list_queue'},
        'tasks.process_detail_page': {'queue': 'detail_queue'},
        'tasks.bulk_save_detail_data': {'queue': 'periodic_queue'},  # 定时任务专用队列
    }

    # Worker 配置
    worker_max_tasks_per_child = 250_000  # 250MB，防止内存泄漏
    task_time_limit = 300  # 任务超时 300 秒

    # 确保任务不会丢失
    task_acks_late = True  # 任务处理完才确认，防止任务丢失
    task_reject_on_worker_lost = True  # Worker 崩溃时重新放回队列

    broker_connection_retry_on_startup = True  # 解决新版 Celery 的启动警告
    task_track_started = True  # 显示任务开始状态
    worker_send_task_events = True  # 启用事件监控

    # Celery Beat 定时任务调度
    beat_schedule = {
        'bulk-save-every-minute': {
            'task': 'bulk_save_detail_data',
            'schedule': 60.0,  # 每 60 秒执行一次
            'args': (1000,),  # 每次处理 1000 条数据
        },
    }

    # # Celery Beat 定时任务调度
    # beat_schedule = {
    #     "run-every-30-seconds": {
    #         "task": "print_hello",
    #         "schedule": 10.0,  # 每 30 秒执行一次
    #     },
    # }
    # Celery Beat 定时任务调度
