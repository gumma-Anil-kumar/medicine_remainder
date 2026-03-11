from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_job():
    """Simple test job"""
    logger.info(f"Test job running at {time.strftime('%H:%M:%S')}")

# Test scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=test_job,
    trigger='interval',
    seconds=10,
    id='test_job',
    replace_existing=True
)

scheduler.start()
logger.info("Test scheduler started")

try:
    # Keep running for 1 minute
    time.sleep(60)
finally:
    scheduler.shutdown()
    logger.info("Test scheduler stopped")