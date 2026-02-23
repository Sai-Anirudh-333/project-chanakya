from langchain_core.messages.human import HumanMessage
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.graph import app as chanakya_brain

logger = logging.getLogger(__name__)

class IntelligenceScheduler:
    def __init__(self):
        # We use BackgroundScheduler so it doesn't block FastAPI's main thread
        self.scheduler = BackgroundScheduler()
        # Define our "Standing Orders" - intel we want gathered on a schedule
        self.standing_orders = [
            "Provide a strategic update on India's defense procurements and border infrastructure development.",
            "Analyze current technological partnerships and semiconductor initiatives in India.",
            "Summarize recent diplomatic engagements between India and the Middle East or Indian Ocean region."
        ]

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
        # Schedule the jobs. We will run them every 6 hours in production, 
        # but for testing, let's just run one every 1 minute.
        
        # To run ALL orders, we just loop through the array and add a job for each one!
        # CRITICAL FIX: We must stagger the jobs so they don't fire at the exact same millisecond.
        # If we fire two LangGraphs concurrently, DuckDuckGo Search and ChromaDB will rate-limit or deadlock.
        from datetime import datetime, timedelta
        
        for i, order in enumerate(self.standing_orders):
            # We delay the first job by 10 seconds, the second by 55 seconds, etc.
            staggered_start = datetime.now() + timedelta(seconds=10 + (i * 45))
            
            self.scheduler.add_job(
                self.execute_standing_orders,
                trigger="interval",
                minutes=2, # Slowed down from 60 seconds to prevent API abuse
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
