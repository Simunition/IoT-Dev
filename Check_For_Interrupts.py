from awscrt import mqtt
import threading
import sys

class Check_For_Interrupts:

    #This class has attributes to hold the last message, a boolean to indicate whether there is a message waiting to be processed,
    #and a total count of all messages received while running.

    def __init__(self, message = '', message_set = False, received_count = 0):
        self.message = message
        self.messageSet = message_set
        self.received_count = received_count

    received_all_event = threading.Event()

    #Method printed to the device terminal indicating the connection has been interrupted and indicates the error 

    def on_connection_interrupted(self, connection, error, **kwargs):
        log_file = open('log.txt', 'a')
        log_file.write("Connection interrupted. error: {}\n".format(error))
        log_file.close()

    #Method to print out information when the connection is resumed

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        log_file = open('log.txt', 'a')
        log_file.write("Connection resumed. return_code: {} session_present: {}\n".format(return_code, session_present))
        log_file.close()

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            log_file = open('log.txt', 'a')
            log_file.write("Session did not persist. Resubscribing to existing topics...\n")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.on_resubscribe_complete)
            log_file.close()

    #Method for resubscribing 

    def on_resubscribe_complete(self, resubscribe_future):
            log_file = open('log.txt', 'a')
            resubscribe_results = resubscribe_future.result()
            log_file.write("Resubscribe results: {}\n".format(resubscribe_results))

            for topic, qos in resubscribe_results['topics']:
                if qos is None:
                    sys.exit("Server rejected resubscribe to topic: {}".format(topic))
            log_file.close()

    #This method actually receives the message from the subscribed topic and sets message equal to the payload, decoded into utf-8
    #for easier reading. It also flips the messageSet boolean to True so that the next time the main loop checks for a 
    #message it see's that there is one pending.

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        log_file = open('log.txt', 'a')
        log_file.write("Received message from topic '{}': {}".format(topic, payload.decode('utf-8')))
        global received_count
        self.received_count += 1

        data = (payload.decode('utf-8'))

        self.messageSet = True
        self.message = data
        log_file.close()
