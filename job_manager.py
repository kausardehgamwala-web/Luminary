import time
import uuid
import threading
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('luminary_job_manager')

class Job:
    def __init__(self, job_id: str, job_type: str = 'image', payload: Optional[Dict[str, Any]] = None, warning: Optional[str] = None):
        self.id = job_id
        self.type = job_type
        self.payload = payload or {}
        self.status = 'pending'
        self.result = None
        self.error = None
        self.warning = warning
        self.created_at = time.time()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'job_id': self.id,
            'type': self.type,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        if self.warning:
            data['warning'] = self.warning
        elif self.result and isinstance(self.result, dict) and 'warning' in self.result:
            data['warning'] = self.result['warning']
        return data

class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JobManager, cls).__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self):
        self.jobs: Dict[str, Job] = {}
        self.jobs_lock = threading.RLock()
        self.ttl_seconds = 3600
        self._start_cleanup_worker()

    def _start_cleanup_worker(self):
        def _cleanup_loop():
            while True:
                time.sleep(300)
                self.cleanup_old_jobs()
        t = threading.Thread(target=_cleanup_loop, daemon=True, name='JobManagerCleanup')
        t.start()

    def cleanup_old_jobs(self):
        cutoff = time.time() - self.ttl_seconds
        with self.jobs_lock:
            expired = [jid for jid, job in self.jobs.items() if job.updated_at < cutoff]
            for jid in expired:
                del self.jobs[jid]
            if expired:
                logger.info(f'[JobManager] Cleaned up {len(expired)} expired job(s).')

    def create_job(self, job_type: str = 'image', payload: Optional[Dict[str, Any]] = None, warning: Optional[str] = None) -> Job:
        job_id = f'job_{uuid.uuid4().hex[:12]}'
        job = Job(job_id, job_type, payload, warning=warning)
        with self.jobs_lock:
            self.jobs[job_id] = job
        logger.info(f'[JobManager] Created job {job_id} (type: {job_type}).')
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        with self.jobs_lock:
            return self.jobs.get(job_id)

    def update_job(self, job_id: str, status: Optional[str] = None, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        with self.jobs_lock:
            job = self.jobs.get(job_id)
            if not job:
                return
            if status is not None:
                job.status = status
            if result is not None:
                job.result = result
            if error is not None:
                job.error = error
            job.updated_at = time.time()
            logger.info(f'[JobManager] Updated job {job_id} -> status: {job.status}')

    def submit_image_task(self, prompt: str, width: int, height: int, negative_prompt: str = '', task_fn = None, warning: Optional[str] = None) -> str:
        job = self.create_job(
            job_type='image',
            payload={'prompt': prompt, 'width': width, 'height': height, 'negative_prompt': negative_prompt},
            warning=warning
        )

        def _worker():
            self.update_job(job.id, status='running')
            try:
                if task_fn:
                    img_url = task_fn(prompt, width, height, negative_prompt=negative_prompt)
                    res_payload = {'image_url': img_url}
                    if warning:
                        res_payload['warning'] = warning
                    self.update_job(job.id, status='ready', result=res_payload)
                else:
                    self.update_job(job.id, status='failed', error='No worker function provided')
            except Exception as e:
                logger.exception(f'[JobManager] Job {job.id} execution failed: {e}')
                self.update_job(job.id, status='failed', error=str(e))

        t = threading.Thread(target=_worker, daemon=True, name=f'ImageJob-{job.id}')
        t.start()
        return job.id

job_manager = JobManager()
