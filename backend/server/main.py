from fastapi import FastAPI, HTTPException,WebSocket
from pydantic import BaseModel
import  pika, json, asyncio

from fastapi.middleware.cors import CORSMiddleware
from typing import List

from threading import Thread
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

connected_clients = set()
# Pydantic model for request validation
class Order(BaseModel):
    side: str
    symbol: str
    quantity: float
    price: float
    ordertype: str
    tif: str
    notes: str = ''

async def broadcast(message):
    dead_clients = []
    for ws in connected_clients:
        try:
            await ws.send_json(message)
        except:
            dead_clients.append(ws)
    for ws in dead_clients:
        connected_clients.remove(ws)

def consume_exec_reports():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue="execution_reports", durable=True)

    def cb(ch, method, properties, body):
        report = json.loads(body)
        print("Forwarding report to Web Clients:", report)

        # Send to async FastAPI loop
        asyncio.run(broadcast(report))

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="execution_reports", on_message_callback=cb)
    print("Waiting for Execution Reports...")
    channel.start_consuming()

# Start Rabbit consumer in separate thread
Thread(target=consume_exec_reports, daemon=True).start()




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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # if you want to receive messages
            print("Received from client:", data)
    except Exception:
        connected_clients.remove(websocket)



@app.post("/orders")
async def place_order(order: Order):
    try:
        print (order)
        publish_order(order.dict())
        return {"status": "success", "message": "Order queued successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
