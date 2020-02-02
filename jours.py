from datetime import datetime, date, timedelta
import pandas as pd
import sys

class holydays :
    """
    This class check if a date is a french day off or a work day
    by default, pentecôte is a working day
    """
    format = ""
    my_date = None
    my_df = None

    workdays = None
    daysoff = None

    def __init__(self, x=None) :
        self.pentecote()
        self.workdays = pd.DataFrame()
        self.daysoff = pd.DataFrame()

        if (x != None):
            self.setDate(x)

    def Dataframe(self, df):
        self.format = "%m/%d/%Y %H:%M"
        if isinstance(df, pd.DataFrame):
            self.my_df = df
        else:
            raise ValueError('{df} not a pandas dataframe')

        if isinstance(df.index, pd.DatetimeIndex):
            self.format = "%Y-%m-d% H%:M%:S%"
            self.split()
        elif isinstance(df.index, pd.RangeIndex) :
            print(
                """
                you must change your RangeIndex in a DatetimeIndex 
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.set_index('datetime')
                df.drop(['date'], axis=1, inplace=True)
                after it's done, you can run the method dfSplit()
                """
            )
        else:
            print(
                """
                if your dataframe index is in date type, you can run the method dfSplit()
                """
            )

    def date(self, x):
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

    def pentecote(self, dayoff=False):
        self.pentecote = dayoff


    def paques(self):
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

    def workday(self):
        return False if (self.weekend() | self.holyday()) else True

    def weekend(self):
        return True if (self.my_date.weekday() == 5 | self.my_date.weekday() == 6) else False

    def holyday(self):
        a = self.my_date.year
        (m, j) = self.paques()  # Dimanche de Pâques
        date_paques = date(a, m, j)

        jour_an = date(a, 1, 1)
        fete_travail = date(a, 5, 1)
        victoire = date(a, 5, 8)
        fete_nationale = date(a, 7, 14)
        assomption = date(a, 8, 15)
        toussain = date(a, 11, 1)
        armistice = date(a, 11, 11)
        noel = date(a, 12, 25)
        lundi_paques = date_paques + timedelta(1)
        ascension = date_paques + timedelta(39)
        pentecote = ""

        if self.pentecote :
            pentecote = date_paques + timedelta(50)

        my_date = date(a, self.my_date.month, self.my_date.day)

        if ((my_date == jour_an) | (my_date == fete_travail) | (my_date == victoire) | (
                my_date == fete_nationale) | (my_date == assomption)
                | (my_date == toussain) | (my_date == armistice) | (my_date == noel) | (
                        my_date == lundi_paques) | (my_date == ascension) | (my_date == pentecote)):
            return True
        else:
            return False

    def split(self):
        list_date = self.my_df.index.tolist()
        for d in list_date :
            if isinstance(d, datetime) :
                new_date = datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
                self.date(new_date.strftime("%d/%m/%Y %H:%M:%S"))
            else :
                self.date(d)

            if self.workday() :
                self.my_df.at[d, 'workday'] = 1
            else:
                self.my_df.at[d, 'workday'] = 0

        self.workdays = self.my_df.loc[self.my_df.workday == 1, :]
        self.daysoff = self.my_df.loc[self.my_df.workday == 0, :]

    def business_days(self):
        return self.workdays

    def public_holiday(self):
        return self.daysoff