# IOT System Simulation
Course Project for CSC-591 IOT Analytics

## System Description
We will consider a simple IoT system where a large number of sensors send messages to a server. Each message contains information collected by a sensor. We assume that the server is near the sensors so that the propagation delay from a sensor to the server is negligible. The server processes the messages and issues commands to actuators. We assume that there are two types of messages, real-time (RT) and non real-time (nonRT). RT messages have to be processed as fast as possible since they represent tasks that need to be executed in real time. NonRT messages represent non real-time tasks and therefore they are not time constrained. The server maintains two queues, an RT queue and a nonRT queue, as shown below.

![simulation](https://user-images.githubusercontent.com/60016007/94994759-caf8b780-0567-11eb-97b5-b6583fe3d998.PNG)

The RT queue has a preemptive priority over the nonRT queue. That is:
1. Each time the server completes a service, i.e., processing a message, it checks the RT queue to see if there are any messages waiting. If there is a message waiting, then it starts processing it. 
2. If the RT queue is empty, the server checks the nonRT queue. 
a. If there is a message waiting, it starts processing it. 
b. If there are no messages waiting, the server becomes idle. 
3. If during the time the server is processing a nonRT message, an RT message arrives, the server interrupts the processing of the nonRT message and starts processing the RT message. Upon completion of processing the RT message, the server selects the next message by going back to step 1. 
4. When the server processes an interrupted nonRT message, it starts processing it from where it stopped when it was interrupted. (This policy is called pre-emptive resume and it is common in CPU scheduling.)

## Project Description
Develop an event-based simulation model of the two-queueuing system at the server, with a view to calculating the 95th percentile of the response time of RT and nonRT messages. The response time is defined as the time elapsing from the time an RT (nonRT) message joins its queue to the moment it is fully processed by the server and departs from the server. Embellish your simulation with additional code so that to estimate the confidence intervals of the response time of the RT and nonRT messages and plot them using graphs.
