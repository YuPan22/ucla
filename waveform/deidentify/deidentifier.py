import os
import pandas
from datetime import datetime

class Deidentifier():
    dict = {}

    def __init__(self):
        #self.create_dictionary()
        self.create_dictionary_edwards_one_month()

    @staticmethod
    def days_between(day1, day2):
        d1 = datetime
        d2 = datetime
        day1 = day1.strip()
        day2 = day2.strip()
        try:
            d1 = datetime.strptime(day1, "%m/%d/%Y")
        except:
            try:
                d1 = datetime.strptime(day1, "%Y-%m-%d")
            except:
                d1 = datetime.strptime(day1, "%Y%m%d")

        try:
            d2 = datetime.strptime(day2, "%m/%d/%Y")
        except:
            try:
                d2 = datetime.strptime(day2, "%Y-%m-%d")
            except:
                d2 = datetime.strptime(day2, "%Y%m%d")

        return abs((d2 - d1).days)

    @staticmethod
    def get_sequence(date_to_mask, dob, mask):
        return str(Deidentifier.days_between(dob, date_to_mask) + mask)


    def create_dictionary(self):
        #for _, row in pandas.read_csv(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deidentify', 'deidentify.csv')).iterrows():
        for _, row in pandas.read_csv(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deidentify.csv')).iterrows():
            Deidentifier.dict[row['stpfilename'].strip().replace(' ','_').split('.')[0]] = {'DateofBirth': row['DateofBirth'], 'BaseDateNumber': row['BaseDateNumber'], 'studyid': str(row['studyid']), 'encounterid': str(row['encounterid'])}

    def create_dictionary_edwards_one_month(self):
        for _, row in pandas.read_csv(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deidentify_edwards_one_month.csv')).iterrows():
            Deidentifier.dict[row['stpfilename'].strip().replace(' ','_').split('.')[0]] = {'studyid': str(row['studyid']), 'encounterid': str(row['encounterid'])}


    @staticmethod
    def query_dictionary(stp_filename, field):
        #return Deidentifier.dict[stp_filename].get(field)

        def normalize_stpfilename_as_dict_key(stp_filename):
            sp = stp_filename.strip().split('.')[0].replace(' ', '_').split('-')
            norm = sp[0] + '-' + sp[1].split('_')[0]
            return norm

        return Deidentifier.dict[normalize_stpfilename_as_dict_key(stp_filename)].get(field)
