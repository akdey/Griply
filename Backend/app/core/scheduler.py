
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
from app.features.wealth.service import WealthService

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler()

async def run_daily_price_sync():
    """
    Task to sync prices for all investment holdings.
    Runs daily.
    """
    logger.info("Starting Daily Price Sync...")
    async with AsyncSessionLocal() as db:
        service = WealthService(db)
        try:
            # We need to implement sync_all_holdings in WealthService first
            await service.sync_all_holdings_prices() 
            logger.info("Daily Price Sync Completed Successfully.")
        except Exception as e:
            logger.error(f"Daily Price Sync Failed: {e}", exc_info=True)

def start_scheduler():
    """
    Start the scheduler if ENABLE_SCHEDULER is True.
    Set ENABLE_SCHEDULER=False when using external cron (e.g., GitHub Actions).
    """
    if not settings.ENABLE_SCHEDULER:
        logger.info("Scheduler disabled (ENABLE_SCHEDULER=False). Using external cron.")
        return
    
    # Schedule the job to run at 3:30 PM IST (10:00 AM UTC)
    # IST is UTC+5:30. 15:30 IST = 10:00 UTC.
    trigger = CronTrigger(hour=10, minute=0)  # 10:00 AM UTC = 3:30 PM IST
    
    scheduler.add_job(run_daily_price_sync, trigger)
    scheduler.start()
    logger.info("Scheduler started. Jobs scheduled.")
