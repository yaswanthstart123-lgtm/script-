"""
SecureHub — MongoDB Connection (Motor Async Driver)
Used for activity logging.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

settings = get_settings()

# ── MongoDB Client ───────────────────────────────
mongo_client: AsyncIOMotorClient = None
mongo_db: AsyncIOMotorDatabase = None


async def connect_mongo():
    """Initialize MongoDB connection on app startup."""
    global mongo_client, mongo_db
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    mongo_db = mongo_client[settings.MONGO_DB_NAME]

    # Create indexes for activity logs
    await mongo_db.activity_logs.create_index("timestamp")
    await mongo_db.activity_logs.create_index("user_id")
    await mongo_db.activity_logs.create_index("path")


async def close_mongo():
    """Close MongoDB connection on app shutdown."""
    global mongo_client
    if mongo_client:
        mongo_client.close()


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Get the MongoDB database instance."""
    return mongo_db
