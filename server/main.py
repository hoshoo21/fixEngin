from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Order API")

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'orders'


origins = [
    "http://localhost:5173/",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       #
    allow_credentials=True,
    allow_methods=["*"],          # allow POST, OPTIONS, GET, etc.
    allow_headers=["*"],          # allow headers like Content-Type
)


# Pydantic model for request validation
class Order(BaseModel):
    side: str
    symbol: str
    quantity: float
    price: float
    ordertype: str
    tif: str
    notes: str = ''


def publish_order(order_data: dict):
    """
    Publish order to RabbitMQ queue
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(order_data),
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )
        print ("order executed successfully ")
        connection.close()
    except Exception as e:
        print("RabbitMQ publish error:", e)
        raise


@app.post("/orders")
async def place_order(order: Order):
    try:
        print (order)
        publish_order(order.dict())
        return {"status": "success", "message": "Order queued successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
