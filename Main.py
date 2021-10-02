import time, json
from random import randint
import Thermostat
import Check_For_Interrupts as Check
from awsiot import mqtt_connection_builder
from awscrt import mqtt, io


#This program is designed to create a virtual IoT device (thermostat) and connect it to the MQTT broker hosted by AWS IoT Core.
#It's designed to have pseudo realistic loops for changing the values associated with the thermostat as they would in real life,
#however, you can easily use this on a physical device by replacing the loops in Thermostat.py with code that actually pulls 
#real values from sensors attached to the device. This requires an AWS account, with a 'thing' created in IoT Core, which you
#can find at: https://aws.amazon.com/iot-core/. 


def main():

    log_file = open('log.txt', 'a')

    #Spin up resources for connection to IoT Core MQTT Broker 

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    #Create thermostat, the three attributes below are the ones that are mandatory to pass,
    #others include humidity, light level, and temperature, default values are:
    #humidity = 70
    #light level = 1
    #temperature = 70

    thermostat = Thermostat.Thermostat(
        storage_ID      = '',
        storage_name    = '',
        address         = '',
    )

    #Create a check object that retains a message when it's received until it can be parsed 

    check = Check.Check_For_Interrupts()

    #Variables for mqtt connection and publishing/subscribing

    #the endpoint for your device is located under AWS IoT > Settings > Device data endpoint
    #while the endpoint is associated with the entire AWS account, the certificates are associated with a specific 'thing'
    #in AWS IoT, and you can find those under AWS IoT > Manage > Things > your thing > certficates 
    #the root_ca cert is one of the CA certficiates for server authentication that AWS owns and maintains 
    #and you can find it at https://docs.aws.amazon.com/iot/latest/developerguide/server-authentication.html

    #once you have these authentication variables configured, client_id, sub_topic, and pub_topic
    #can be any string that you like, client_id is the ID used for the connection and is attached to the publications 
    #subscription topic is the channel that the device will listen to for requests to set the temperature and light level of the device
    #publish topic is where the device sends messages to regarding current statistics, and should be the same channel you should subscribe to 
    #from another device if you want to receive those messages

    endpoint = ''   #ex \"abcd12345wxyz-ats.iot.us-east-1.amazonaws.com\"
    port = 8883      #443 or 8883
    cert = ''       #file path to client cert in PEM format.
    key = ''        #File path to your private key, in PEM format.
    root_ca = ''    #file path to root CA in PEM format.
    client_id = 'clientTest'  #client ID for MQTT connection
    sub_topic = 'subTest'      #topic to sub to
    pub_topic = 'pubTest'      #topic to pub to


    #Create an MQTT connection with the above variables using the AWS IoT Connection Builder 

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=port,
            cert_filepath=cert,
            pri_key_filepath=key,
            client_bootstrap=client_bootstrap,
            ca_filepath=root_ca,
            on_connection_interrupted=check.on_connection_interrupted,
            on_connection_resumed=check.on_connection_resumed,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=30,
        )

    #Connection processing and confirmation that the connection succeeded 

    log_file.write("Connecting to {} with client ID '{}'... \n".format(
        endpoint, client_id))

    connect_future = mqtt_connection.connect()

    #Future.result() waits until a result is available

    connect_future.result()
    log_file.write("Connected!\n")


    #Subscribe to the requested topic, when a message is received it passes it into on_message_received in the 
    #check for interrupts class, which then stores the message and sets a boolean flag to indicate a message is waiting

    log_file.write("Subscribing to topic '{}'...\n".format(sub_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=sub_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=check.on_message_received)

    #Confirmation that subscription was successful 

    subscribe_result = subscribe_future.result()
    log_file.write("Subscribed with {}\n".format(str(subscribe_result['qos'])))


    #Now that we have our environment set up and connections made, this loop does all the heavy lifting.
    #First, it's enclosed in a try catch loop that catches a keyboard interrupt and uses that to disconnect the MQTT session.
    #Inside it changes the temperature of the thermostat and there's a 1/100 chance it also changes the humidity level. 
    #After that, it collects the current data associated with the thermostat object and publishes it to the appropriate topic with the MQTT broker. 
    #Once the values have changed, or had a chance to change, we start a for loop that uses the random integer generated to wait somewhere 
    #between 2 and 10 minutes to start the loop over. It waits 1 second at a time, and each second it checks to see if there is a message 
    #from the subscribed topic, and if there is it responds appropriately. Currently, the only messages it is configured to receive are 
    #one to change the set temperature, and one to change the light level. The messages are also expected to arrive in JSON format.
    #Once the message is parsed it sets the boolean for message set back to false. The limitation of this method is that the device cannot
    #recieve more than 1 request to change one of these values per second, however, it can receive a request to change both at once as long as they 
    #are sent in a single message. As an example, here's how these messages should be formatted when they're received:
    # {
    #     "setTemp": "25",
    #     "setLight": "1"
    # }
    #Optional to include one or both of these keys, the values are expected to be integers

    try:
        while (True):
            rand_time = randint(120,600) ##change to 120, 600 in production, 1,5 for testing
            
            if(randint(1,100) == 66):
                thermostat.humidity_loop()
            
            thermostat.temp_loop()
            data = json.dumps(thermostat.getData())
            log_file.write(data + '\n')

            mqtt_connection.publish(
                topic = pub_topic,
                payload=data,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )

            for i in range(rand_time):
                log_file.flush()
                if(check.messageSet == True):
                    setRequest = json.loads(check.message)

                    for (k, v) in setRequest.items():
                        if (k == "setTemp"):
                            thermostat.set_temp = int(v)
                            check.messageSet = False
                        elif (k == "setLight"):
                            thermostat.light_level = int(v)
                            check.messageSet = False
                time.sleep(1)

    except KeyboardInterrupt:
        #disconnect the MQTT broker connection upon interrupt from the keyboard 

        log_file.write("Disconnecting...\n")
        log_file.close()
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        log_file.write("Disconnected!\n")


if __name__ == "__main__":
    main()