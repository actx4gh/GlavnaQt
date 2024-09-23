from collections import defaultdict

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QMutexLocker, QMutex, QWaitCondition

from glavnaqt.core import logger


def log_active_threads() -> None:
    """
    Logs the active thread count in the global QThreadPool instance.

    :return: None
    """
    thread_pool = QThreadPool.globalInstance()
    active_count = thread_pool.activeThreadCount()
    logger.debug(f"[ThreadManager] Active threads: {active_count}")


class TaskRunnable(QRunnable):
    """
    A QRunnable subclass that wraps a callable task and supports tagging.

    Attributes:
        function (callable): The task function to be executed in the thread.
        on_finished (callable, optional): The callback function to be called after the task finishes.
        tag (str, optional): A tag to identify tasks by group or purpose.
        args (tuple): Arguments to pass to the task function.
        kwargs (dict): Keyword arguments to pass to the task function.
    """

    def __init__(self, function: callable, on_finished: callable = None, tag: str = None, *args, **kwargs) -> None:
        """
        Initializes a TaskRunnable object.

        :param function: The callable to be run in the task.
        :param on_finished: An optional callable to be called when the task completes.
        :param tag: An optional string tag to group tasks.
        :param args: Additional positional arguments for the task.
        :param kwargs: Additional keyword arguments for the task.
        """
        super().__init__()
        self.function = function
        self.on_finished = on_finished
        self.tag = tag
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        Runs the task function, handles exceptions, and calls the on_finished callback if provided.

        :return: None
        """
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            logger.error(f"[ThreadManager] Error executing task with tag '{self.tag}': {e}")
        finally:
            if self.on_finished:
                try:
                    self.on_finished(self.tag)
                except Exception as e:
                    logger.error(f"[ThreadManager] Error in on_finished callback for tag '{self.tag}': {e}")


class ThreadManager(QObject):
    """
    Manages a thread pool and provides methods for submitting, tracking, and waiting for tasks.

    Attributes:
        thread_pool (QThreadPool): The thread pool used to manage tasks.
        is_shutting_down (bool): A flag indicating if the manager is shutting down.
        is_shutting_down_mutex (QMutex): A mutex to protect access to the is_shutting_down flag.
        active_tasks_by_tag (defaultdict): A dictionary to track the number of active tasks by tag.
        tag_mutex (QMutex): A mutex to protect access to active_tasks_by_tag.
        tag_condition (QWaitCondition): A condition variable to signal when all tasks for a tag are completed.
    """

    def __init__(self, max_workers: int = 16) -> None:
        """
        Initializes a ThreadManager with the specified maximum number of worker threads.

        :param max_workers: The maximum number of threads in the thread pool.
        :return: None
        """
        super().__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_workers)
        self.is_shutting_down = False
        self.is_shutting_down_mutex = QMutex()

        self.active_tasks_by_tag = defaultdict(int)
        self.tag_mutex = QMutex()
        self.tag_condition = QWaitCondition()

    def submit_task(self, task: callable, *args, tag: str = None, on_finished: callable = None, **kwargs) -> QRunnable:
        """
        Submits a task to the thread pool and assigns it a tag and optional completion callback.

        :param task: The task function to be run in a separate thread.
        :param tag: An optional string tag to group tasks by purpose.
        :param on_finished: A callback function to be called when the task finishes.
        :param args: Positional arguments to pass to the task.
        :param kwargs: Keyword arguments to pass to the task.
        :return: The QRunnable object representing the submitted task.
        """
        with QMutexLocker(self.is_shutting_down_mutex):
            if self.is_shutting_down:
                logger.warning("[ThreadManager] Cannot submit new tasks, shutdown in progress.")
                return None

            try:
                runnable = TaskRunnable(
                    task,
                    on_finished=on_finished or self.task_finished_callback,
                    tag=tag,
                    *args,
                    **kwargs
                )

                if tag:
                    with QMutexLocker(self.tag_mutex):
                        self.active_tasks_by_tag[tag] += 1

                self.thread_pool.start(runnable)
                return runnable
            except Exception as e:
                logger.error(f"[ThreadManager] Error submitting task: {e}")
                return None

    def task_finished_callback(self, tag: str) -> None:
        """
        A callback that is called when a task completes. It decrements the active task count for the tag
        and wakes any waiting threads if all tasks with the tag are completed.

        :param tag: The tag associated with the completed task.
        :return: None
        """
        if tag:
            with QMutexLocker(self.tag_mutex):
                if tag in self.active_tasks_by_tag:
                    self.active_tasks_by_tag[tag] -= 1
                    if self.active_tasks_by_tag[tag] <= 0:
                        self.active_tasks_by_tag.pop(tag, None)
                        self.tag_condition.wakeAll()

    def wait_for_tagged_tasks(self, tag: str) -> None:
        """
        Waits for all tasks associated with the specified tag to complete.

        :param tag: The tag of the tasks to wait for.
        :return: None
        """
        with QMutexLocker(self.tag_mutex):
            while tag in self.active_tasks_by_tag:
                self.tag_condition.wait(self.tag_mutex)

    def shutdown(self) -> None:
        """
        Shuts down the thread pool by preventing new tasks from being submitted and waiting for
        all running tasks to complete.

        :return: None
        """
        logger.info("[ThreadManager] Shutting down thread pool.")
        with QMutexLocker(self.is_shutting_down_mutex):
            self.is_shutting_down = True

        self.thread_pool.waitForDone()
        logger.info("[ThreadManager] Thread pool shutdown complete.")
