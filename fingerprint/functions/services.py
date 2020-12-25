import logging
import os
import time
import hashlib
import csv
import pandas as pd
from .config import Finger
from .R305 import PyFingerprint

"""R305 fingerprint sensor for raspbbery pi 4"""
__author__ = "Thanhlv"
__version__ = "0.1.0"
__date__ = "2020-Dec-17"
__maintainer__ = "Thanhlv"
__email__ = "thanhlv@d-soft.com.vn"
__status__ = "Development"

logging.basicConfig(format='[%(levelname)s] - %(message)s', level=logging.INFO)


class FingerPrint():

    def __init__(self, port='/dev/ttyS0', baudRate=57600,
                 address=0xFFFFFFFF, password=0x00000000):

        self.port = port
        self.baudRate = baudRate
        self.address = address
        self.password = password
        self.message = {'code':'None', 'message':''}
        self.db_path = './data/database.csv'



        """Manager R305 services
        """

        try:
            self.f = PyFingerprint(self.port, self.baudRate,
                                   self.address, self.password)

            if (self.f.verifyPassword() is False):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            logging.error('The fingerprint sensor could not be initialized!')
            logging.error('Exception message: ' + str(e))
            exit(1)

        self.status = False


    def enroll(self):
        """
            Enrolling template for new staff.
        """
        # Tries to enroll new finger
        try:
            self.message = {'code':'100', 'message':'Please give template simple'}
            
            # Wait that finger is read
            while (self.f.readImage() is False):
                self.message = {'code':'101', 'massage':'Waiting for template simple'}
                pass
            
            # Converts read image to characteristics
            # and stores it in charbuffer 1
            self.f.convertImage(Finger.CHARBUFFER1)
            # Checks if finger is already enrolled
            result = self.f.searchTemplate()
            positionNumber = result[0]

            if (positionNumber >= 0):
                self.message = {'code':'200', 'message':'You has been registered'}
                logging.info('Template already exists at position #' +
                             str(positionNumber))
                res = {'code': '200', 'status': '',
                       'message': 'Registered'}
                return res
                exit(0)
            self.message = {'code':'101', 'message':'Processing .....'}
            logging.info('Proccessing...')
            time.sleep(2)

            logging.info('Waiting for same finger again...')
            self.message = {'code':'102', 'message':'Please try again ......'}
            # Wait that finger is read again
            while (self.f.readImage() is False):
                pass

            # Converts read image to characteristics
            # and stores it in charbuffer 2
            self.f.convertImage(Finger.CHARBUFFER2)

            # Compares the charbuffers
            if (self.f.compareCharacteristics() == 0):
                self.message = {'code':'401', ' message':'Not matching '}
                res = {'code': '200', 'status': 'NO',
                       'message': 'Fingers do not match'}

                raise Exception('Fingers do not match')

            # Creates a template
            self.f.createTemplate()

            # Saves template at new position number
            positionNumber = self.f.storeTemplate()
            logging.info('Finger enrolled successfully!')
            logging.info('New template position #' + str(positionNumber))

            self._enter_info(positionNumber)
            message = {'code': '200', 'status': 'DONE',
                   'message': 'Finger enrolled successfully'}
            
            res = {'code': '200', 'status': 'DONE',
                   'message': 'Finger enrolled successfully'}
            return res

        except Exception as e:
            logging.error('Operation failed!')
            logging.error('Exception message: ' + str(e))
            res = {'code': '204', 'status': 'NOT',
                   'message': 'Please try again !!!'}
            return res
            exit(1)


    def remove_template_byname(self, name):

        """Remove template and username in database

        Args:
            name (String): Username
            
        """

        logging.info('Currently used templates: ' +
                     str(self.f.getTemplateCount()) + '/' +
                     str(self.f.getStorageCapacity()))
        
        position = self._delete_info(name)  # Delete infor in database

        try:
            positionNumber = position
            positionNumber = int(positionNumber)

            if (self.f.deleteTemplate(positionNumber) is True):
                print('Template deleted!')

        except Exception as e:
            logging.error('Operation failed!')
            logging.error('Exception message: ' + str(e))
            exit(1)
    def remove_template_bypos(self, position):

        """Remove template and username in database

        Args:
            name (String): Username
            
        """

        logging.info('Currently used templates: ' +
                     str(self.f.getTemplateCount()) + '/' +
                     str(self.f.getStorageCapacity()))

        try:
            positionNumber = position
            positionNumber = int(positionNumber)

            if (self.f.deleteTemplate(positionNumber) is True):
                print('Template deleted!')

        except Exception as e:
            logging.error('Operation failed!')
            logging.error('Exception message: ' + str(e))
            exit(1)

    def recognize(self):
        """
            Matching template in fingerprint and database.
        """

        try:
            logging.info('Currently used templates:\t' +
                         str(self.f.getTemplateCount()) + '/' +
                         str(self.f.getStorageCapacity()))

            # Tries to search the finger and calculate hash

            logging.info('Waiting for finger...')

            # Wait that finger is read
            # Serial read in __readPacket

            while (self.f.readImage() is False):
                pass

            # Converts read image to characteristics
            # and stores it in charbuffer 1
            self.f.convertImage(Finger.CHARBUFFER1)

            # Searchs template
            result = self.f.searchTemplate()
            positionNumber = result[0]
            accuracyScore = result[1]
            if (positionNumber == -1):
                logging.info('No match found!')

            else:
                res = {'code': '200', 'status': '200',
                       'message': 'Register Successfully'}
                logging.info('Found template at position: \t' +
                             str(positionNumber))
                # logging.info('Accuracy: \t' + str(accuracyScore))

            # Loads the found template to charbuffer 1
            self.f.loadTemplate(positionNumber, Finger.CHARBUFFER1)

            # Downloads the characteristics of template loaded in charbuffer 1
            characterics = str(
                self.f.downloadCharacteristics(
                    Finger.CHARBUFFER1)).encode('utf-8')

            # Hashes characteristics of template
            logging.info('SHA-2 hash of template: \t' +
                         hashlib.sha256(characterics).hexdigest())
            res = {'code': '200', 'status': '200',
                       'message': 'Register Successfully'}
            return res

        except Exception as e:
            logging.error('Operation failed!')
            logging.error('Exception message: ' + str(e))
            exit(1)


    def template_number(self):
        """
            Show number of templates
        """
        logging.info('Currently used templates:\t' +
                     str(self.f.getTemplateCount()) + '/' +
                     str(self.f.getStorageCapacity()))
        # Check in database
        for page in range(0, 4):
            templateIndex = self.f.getTemplateIndex(page)
            for i in range(len(templateIndex)):
                if templateIndex[i] is False:
                    # Calculate position number
                    positionNumber = len(templateIndex) * page + i
                    return positionNumber
                    break


    def _enter_info(self, index):
        """Enter member information while registering membership

        Args:
            index (int): Position available for register
        """
        namelist = []
        with open(self.db_path, 'a') as f:
            db = open(self.db_path, 'r').read()
            db1 = csv.reader(open(self.db_path, 'r'))
            for row in db1:
                namelist.append(row[1])
            # Two times checking
            for i in range(2):
                new_name = input('Enter your ID: ').lower()

                if new_name in namelist:
                    if i == 2:
                        logging.info('Try again after 5 munites!!!')
                        time.sleep(1*100)
                        break
                    logging.info('Name is registed!!!')
                    i += 1
                else:
                    if index == 0:
                        new_data = pd.DataFrame([{'Index': str(index),
                                                  'Name': str(new_name)}])
                        new_data.to_csv(f, index=False, header=True)
                        f.close()
                        logging.info('You is register successful!!!')
                        break
                    else:
                        new_data = pd.DataFrame([{'Index': str(index),
                                                  'Name': str(new_name)}])
                        new_data.to_csv(f, index=False, header=False)
                        f.close()
                        logging.info('You is register successful!!!')
                        break


    def _delete_info(self, name):

        """ Delete infor in db according to name

        Returns:
            [int]: Retrurn position number in database
        """

        logging.info('Currently used templates: ' +
                     str(self.f.getTemplateCount()) + '/' +
                     str(self.f.getStorageCapacity()))

        lines = []
        with open(self.db_path, 'r') as readfile:
            reader = csv.reader(readfile)
            for row in reader:
                if row[1] == name:
                    position = row[0]
                else:
                    lines.append(row)

        db = pd.DataFrame(lines, columns=(['Index'], ['Name']))
        with open(self.db_path, 'w') as writefile:
            db.to_csv(writefile, index=False, header=False)

        return position


    def test_infor(self, name):

        """ Delete infor in db according to name

        Returns:
            [int]: Retrurn position number in database
        """

        logging.info('Currently used templates: ' +
                     str(self.f.getTemplateCount()) + '/' +
                     str(self.f.getStorageCapacity()))

        lines = []
        with open(self.db_path, 'r') as readfile:
            reader = csv.reader(readfile)
            for row in reader:
                if row[1] == name:
                    position = row[0]
                else:
                    lines.append(row)

        db = pd.DataFrame(lines, columns=(['Index'], ['Name']))
        with open(self.db_path, 'w') as writefile:
            db.to_csv(writefile, index=False, header=False)

        return position


    def read_template(self):
        """
            Get template which using for update to database
        """

        # Serial read from sensor
        while(self.f.readImage() is False):
            pass

        self.f.convertImage(Finger.CHARBUFFER1)


    def set_password(self, new_password):
        """
            Set new password for finger print module
        Args:
            new_password(str): new password
        """

        self.f.setPassword(new_password)
