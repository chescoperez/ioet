import re
import datetime
import os


BANDINC = ["00:00", "09:01", "18:01"]
BANDEND = ["09:00", "18:00", "23:59"]


# Cost band

weekband1 = 25
weekband2 = 15
weekband3 = 20
weekendband1 = 30
weekendband2 = 20
weekendband3 = 25

# Time Bands

franjaInc1 = datetime.time(
    int(BANDINC[0].split(':')[0]), int(BANDINC[0].split(':')[1]))
franjaInc2 = datetime.time(
    int(BANDINC[1].split(':')[0]), int(BANDINC[1].split(':')[1]))
franjaInc3 = datetime.time(
    int(BANDINC[2].split(':')[0]), int(BANDINC[2].split(':')[1]))
franjaFin1 = datetime.time(
    int(BANDEND[0].split(':')[0]), int(BANDEND[0].split(':')[1]))
franjaFin2 = datetime.time(
    int(BANDEND[1].split(':')[0]), int(BANDEND[1].split(':')[1]))
franjaFin3 = datetime.time(
    int(BANDEND[2].split(':')[0]), int(BANDEND[2].split(':')[1]))


def diff_times_in_seconds(t1, t2):
    # Diff of two times in seconds
    h1, m1, s1 = t1.hour, t1.minute, t1.second
    h2, m2, s2 = t2.hour, t2.minute, t2.second
    t1_secs = s1 + 60 * (m1 + 60*h1)
    t2_secs = s2 + 60 * (m2 + 60*h2)
    return (t2_secs - t1_secs)


# Cost per second

costweekband1 = weekband1/3600
costweekband2 = weekband2/3600
costweekband3 = weekband3/3600
costweekendband1 = weekendband1/3600
costweekendband2 = weekendband2/3600
costweekendband3 = weekendband3/3600

# Class definition SWITCH


class switch:

    def __init__(self, variable, comparator=None, strict=False):
        self.variable = variable
        self.matched = False
        self.matching = False
        if comparator:
            self.comparator = comparator
        else:
            self.comparator = lambda x, y: x == y
        self.strict = strict

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def case(self, expr, break_=False):
        if self.strict:
            if self.matched:
                return False
        if self.matching or self.comparator(self.variable, expr):
            if not break_:
                self.matching = True
            else:
                self.matched = True
                self.matching = False
            return True
        else:
            return False

    def default(self):
        return not self.matched and not self.matching


def costWeek(type, startHour, endHour):

    # Cost calculation between week

    with switch(type) as s:
        if s.case(1, True):
            return (diff_times_in_seconds(startHour, endHour)*costweekband1)
        if s.case(2, True):
            return (diff_times_in_seconds(startHour, endHour)*costweekband2)
        if s.case(3, True):
            return (diff_times_in_seconds(startHour, endHour)*costweekband3)
        if s.case(4, True):
            return ((diff_times_in_seconds(startHour, franjaFin1)*costweekband1)+(diff_times_in_seconds(franjaFin1, endHour)*costweekband2))
        if s.case(5, True):
            return ((diff_times_in_seconds(startHour, franjaFin2)*costweekband2)+(diff_times_in_seconds(franjaFin2, endHour)*costweekband3))
        if s.case(6, True):
            return ((diff_times_in_seconds(startHour, franjaFin1)*costweekband1) +
                    (diff_times_in_seconds(franjaFin1, franjaFin2)*costweekband2) +
                    (diff_times_in_seconds(franjaFin2, endHour)*costweekband3))
        if s.default():
            return ("Case not found")


