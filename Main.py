import time, json
from random import randint
import Thermostat
import Check_For_Interrupts as Check
from awsiot import mqtt_connection_builder
from awscrt import mqtt, io

##Main Function 
def main():
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    #create a thermostat
    thermostat = Thermostat.Thermostat()

    #variables for mqtt connection and pub/sub
    endpoint = 'a1w7q2emoqb76a-ats.iot.us-east-2.amazonaws.com'   #ex \"abcd12345wxyz-ats.iot.us-east-1.amazonaws.com\"
    port = 8883      #443 or 8883
    cert = 'C:\\Users\\sims8\\OneDrive\\Public\\Python\\IoT\\4a90b6d6a1-certificate.pem'       #file path to client cert in PEM format.
    key = 'C:\\Users\\sims8\\OneDrive\\Public\\Python\\IoT\\4a90b6d6a1-private.pem'        #File path to your private key, in PEM format.
    root_ca = 'C:\\Users\\sims8\\OneDrive\\Public\\Python\\IoT\\AmazonRootCA1.pem'    #file path to root CA in PEM format.
    client_id = 'clientTest'  #client ID for MQTT connection
    sub_topic = 'subTest'      #topic to sub to
    pub_topic = 'pubTest'      #topic to pub to

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=port,
            cert_filepath=cert,
            pri_key_filepath=key,
            client_bootstrap=client_bootstrap,
            ca_filepath=root_ca,
            on_connection_interrupted=Check.on_connection_interrupted,
            on_connection_resumed=Check.on_connection_resumed,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=30,
        )

    print("Connecting to {} with client ID '{}'...".format(
        endpoint, client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(sub_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=sub_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=Check.on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    #publish 
    try:
        while (True):
            rand_time = randint(1,5) ##change to 120, 600 in production
            
            thermostat.temp_loop(thermostat)
            data = json.dumps(thermostat.getData(thermostat))
            print(data)

            mqtt_connection.publish(
                topic = pub_topic,
                payload=data,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )

            for i in range(rand_time):
                time.sleep(1)

    except KeyboardInterrupt:
        #on keyboard interrupt 
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")


if __name__ == "__main__":
    main()