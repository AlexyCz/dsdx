# DSDX - Distributed Systems Design by Example

---

# Publish-Subscribe Message Queue

## Expand
> Decoupling in a pub-sub system:
> 
The focus with an implemention of a publish-subscriber model is that it allows for seperation of concerns by reducing dependencies between those that are sending messages/requests and those are recieving those messages for whatever business logic comes next. "..enables independent development, testing, and scaling" given they are seperate components with specified tasks and concerns.

Low level attribute: using separate queues per subscriber to decouple the multiple recievers of a single message sent by a publisher.

> Drop, Block, and Signal backpressure strategies:
> 

Drop strategies (rather self-descriptive) allow the system to reject new incoming messages given the current full state of a queue. Naturally, we lose information with this strategy, so it is important to have some mechanisms in place when we are wanting to be aware of every piece of data flowing through.
Blocking makes the publisher tightly coupled with the subscriber. A publisher will stall any actions until there is space in the queue for another message. If a subscriber is slow, the publisher will be slow.
Signaling across components can take on a few strategies, explained here are the publisher dynamically adjusting its publishing rates based on queue hold up or failures, and also utilizing prioritization for messages to have a smarter approach to dropping incoming requests.

> Why an acknowledgment-based delivery implementation?
>
Firstly, provides a strong feedback loop for message delivery resolution. If a subscriber will have the responsibility of acknowledging a message once processed so that the broker can requeue a dropped message or remove it from needing another acknowledgement check. Critical here given there is a possibility of delivering the same message more than once is idempotency, nth processing is identical to 0th processing.

> Round-robin and partition-based consumer group assignment:
>

## Exercises:

### One:

> In the backpressure simulation, what happens if you increase the publisher's base interval to match the subscriber's processing time? What if you set the queue size to 1? Run both variations and describe the equilibrium behavior in each case.
> 

In `ex_backpressure.py`, L20 has arguments for the back pressure publisher; increase the base interval to `1.0`. In L25, reduce the processing time for the subscriber to match, i.e. `1.0`.

Reference `msgque/ex_backpressure_pubsub_interval_processing_match.out`: We see that the subscriber can process every message that was published. Not a single message dropped given there was never a moment of backpressure hit the subscriber.

Same file, L16 has the call to the broker; change the queue size to `1`.

Reference `msgque/ex_backpressure_single_msg_queue.out`: Messages immediately encounter backpressure and forces the publisher to increase time between the next message that is being published. However, unsure if matching interval and processing time values should remain for this single message queue simulation.



### Two:

> The priority broker evicts low-priority messages when the queue is full. Add a counter to track how many messages of each priority level were dropped. Run a simulation where the publisher sends equal numbers of high- and low-priority messages. What fraction of each priority level was dropped? (Starter: add dropped_by_priority: dict to the broker's init.)
> 

In `priority_backpressure.py`: add new attribute `messages_dropped` that will be a dictionary with priority level as key and count as value.
In `publish()`:L63 within the else block, we acknowledge the message that was dropped.

### Three:

> A subscriber crashes after dequeuing a message but before acknowledging it. In the acknowledgment broker, what happens to that message? Trace through ack_broker.py to find where the timeout fires and what it does. What would happen if the subscriber crashed again on the redelivered message?
> 

In the acknowledgement broker we have the attribute of `pending_acks` that holds all id's that need to be addressed. If the subscriber dequed but didn't call the `acknowledge` method, we will still find the id in the list. Subsequently, the broker executes a redelivery on L51.
This will keep going until the `pending_acks` list no longer contains this particular dropped `ack_id`.

### Four:

> The consumer group uses round-robin distribution. Write a simulation where one consumer in a group is 10x slower than the others (it takes 10 time units to process each message instead of 1). Does round-robin distribute load evenly in this case? Propose a least-loaded distribution strategy and describe what state the distributor would need to track.
> 

TODO

### Five:

> The current broker does not persist messages to disk. If the broker process crashes, all queued messages are lost. Describe the changes needed to support durable messaging (messages survive broker restarts). What is the performance cost of each change?
> 

We can do intermittent disk writes to reduce the cost of outputs. Writing out of memory is time costly, so it is an efficiency decision to keep the writes within a designated frequency.
Another idea would be to add another condition to write out given a certain volume of messages in the queue. I only think of this given a slow down or crashed subscriber, we start gathering a large amount of messages that need addressing, so safety would suggest to write out.