def costWeekEnd(type, startHour, endHour):

    # Cost calculation between weekend

    with switch(type) as s:
        if s.case(1, True):
            return (diff_times_in_seconds(startHour, endHour)*costweekendband1)
        if s.case(2, True):
            return (diff_times_in_seconds(startHour, endHour)*costweekendband2)
        if s.case(3, True):
            return (diff_times_in_seconds(startHour, endHour)*costweekendband3)
        if s.case(4, True):
            return ((diff_times_in_seconds(startHour, franjaFin1)*costweekendband1)+(diff_times_in_seconds(franjaFin1, endHour)*costweekendband2))
        if s.case(5, True):
            return ((diff_times_in_seconds(startHour, franjaFin2)*costweekendband2)+(diff_times_in_seconds(franjaFin2, endHour)*costweekendband3))
        if s.case(6, True):
            return ((diff_times_in_seconds(startHour, franjaFin1)*costweekendband1) +
                    (diff_times_in_seconds(franjaFin1, franjaFin2)*costweekendband2) +
                    (diff_times_in_seconds(franjaFin2, endHour)*costweekendband3))
        if s.default():
            return ("Case not found")

# Set case cost


def tipo(setStartHour, setEndHour):

    if setStartHour >= franjaInc1 and setEndHour <= franjaFin1:
        return 1
    elif setStartHour >= franjaInc2 and setEndHour <= franjaFin2:
        return 2
    elif setStartHour >= franjaInc3 and setEndHour <= franjaFin3:
        return 3
    elif setStartHour >= franjaInc1 and setEndHour > franjaFin1 and setEndHour <= franjaFin2:
        return 4
    elif setStartHour >= franjaInc2 and setEndHour > franjaFin2 and setEndHour <= franjaFin3:
        return 5
    elif setStartHour >= franjaInc1 and setEndHour > franjaFin2 and setEndHour <= franjaFin3:
        return 6
    else:
        return 0

# Main execution


def main():

    RENE = "MO10:00-12:00,TU10:00-12:00,TH01:00-03:00,SA14:00-18:00,SU20:00-21:00"
    schedule = RENE.split(',')

    totalCost = 0

    # Selecting the case
    print("Press 1 for RENE")
    print("Press 2 for ASTRID")
    print("Press 3 for CUSTOM")
    input1 = input()

    if input1 == "1":
        RENE = "MO10:00-12:00,TU10:00-12:00,TH01:00-03:00,SA14:00-18:00,SU20:00-21:00"
        schedule = RENE.split(',')
    elif input1 == "2":
        ASTRID = "MO10:00-12:00,TH12:00-14:00,SU20:00-21:00"
        schedule = ASTRID.split(',')
    elif input1 == "3":
        print("Enter your schedule colon separated ex. SA14:00-18:00,SU20:00-21:00n3: ")
        input2 = input()
        CUSTOM = input2
        schedule = CUSTOM.split(',')
    else:
        print("Not valid option")
        exit()

    os.system('clear')
    print()
    print()
    print("----Staring cost calc ---")
    print()

    try:

        # Calculating the cost

        for x in schedule:

            # Extracting the variables from string

            day = re.search('^(.+?)\d', x).group(1)
            start = re.search('^[A-Z]{2}(.+?)-', x).group(1)
            end = re.search('-(.+?)$', x).group(1)
            print('Day: '+day)
            print('Start: '+start)
            print('End: '+end)

            # Setting up the start time and end time

            startHour = datetime.time(
                int(start.split(':')[0]), int(start.split(':')[1]))
            endHour = datetime.time(
                int(end.split(':')[0]), int(end.split(':')[1]))
            print("Start hour: ", startHour)
            print("End hour: ", endHour)

            # Selecting week calc or weekend calc
            typeCalc = tipo(startHour, endHour)

            if day == "SA" or day == "SU":
                partialCost = costWeekEnd(typeCalc, startHour, endHour)
                print("Partial cost: ", partialCost)
                totalCost = totalCost+partialCost
            else:
                partialCost = costWeek(typeCalc, startHour, endHour)
                print("Partial cost: ", partialCost)
                totalCost = totalCost+partialCost
            print("---------------------------")

        # Printing the outcome
        print("Total cost: ", totalCost)
        print()
        print()

    except AttributeError:
        pass


main()
