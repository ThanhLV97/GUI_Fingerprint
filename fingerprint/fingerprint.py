import os
import time
from functions.services import FingerPrint
import threading
"""R305 fingerprint sensor for raspbbery pi 4"""
__author__ = "Thanhlv"
__version__ = "0.1.0"
__date__ = "2020-Dec-17"
__maintainer__ = "Thanhlv"
__email__ = "thanhlv@d-soft.com.vn"
__status__ = "Development"

"""
    Example:
        db_path = '.data/database.scv'
        FingerPrint.recognize()
        FingerPrint.enroll(db_path)
        FingerPrint.remove_template(name, db_path)
        FingerPrint.recognize()
        Fingerprint.template_number() /get number of templates in db_base
"""



Finger = FingerPrint()

def get(key, distionary):
    for k, value in distionary.items():
        if key == k:
            return value

def log():
    codelist = ['100','101', '102', '200']
    while True:

        dis = Finger.message
        print(dis)
        code = 'code'
        message = 'message'
        code = get(code, dis)
        message = get(message, dis)

        if code in codelist:
            print(message)
            break

def test_update_log():
    while True:
        Finger.enroll()

if __name__ == "__main__":

    t1 = threading.Thread(target=log)
    t2 = threading.Thread(target=test_update_log)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # for i in range(100):
    #     Finger.remove_template_bypos(i)

    # print(Finger.message)


