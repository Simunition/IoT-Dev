import time
from random import randint
import Thermostat
import Check_For_Interrupts as Check
import boto3

##Main Function 
def main():

    #create a thermostat
    thermostat = Thermostat.Thermostat()

    #Setup IoT
    iot = boto3.client('iot-data')

    #while loop runs infinately to iterate the thermostat actual temp up and down
    #once every 2-10 minutes and checks for an MQTT message (interrupt) once every second 

    while (True):
        rand_time = randint(1,5)
        
        thermostat.temp_loop(thermostat)
        iot.publish(topic='/test', payload='test')

        for i in range(rand_time):
            Check.check_for_interrupt(thermostat)
            time.sleep(1)


if __name__ == "__main__":
    main()