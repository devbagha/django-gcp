from celery import shared_task
import time

@shared_task
def sample_task(wait_time=10):
    """
    A sample task that sleeps for a specified amount of time.
    """
    time.sleep(wait_time)
    return {'status': 'Task completed', 'wait_time': wait_time}

@shared_task
def add(x, y):
    """
    A simple task that adds two numbers.
    """
    return x + y