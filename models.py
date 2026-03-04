from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(String)
    output_label = Column(String)
    score = Column(Float)
    latency = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    cache_hit = Column(Integer, default=0) # 1 for hit, 0 for miss
