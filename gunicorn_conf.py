from multiprocessing import cpu_count

# Socket Path
bind = 'unix:/home/suraj/fastapi/gunicorn.sock'

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/suraj/fastapi/access_log'
errorlog =  '/home/suraj/fastapi/error_log'