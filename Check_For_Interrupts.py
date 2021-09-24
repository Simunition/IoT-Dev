from awscrt import mqtt
import threading
import sys

class Check_For_Interrupts:

    def __init__(self, message, message_set = False, received_count = 0):
        self.message = message
        self.messageSet = message_set
        self.received_count = received_count

    received_all_event = threading.Event()


    def on_connection_interrupted(self, connection, error, **kwargs):
        print("Connection interrupted. error: {}".format(error))


    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.on_resubscribe_complete)


    def on_resubscribe_complete(self, resubscribe_future):
            resubscribe_results = resubscribe_future.result()
            print("Resubscribe results: {}".format(resubscribe_results))

            for topic, qos in resubscribe_results['topics']:
                if qos is None:
                    sys.exit("Server rejected resubscribe to topic: {}".format(topic))


    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))
        global received_count
        self.received_count += 1

        data = (payload.decode('utf-8')).split(':')

        self.messageSet = True
        self.message = data
