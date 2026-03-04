from langchain_core.messages.human import HumanMessage
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.databases.db_config import SessionLocal
from app.crud.topics import get_topics
from app.graph import app as chanakya_brain

logger = logging.getLogger(__name__)

class IntelligenceScheduler:
    def __init__(self):
        # We use BackgroundScheduler so it doesn't block FastAPI's main thread
        self.scheduler = BackgroundScheduler()
        
    def _get_topics_from_db(self):
        """Fetches all active ScoutTopics from the Postgres database."""
        
        with SessionLocal() as db:
            topics = get_topics(db)
            # Extract just the string topic from the SQLAlchemy models
            return [t.topic for t in topics]

    def execute_standing_orders(self,order_text:str):
        logger.info(f"🦾 AUTOPILOT ENGAGED: Executing Standing Order: {order_text}")

        try:
            msgDic = {
                "messages":[
                    HumanMessage(content=order_text)
                ]
            }

            chanakya_brain.invoke(msgDic)
            logger.info(f"✅ AUTOPILOT SUCCESS: {order_text}")
        except Exception as e:
            logger.error(f"❌ AUTOPILOT FAILED: {order_text} | Error: {str(e)}")
        
    def start(self):
        # Fetch the live topics from the database right as the server boots
        standing_orders = self._get_topics_from_db()
        logger.info(f"Loaded {len(standing_orders)} Standing Orders from the database.")
        
        # Schedule the jobs. We will run them every 12 hours in production.
        
        # To run ALL orders, we just loop through the array and add a job for each one!
        # We must stagger the jobs so they don't fire at the exact same millisecond.
        # If we fire two LangGraphs concurrently, DuckDuckGo Search and ChromaDB will rate-limit or deadlock.
        from datetime import datetime, timedelta
        
        for i, order in enumerate(standing_orders):
            # We delay the first job by 10 seconds, the second by 55 seconds, etc.
            staggered_start = datetime.now() + timedelta(seconds=10 + (i * 45))
            
            self.scheduler.add_job(
                self.execute_standing_orders,
                trigger="interval",
                hours=12, # Slowed down for production.
                args=[order],
                id=f"intel_update_{i}",
                replace_existing=True,
                next_run_time=staggered_start
            )

        # Start the background thread
        self.scheduler.start()
        logger.info("🕒 Intelligence Scheduler Started.")

    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("🛑 Intelligence Scheduler Shut Down.")

# Create a singleton instance we can import in main.py
autopilot = IntelligenceScheduler()
