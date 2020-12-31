import logging
import os
import time
import hashlib
import csv
import pandas as pd
from .config import Finger
from .R305 import PyFingerprint
from pymongo import MongoClient
from .db_manage import DataManage, Key


"""R305 fingerprint sensor for raspberry pi 4"""
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
        self.message = {'code': 'None', 'message': ''}
        self.db_path = './data/database.csv'
        self.database = DataManage()


        """Manager R305 services
        """

        try:
            self.f = PyFingerprint(self.port, self.baudRate,
                                   self.address, self.password)

            if (self.f.verifyPassword() is False):
                raise ValueError('The given fingerprint sensor password is wrong !')

        except Exception as e:
            logging.error('The fingerprint sensor could not be initialized!')
            logging.error('Exception message: ' + str(e))
            exit(1)

        self.status = False


    def enroll(self):
        """
            Enrolling template for new staff.
        
        Return:
            positionNumber(int): Index of template in memory
        """
        # Tries to enroll new finger

        try:
            i = 0
            pos_Numbers, temp_shas = [], []
            while i < 2:
                self.message = {'code': '100', 'status': 'begin',
                                'message': 'Please give template simple'}

                # Wait that finger is read
                while (self.f.readImage() is False):
                    self.message = {'code': '102', 'status': 'waiting',
                                    'massage': 'Waiting for template simple'}
                    pass

                # Converts read image to characteristics
                # and stores it in charbuffer 1
                self.f.convertImage(Finger.CHARBUFFER1)
                # Checks if finger is already enroll
                result = self.f.searchTemplate()
                positionNumber = result[0]

                if (positionNumber >= 0):
                    self.message = {'code': '200', 'status': 'registed',
                                    'message': 'You has been registered'}
                    logging.info('Template already exists at position #' +
                                str(positionNumber))
                    i += 1

                else:
                    self.message = {'code': '102', 'status': 'processing',
                                    'message': 'Processing .....'}
                    logging.info('Proccessing...')
                    time.sleep(2)

                    logging.info('Waiting for same finger again...')
                    self.message = {'code': '102', 'status': 'waiting',
                                    'message': 'Please try again ......'}
                    # Wait that finger is read again
                    while (self.f.readImage() is False):
                        pass

                    # Converts read image to characteristics
                    # and stores it in charbuffer 2
                    self.f.convertImage(Finger.CHARBUFFER2)

                    # Compares the charbuffers
                    if (self.f.compareCharacteristics() == 0):
                        self.message = {'code': '401', 'status': 'processing',
                                        'message': 'Not match '}

                    else:
                        # Creates a template
                        self.f.createTemplate()
                        # Saves template at new position number
                        positionNumber = self.f.storeTemplate()
                        # Downloads the characteristics of template loaded in charbuffer
                        characteris = str(self.f.downloadCharacteristics(
                                            Finger.CHARBUFFER1)).encode('utf-8')
                        # Hashes characteristics of template
                        temp_sha = hashlib.sha256(characteris).hexdigest()
                        pos_Numbers.append(positionNumber)
                        temp_shas.append(temp_sha)
                        i += 1

                return pos_Numbers, temp_shas
        except Exception as e:
            logging.error('Operation failed!')
            logging.error('Exception message: ' + str(e))
            self.message = {'code': '404', 'status': 'ERROR',
                            'message': str(e)}
            exit(1)


    def remove_template(self, id):

        """Remove template and username in database

        Args:
            name (String): Username

        """
        pos = self.database.get_info(id, Key.pos)
        for i in pos:
        
            
            logging.info('Currently used templates: ' +
                        str(self.f.getTemplateCount()) + '/' +
                        str(self.f.getStorageCapacity()))

            try:
                positionNumber = i
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

            logging.info('Waiting for template...')
            self.message = {'code': '102', 'status': 'waiting',
                            'message': 'Waiting for template...'}

            # Wait that finger is read
            # Serial read in __readPacket

            while (self.f.readImage() is False):
                pass
            self.message = {'code': '102', 'status': 'received',
                            'message': 'Get template successfully'}
            # Converts read image to characteristics
            # and stores it in charbuffer 1

            self.f.convertImage(Finger.CHARBUFFER1)

            # Searchs template
            result = self.f.searchTemplate()
            positionNumber = result[0]
            accuracyScore = result[1]
            if (positionNumber == -1):
                logging.info('No match found!')
                self.message = {'code': '102', 'status': 'Not found',
                                'message': 'No match found!'}

            else:
                self.message = {'code': '200', 'status': 'successfull',
                                'message': 'Register Successfully'}

                logging.info('Found template at position: \t' +
                            str(positionNumber))
                
                data = self.database.fingerprint.find({'ID':'6'})
                logging.info('data:',data)

                # Loads the found template to charbuffer 1

                self.f.loadTemplate(positionNumber, Finger.CHARBUFFER1)

                # Downloads the characteristics of template loaded in charbuffer
                characteris = str(self.f.downloadCharacteristics(
                                    Finger.CHARBUFFER1)).encode('utf-8')

                # Hashes characteristics of template
                logging.info('SHA-2 hash of template: \t' +
                            hashlib.sha256(characteris).hexdigest())

        except Exception as e:
            logging.error('Operation failed!')
            logging.error('Exception message: ' + str(e))
            self.message = {'code': '404', 'status': 'ERROR',
                            'message': str(e)}
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
                name = input('Enter your ID: ').lower()

                if name in namelist:
                    if i == 2:
                        logging.info('Try again after 5 minutes!!!')
                        time.sleep(1*100)
                        i == 0
                    logging.info('Name is registed!!!')
                    i += 1
                else:
                    if index == 0:
                        new_data = pd.DataFrame([{'Index': str(index),
                                                  'Name': str(name)}])
                        new_data.to_csv(f, index=False, header=True)
                        f.close()
                        logging.info('You is register successful!!!')
                        return name
                        break
                    else:
                        new_data = pd.DataFrame([{'Index': str(index),
                                                  'Name': str(name)}])
                        new_data.to_csv(f, index=False, header=False)
                        f.close()
                        logging.info('You is register successful!!!')
                        return name
                        break

    def _enter_info_db(self, id, name, pos, temp_sha):

        """ Get all info from UI and check and update data into mongodb.
        Args:
            id(int): User ID
            name(str): Username
            pos(int): Position template in fingerprint memory
            temp_sha(str): SHA hash code of template

        Return:
            Status(json): info about the process
        """
        self.message = {'code': 100, 'status': 'checking'}
        status, _ = self.database.check_finger(id)

        self.message = {'code': 100, 'status': 'pushing'}
        res = self.database.push_data(status, id, name, pos, temp_sha)
        self.message = {'code': 200, 'status': 'success'}

    def _delete_info(self, name):

        """ Delete info in db according to name.

        Returns:
            [int]: Return position number in database.
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


    def test_info(self, name):

        """ Delete info in db according to name

        Returns:
            [int]: Return position number in database
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
