from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import re

class holydays:
    """
    This class check if a date is a french day off or a work day
    by default, pentecôte is a working day
    """
    format = ""
    my_date = None

    def __init__(self, str_date=None, pentecote=False, extradayoff=False):
        r"""
        constructor
        :param date (string, optional):
        :param pentecote (bool, optional):
        :param extradayoff (bool, optional):
        """
        self.__pentecote(pentecote)
        self.__set_extradaysoff(extradayoff)

        if type(str_date) == str:
            self.__date(str_date)

    def __pentecote(self, dayoff=False):
        self.pentecoteoff = dayoff

    def __set_extradaysoff(self, dayoff=False):
        self.extradaysoff = dayoff

    def __paques(self):
        """Calcul du Dimanche de Pâques par l'algorithme de Oudin
        (avec annee > 1583 : début du calendrier grégorien (Voir lien suivant)).
        (http://www.fil.univ-lille1.fr/~wegrzyno/portail/InitProg/Doc/TP/TP6/tp6.pdf)
        Autres Bibliographies intéressantes et merci à  eux créateurs et contributeurs :
        http://www.les-mathematiques.net/phorum/read.php?5,433156,page=1
        http://olravet.free.fr/AideCalendes/Paques.htm#Calcul
        http://python.jpvweb.com/mesrecettespython/doku.php?id=date_de_paques"""
        a = self.my_date.year
        g, b, c = a % 19, a + (a // 4), a // 100
        c4, e = c // 4, (8 * c + 13) // 25
        h = (19 * g + c - c4 - e + 15) % 30
        k, p, q = h // 28, (h + 1) // 13, (21 - g) // 11
        i = (k * p * q - 1) * k + h
        j1 = (b + i + 2 + c4) - c
        j2 = j1 % 7
        r = 28 + i - j2
        return ((4, r - 31) if r > 31 else (3, r))

    def __workday(self):
        self.__set_holyday()
        return False if ((self.__extra_days_off() & self.extradaysoff) | self.__weekend() | self.__holyday(
            date(self.my_date.year, self.my_date.month, self.my_date.day))) else True

    def __weekend(self):
        return True if ((self.my_date.weekday() == 5) | (self.my_date.weekday() == 6)) else False

    def __set_holyday(self):
        a = self.my_date.year
        (m, j) = self.__paques()  # Dimanche de Pâques
        self.date_paques = date(a, m, j)

        self.jour_an = date(a, 1, 1)
        self.fete_travail = date(a, 5, 1)
        self.victoire = date(a, 5, 8)
        self.fete_nationale = date(a, 7, 14)
        self.assomption = date(a, 8, 15)
        self.toussain = date(a, 11, 1)
        self.armistice = date(a, 11, 11)
        self.noel = date(a, 12, 25)
        self.lundi_paques = self.date_paques + timedelta(1)
        self.ascension = self.date_paques + timedelta(39)

        self.holyday = {'new year': self.jour_an, 'pâques (sunday)': self.date_paques, 'pâques (monday)': self.lundi_paques, '1st may': self.fete_travail, 'victory': self.victoire, 'ascension': self.ascension}

        pentecote = ""

        if self.pentecoteoff:
            pentecote = self.date_paques + timedelta(50)
            self.holyday.update({'pentecote': pentecote})

        self.pentecote = pentecote

        self.holyday.update({'national day': self.fete_nationale, 'assomption': self.assomption, 'toussain': self.toussain, 'armistice': self.armistice, 'noel': self.noel})


    def __holyday(self, my_date):
        if ((my_date == self.jour_an) | (my_date == self.fete_travail) | (my_date == self.victoire) | (
                my_date == self.fete_nationale) | (my_date == self.assomption)
                | (my_date == self.toussain) | (my_date == self.armistice) | (my_date == self.noel) | (
                        my_date == self.lundi_paques) | (my_date == self.ascension) | (my_date == self.pentecote)):
            return True
        else:
            return False

    def __extra_days_off(self):
        today = date(self.my_date.year, self.my_date.month, self.my_date.day)

        if (
                ((today.weekday() == 0) & (self.__holyday(today + timedelta(1))))
                |
                ((today.weekday() == 4) & (self.__holyday(today - timedelta(1))))
        ):
            return True
        else:
            return False

    def __date(self, str_date):
        self.my_date = clock.datetime(str_date)

    def thisdate(self, date):
        """
        set the date
        :param date (string / datetime /timestamp):
        """
        self.__date(date)

    def holyday(self, year=None):
        """
        french holydays date dictionary
        :param year (int optional):
        :return (dictionary):
        """
        if year is not None and self.my_date is None:
            self.my_date = date(year, 1, 1)

        return self.holyday

    def is_working_day(self):
        """
        return True if date is a business day, False otherwise
        :return (boolean):
        """
        if self.my_date is not None:
            if self.__workday():
                return True
            else:
                return False
        else:
            raise ValueError('date must be provided')

class solstice:
    """
        This class check if a date is in summer time or in winter time
    """

    def __init__(self, obj_date, timeZone=None):
        r"""
        Constructor
        :param date (datetime): date in UTC
        :param timezone (str, optional): timezone by default it s on Europe/Paris
        """
        self.my_date = clock(obj_date, timeZone=timeZone)

    def is_winter(self):
        """
        return True if date is in winter, False otherwise
        :return (boolean):
        """
        if self.my_date.shift().hour == 1:
            return True
        else:
            return False

class clock:

    utc = pytz.utc
    local = pytz.timezone('Europe/Paris')
    my_date = None

    def __init__(self, date, timeZone=None):
        r"""
        Constructor
        :param date (datetime / string):
        :param timeZone (string, optional):
        """
        if timeZone is not None:
            self.local = pytz.timezone(timeZone)

        self.__date(date)

    def __date(self, date):
        date_format = ['%d.%m.%Y', '%d.%m.%Y %H:%M', '%d.%m.%Y %H:%M:%S', '%d-%m-%Y', '%d-%m-%Y %H:%M',
                       '%d-%m-%Y %H:%M:%S', '%d/%m/%Y', '%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S',
                       '%m.%d.%Y', '%m.%d.%Y %H:%M', '%m.%d.%Y %H:%M:%S', '%m-%d-%Y', '%m-%d-%Y %H:%M',
                       '%m-%d-%Y %H:%M:%S', '%m/%d/%Y', '%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S',
                       '%Y.%m.%d', '%Y.%m.%d %H:%M', '%Y.%m.%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M',
                       '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S',
                       '%Y.%d.%m', '%Y.%d.%m %H:%M', '%Y.%d.%m %H:%M:%S', '%Y-%d-%m', '%Y-%d-%m %H:%M',
                       '%Y-%d-%m %H:%M:%S', '%Y/%d/%m', '%Y/%d/%m %H:%M', '%Y/%d/%m %H:%M:%S',
                       '%Y']

        if isinstance(date, datetime):
            self.my_date = date
        elif type(date) == str:
            for format in date_format:
                try:
                    new_date = datetime.strptime(date, format)
                    self.my_date = datetime(new_date.year, new_date.month, new_date.day, new_date.hour, new_date.minute, new_date.second)
                    break
                except ValueError as e:
                    pass
        else:
            raise ValueError('date must be a datetime')

        if isinstance(self.my_date, datetime):
            self.__time_zone()

    def __time_zone(self):
        date_obj = self.utc.localize(self.my_date, is_dst=None).astimezone(self.local)
        matches = re.match(r"(\d{4}-\d{2}-\d{2}).(\d{2}:\d{2}:\d{2}).(\d{2}\d{2})",
                           date_obj.strftime("%Y-%m-%d %H:%M:%S%z"))
        self.date_object = datetime.strptime(matches.groups()[0], '%Y-%m-%d')
        self.time_object = datetime.strptime(matches.groups()[1], '%H:%M:%S').time()
        self.shift_object = datetime.strptime(matches.groups()[2], '%H%M').time()

    def time(self):
        """
        Time Object
        :return time (object datetime):
        """
        return self.time_object

    def shift(self):
        """
        Shift Object
        :return time (object datetime):
        """
        return self.shift_object

    def date(self):
        """
        date Object
        :return date (objet datetime):
        """
        return self.date_object

    def date_utc(self):
        """
        date UTC Object
        :return date (objet datetime):
        """
        return self.my_date

    @classmethod
    def datetime(cls, str_date):
        """

        :param str_date ():
        :return:
        """
        return cls(str_date).date_utc()

class special_days:

    def __init__(self):
        r"""
        constructor
        """
        self.event = {}

    def add(self, key, value):
        """
        add a entry at the event dictionary
        :param key:
        :param value:
        """
        self.event[key] = clock.datetime(value)

    def add_dict(self, **kwargs):
        """
            set a event dictionary, date events must be in string format (mm-dd-yyyy or dd/mm/yyyy or dd-mm-yyyy)
            :param kwargs: dict, event="date" (event name unique ex: world_cup_starting_date=date, world_cup_ending_date=date, etc ...)
        """

        for key, value in kwargs.items():

            if isinstance(value, list):
                key = key + '_day_'

                date_list = [clock.datetime(value[0]) - timedelta(days=x) for x in
                             range(int((clock.datetime(value[1]) - clock.datetime(value[0])).days) + 1)]

                for idx, val in enumerate(date_list):
                    idx = idx + 1
                    self.event[key + str(idx)] = val

            else:
                self.event[key] = clock.datetime(value)

    def add_list(self, *args):
        """
            set a list, date events must be in string format (mm-dd-yyyy or dd/mm/yyyy or dd-mm-yyyy)
            :param args: list, "date", "date", etc ...
        """

        for idx, value in enumerate(args):
            if isinstance(value, list):
                date_list = [clock.datetime(value[0]) - timedelta(days=x) for x in
                             range(int((clock.datetime(value[1]) - clock.datetime(value[0])).days) + 1)]
                self.event = self.event + date_list
            else:
                self.event[idx] = clock.datetime(value)

    def delete(self, key):
        """
        delete a entry at the event dictionary
        :param key:
        """
        self.event.pop(key)

    def list_event(self):
        """
        return the event dictionary
        :return (dictionary):
        """
        return self.event


class seasonalize:
    sdays_df = None
    merge = False
    mixed_columns = False
    pentecote = False
    extradayoff = False

    def __init__(self, DataFrame, **kwargs):
        r"""
        set a event dictionary or list, date events must be in string format (mm-dd-yyyy or dd/mm/yyyy or dd-mm-yyyy)
        :param args: list, "date", "date", etc ...
        :param kwargs: dict, event="date" (event name unique ex: world_cup_starting_date=date, world_cup_ending_date=date, etc ...)
        """
        if isinstance(DataFrame, pd.DataFrame):
            self.my_df = DataFrame.copy()

            self.special_days = special_days()
            dates = []

            for key, value in kwargs.items():
                if key == 'mixed_columns':
                    self.mixed_columns = value
                elif key == 'merge':
                    self.merge = value
                elif key == 'pentecote':
                    self.pentecote = value
                elif key == 'extradayoff':
                    self.extradayoff = value
                elif key == 'events':
                    self.special_days.add_dict(**value)
                else:
                    dates.append(clock.datetime(value))

            if len(dates) > 0:
                self.special_days.add_list(dates)

            self.__generate_dataset()
            self.__set_special_day()
            self.__merge_dataset()

        else:
            raise ValueError('{df} not a pandas dataframe')

    def __generate_dataset(self):
        if self.mixed_columns:
            self.__mixed_columns()
        else:
            self.__unique_columns()

    def __unique_columns(self):
        self.dataset = pd.DataFrame(
            {
                'winter': False,
                'summer': False,
                'on_work': False,
                'off_work': False
            }, index=self.my_df.index
        )

        hday = holydays(pentecote=self.pentecote, extradayoff=self.extradayoff)

        list_date = self.my_df.index.tolist()
        for d in list_date:
            hday.thisdate(d)

            if solstice(d).is_winter():
                self.dataset.at[d, 'winter'] = True
            else:
                self.dataset.at[d, 'summer'] = True

            if hday.is_working_day():
                self.dataset.at[d, 'on_work'] = True
            else:
                self.dataset.at[d, 'off_work'] = True

    def __mixed_columns(self):
        self.dataset = pd.DataFrame(
            {
                'winter_on_work': False,
                'winter_off_work': False,
                'summer_on_work': False,
                'summer_off_work': False
            }, index=self.my_df.index
        )

        hday = holydays(self.pentecote, self.extradayoff)

        list_date = self.my_df.index.tolist()
        for d in list_date:
            hday.thisdate(d)
            if solstice(d).is_winter():
                if hday.is_working_day():
                    self.dataset.at[d, 'winter_on_work'] = True
                else:
                    self.dataset.at[d, 'winter_off_work'] = True

            else:
                if hday.is_working_day():
                    self.dataset.at[d, 'summer_on_work'] = True
                else:
                    self.dataset.at[d, 'summer_off_work'] = True

    def __set_special_day(self):
        self.sdays_df = pd.DataFrame(
            {
                'special_days': False,
            }, index=self.my_df.index
        )

        self.list_event = self.special_days.list_event()

        list_date = self.my_df.index.tolist()
        for d in list_date:
            dt_event = clock.datetime(d)

            if self.event(dt_event):
                self.sdays_df.at[d, 'special_days'] = True

    def __merge_dataset(self):
        if self.merge:
            self.sdays_df = pd.merge(self.my_df, self.sdays_df, left_index=True, right_index=True)
            self.dataset = pd.merge(self.sdays_df, self.dataset, left_index=True, right_index=True)

    def event(self, date):
        """
        Check if a date is in the event dictionary
        :param date (datetime, timestamp):
        :return (boolean):
        """
        for key, value in self.list_event.items():
            if value == date:
                return True
        return False

    def events_dataset(self):
        """
        specials events dataframe
        :return (DataFrame):
        """
        return self.sdays_df

    def seasons_dataset(self):
        """
        seasonality dataframe
        :return (DataFrame):
        """
        return self.dataset