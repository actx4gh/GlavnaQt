import inspect
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
    def __init__(self, function: callable, on_finished: callable = None, tag: str = None, stop_flag: callable = None,
                 *args, **kwargs) -> None:
        super().__init__()
        self.function = function
        self.on_finished = on_finished
        self.tag = tag
        self.stop_flag = stop_flag  # Stop flag function
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            # Check if 'stop_flag' is a valid parameter for the function
            sig = inspect.signature(self.function)
            if 'stop_flag' in sig.parameters:
                # Pass stop_flag to the function
                self.function(*self.args, stop_flag=self.stop_flag, **self.kwargs)
            else:
                # Call the function without stop_flag
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

    def __init__(self, max_workers: int = 16) -> None:
        super().__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_workers)
        self.is_shutting_down = False
        self.is_shutting_down_mutex = QMutex()
        self.active_tasks_by_tag = defaultdict(int)
        self.stop_flags_by_tag = defaultdict(lambda: False)  # Stop flags for tasks by tag
        self.tag_mutex = QMutex()
        self.tag_condition = QWaitCondition()

    def submit_task(self, task: callable, *args, tag: str = None, on_finished: callable = None, **kwargs) -> QRunnable:
        with QMutexLocker(self.is_shutting_down_mutex):
            if self.is_shutting_down:
                logger.warning("[ThreadManager] Cannot submit new tasks, shutdown in progress.")
                return None

            try:
                # Always pass the task, decide later in TaskRunnable whether stop_flag is needed
                runnable = TaskRunnable(
                    task,
                    on_finished=on_finished or self.task_finished_callback,
                    tag=tag,
                    stop_flag=lambda: self.stop_flags_by_tag[tag],
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

    def stop_tasks_by_tag(self, tag: str) -> None:
        """
        Signal all tasks with the given tag to stop.
        """
        with QMutexLocker(self.tag_mutex):
            if tag in self.active_tasks_by_tag:
                self.stop_flags_by_tag[tag] = True
                logger.info(f"[ThreadManager] Stop signal sent for tasks with tag '{tag}'")

    def reset_stop_flag(self, tag: str) -> None:
        """
        Reset the stop flag for the specified tag.
        """
        self.stop_flags_by_tag[tag] = False

    def task_finished_callback(self, tag: str) -> None:
        if tag:
            with QMutexLocker(self.tag_mutex):
                if tag in self.active_tasks_by_tag:
                    self.active_tasks_by_tag[tag] -= 1
                    if self.active_tasks_by_tag[tag] <= 0:
                        self.active_tasks_by_tag.pop(tag, None)
                        self.tag_condition.wakeAll()
                        self.stop_flags_by_tag.pop(tag, None)  # Clean up stop flag

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
        Shuts down the thread pool by preventing new tasks from being submitted and stopping all running tasks.

        :return: None
        """
        logger.info("[ThreadManager] Shutting down thread pool and stopping all running tasks.")

        with QMutexLocker(self.is_shutting_down_mutex):
            self.is_shutting_down = True

        # Signal all running tasks to stop
        with QMutexLocker(self.tag_mutex):
            for tag in self.active_tasks_by_tag:
                self.stop_flags_by_tag[tag] = True
            logger.info("[ThreadManager] Stop signals sent for all running tasks.")

        # Do not wait for tasks to finish, just signal shutdown
        self.thread_pool.clear()
        logger.info("[ThreadManager] Thread pool shutdown initiated, not waiting for tasks to complete.")

