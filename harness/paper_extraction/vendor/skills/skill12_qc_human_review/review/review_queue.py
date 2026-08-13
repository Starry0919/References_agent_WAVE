class ReviewQueue:
    def __init__(self): self.tasks = {}
    def add(self, task): self.tasks[task["task_id"]] = dict(task); return task
    def get(self, task_id): return self.tasks.get(task_id)
