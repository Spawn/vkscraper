import gevent


class AsyncRequests(object):

    def __init__(self, timeout):
        self.jobs_pull = []
        self.timeout = timeout

    def add_job(self, job):
        self.jobs_pull.append(job)

    def join_jobs(self):
        timeout = len(self.jobs_pull) * self.timeout
        for result in gevent.joinall(self.jobs_pull, timeout=timeout):
            yield result.get()
