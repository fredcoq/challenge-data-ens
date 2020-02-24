from datetime import datetime, date, timedelta
import pytz
import pandas as pd
import sys
import re


class holydays:
    """
    This class check if a date is a french day off or a work day
    by default, pentecôte is a working day
    """
    format = ""
    my_date = None
    my_df = None

    workdays = None
    daysoff = None
    prophet_df = None

    def __init__(self, Dataframe=None, date=None, pentecote=False, extradayoff=False):
        r"""
        constructor
        :param Dataframe (Dataframe, optional):
        :param date (string, optional):
        :param pentecote (bool, optional):
        :param extradayoff (bool, optional):
        """
        self.__pentecote(pentecote)
        self.__set_extradaysoff(extradayoff)

        self.workdays = pd.DataFrame()
        self.daysoff = pd.DataFrame()

        if (date != None):
            self.__date(date)

        if Dataframe is not None:
            self.Dataframe(Dataframe)

    def __date(self, x):
        try:
            datetime_object = datetime.strptime(x, '%d/%m/%Y')
            self.my_date = datetime_object
        except Exception:
            try:
                datetime_object = datetime.strptime(x, '%d/%m/%Y %H:%M')
                self.my_date = datetime_object
            except Exception:
                try:
                    datetime_object = datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
                    self.my_date = datetime_object
                except Exception:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise

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

        pentecote = ""

        if self.pentecoteoff:
            pentecote = self.date_paques + timedelta(50)

        self.pentecote = pentecote

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

    def Dataframe(self, df):
        r"""
        setting DataFrame
        :param df (DataFrame): DataFrame to split
        """
        self.format = "%m/%d/%Y %H:%M"
        if isinstance(df, pd.DataFrame):
            self.my_df = df.copy()
            self.prophet_df = self.my_df.copy()

            if isinstance(df.index, pd.DatetimeIndex):
                self.format = "%Y-%m-d% H%:M%:S%"
                self.split()

            elif isinstance(df.index, pd.RangeIndex):
                print(
                    """
                    you must change your RangeIndex in a DatetimeIndex 
                    df['datetime'] = pd.to_datetime(df['date'])
                    df = df.set_index('datetime')
                    df.drop(['date'], axis=1, inplace=True)
                    after it's done, you can run the method split()
                    """
                )
            else:
                print(
                    """
                    if your dataframe index is in date type, you can run the method split() or prophet()
                    """
                )
        else:
            raise ValueError('{df} not a pandas dataframe')

    def split(self):
        """
        Split the DataFrame into 2 separate DataFrames : business days and public holydays
        """
        list_date = self.my_df.index.tolist()
        for d in list_date:
            if isinstance(d, datetime):
                new_date = datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
                self.__date(new_date.strftime("%d/%m/%Y %H:%M:%S"))
            else:
                self.__date(d)

            if self.__workday():
                self.my_df.at[d, 'workday'] = 1
            else:
                self.my_df.at[d, 'workday'] = 0

        self.workdays = self.my_df.loc[self.my_df.workday == 1, self.my_df.columns != 'workday']
        self.daysoff = self.my_df.loc[self.my_df.workday == 0, self.my_df.columns != 'workday']

    def prophet(self):
        """
        Generate Prophet DataFrame with on_work / off_work column
        :return DataFrame:
        """
        self.prophet_df = self.prophet_df.join(pd.DataFrame(
            {
                'on_work': False,
                'off_work': False
            }, index=self.prophet_df.index
        ))

        list_date = self.prophet_df.index.tolist()

        for d in list_date:
            if isinstance(d, datetime):
                new_date = datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
                self.__date(new_date.strftime("%d/%m/%Y %H:%M:%S"))
            else:
                self.__date(d)

            if self.__workday():
                self.prophet_df.at[d, 'on_work'] = True
            else:
                self.prophet_df.at[d, 'off_work'] = True

        return self.prophet_df

    def business_days(self):
        """
        split with business days
        :return (DataFrame):
        """
        return self.workdays

    def public_holiday(self):
        """
        split with public holydays
        :return (DataFrame):
        """
        return self.daysoff


