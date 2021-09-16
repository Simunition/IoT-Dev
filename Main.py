import time
from random import randint
import Thermostat
import Check_For_Interrupts as Check

##Main Function 
def main():
    thermostat = Thermostat.Thermostat()

    while (True):
        rand_time = randint(120,600)
        
        Thermostat.temp_loop(thermostat)

        for i in range(rand_time):
            Check.check_for_interrupt()
            time.sleep(1)


if __name__ == "__main__":
    main()