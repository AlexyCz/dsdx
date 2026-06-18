# DSDX - Distributed Systems Design by Example

---

# Publish-Subscribe Message Queue

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

TODO

### Four:

> The consumer group uses round-robin distribution. Write a simulation where one consumer in a group is 10x slower than the others (it takes 10 time units to process each message instead of 1). Does round-robin distribute load evenly in this case? Propose a least-loaded distribution strategy and describe what state the distributor would need to track.
> 

TODO

### Five:

> The current broker does not persist messages to disk. If the broker process crashes, all queued messages are lost. Describe the changes needed to support durable messaging (messages survive broker restarts). What is the performance cost of each change?
> 

TODO
