#quickfix #python #fastapi #reactjs #tailwindcss 

Fix Engine written with help of quickfix third part library, with backend written in python and front-end written in react js. 
Three basic trading algorithms implemented in the application (Market/Immediate, TWAP, Mean Reversion) 

This application covers over 

1.Folder layout (developer-friendly)

2. Interfaces (Strategy, Order, OrderManager, FIXInitiator)

3. Strategy base + examples (Market, TWAP, MeanReversion)

4. OrderManager that receives signals (via direct call or RabbitMQ), validates & routes to FIXInitiator

5. FIXInitiator wrapper (non-blocking, waits for logon, callback for exec reports)

6. Minimal ExecutionReport handling and lifecycle

7. Testing & deployment notes, monitoring, safety checks



High Level architecutre of application is 

                                +------------------+
                                |   Web Client     |
                                | (UI / Algo cfg)  |
                                +--------+---------+
                                         |
                                         | REST / WebSocket
                                         v
                   +----------------+ FastAPI (API) ----------------+
                   |                                            |
                   | publishes orders / receives exec reports   |
                   | (REST -> RabbitMQ / WS clients subscribe)  |
                   +----------------+---------------------------+
                                    |
                    RabbitMQ 'orders' queue (durable)
                                    |
                  +-----------------v----------------+
                  |   Order Manager (service)         |  <-- validates, risk checks, splits orders
                  |  - accepts signals/orders         |
                  |  - instantiates execution algos   |
                  |  - sends send_order() to FIXInitiator
                  +-----------------+----------------+
                                    |
                                    v
                          FIXInitiator (wrapper around quickfix)
                          - starts SocketInitiator
                          - waits for onLogon before sending
                          - handles exec reports -> forwards to Order Manager / RabbitMQ


                                    |
                                    v
                              Counterparty FIX Gateway