class summer_winter_time:
    """
        This class split a dataframe into two dataframes according to summer time or winter time
    """
    my_df = None
    winter = None
    summer = None

    utc = pytz.utc
    paris = pytz.timezone('Europe/Paris')

    def __init__(self, DataFrame):
        """
        Constructor
        :param DataFrame (DataFrame):
        """
        if isinstance(DataFrame, pd.DataFrame):
            self.my_df = DataFrame.copy()
            self.winter = pd.DataFrame()
            self.summer = pd.DataFrame()
            self.__generate_prophet(DataFrame)
            self.__split()
        else:
            raise ValueError('{df} not a pandas dataframe')

    def __split(self):
        if isinstance(self.my_df.index, pd.DatetimeIndex):
            list_date = self.my_df.index.tolist()
            for d in list_date:
                self.my_df.at[d, 'time'] = self.__time_zone(d).hour
        else:
            for index, row in self.my_df.iterrows():
                self.my_df.at[index, 'time'] = self.__time_zone(index).hour

        self.winter = self.my_df.loc[self.my_df.time == 1, self.my_df.columns != 'time']
        self.summer = self.my_df.loc[self.my_df.time == 2, self.my_df.columns != 'time']

    def __time_zone(self, str_date):
        date_obj = self.utc.localize(str_date, is_dst=None).astimezone(self.paris)
        matches = re.match(r"(\d{4}-\d{2}-\d{2}).(\d{2}:\d{2}:\d{2}).(\d{2}\d{2})",
                           date_obj.strftime("%Y-%m-%d %H:%M:%S%z"))
        time_object = datetime.strptime(matches.groups()[2], '%H%M').time()
        return time_object

    def __generate_prophet(self, prophet_df):
        self.prophet_df = prophet_df.join(pd.DataFrame(
            {
                'winter': False,
                'summer': False
            }, index=prophet_df.index
        ))

        if isinstance(self.prophet_df.index, pd.DatetimeIndex):
            list_date = self.prophet_df.index.tolist()
            for d in list_date:
                if self.__time_zone(d).hour == 1:
                    self.prophet_df.at[d, 'winter'] = True
                else:
                    self.prophet_df.at[d, 'summer'] = True
        else:
            for index, row in self.my_df.iterrows():
                if self.__time_zone(index).hour == 1:
                    self.prophet_df.at[index, 'winter'] = True
                else:
                    self.prophet_df.at[index, 'summer'] = True

    def winter_time(self):
        """
        split with winter time
        :return (DataFrame):
        """
        return self.winter

    def summer_time(self):
        """
        split with summer time
        :return (DataFrame):
        """
        return self.summer

    def prophet(self):
        """
        Dataframe for Prophet with summer / winter columns
        :return (DataFrame):
        """
        return self.prophet_df

def generate_prophet_dataframe(DataFrame, pentecote=False, extradayoff=False):
    """
    Generate Prophet DataFrame with on_work / off_work and summer / winter columns
    :param DataFrame (DataFrame): pandas Dataframe
    :param pentecote (bool, optional): True if Pentecote must be day off False if it's a business day
    :param extradayoff (bool, optional): True if monday before a public holyday or friday after a public holyday is day off False if it's a business day
    :return (DataFrame):
    """

    if isinstance(DataFrame, pd.DataFrame):
        return holydays(summer_winter_time(DataFrame).prophet(), pentecote=pentecote, extradayoff=extradayoff).prophet()
    else:
        raise ValueError('{df} not a pandas dataframe')


def to_cet(df):
    """
    Replace UTC index into CET index
    :param df (Dataframe):
    :return Dataframe:
    """
    if isinstance(df, pd.DataFrame):
        utc = pytz.utc
        paris = pytz.timezone('Europe/Paris')

        if isinstance(df.index, pd.DatetimeIndex):
            list_date = df.index.tolist()
            for d in list_date:
                date_obj = utc.localize(d, is_dst=None).astimezone(paris)
                df.at[d, 'Date'] = datetime(date_obj.year, date_obj.month, date_obj.day, date_obj.hour, date_obj.minute,
                                            date_obj.second)
        else:
            for index, row in df.iterrows():
                date_obj = utc.localize(index, is_dst=None).astimezone(paris)
                df.at[index, 'Date'] = datetime(date_obj.year, date_obj.month, date_obj.day, date_obj.hour,
                                                date_obj.minute,
                                                date_obj.second)

        df.reset_index(inplace=True)
        df.set_index('Date', inplace=True)

        return df
    else:
        raise ValueError('{df} not a pandas dataframe')