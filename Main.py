import time
from random import randint
import Thermostat
import Check_For_Interrupts as Check

##Main Function 
def main():

    #create a thermostat
    thermostat = Thermostat.Thermostat()

    #while loop runs infinately to iterate the thermostat actual temp up and down
    #once every 2-10 minutes and checks for an MQTT message (interrupt) once every second 

    while (True):
        rand_time = randint(1,5)
        
        thermostat.temp_loop(thermostat)

        for i in range(rand_time):
            Check.check_for_interrupt(thermostat)
            time.sleep(1)


if __name__ == "__main__":
    main()