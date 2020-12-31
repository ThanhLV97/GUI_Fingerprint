from pymongo import MongoClient
import os
import sys
"""
    Config key for dbs model
"""
class Key(Novalue):
    id  = '_id'
    pos = 'pos'
    name = 'name'
    fingertemp = 'fingertemp'



"""
    Module to manage Mongodb database.
    Check and synchronize finger print and recognition userdata
"""
class DataManage():
    def __init__(self):
        self.client = MongoClient("mongodb+srv://thanh15dt2:thanh15dt2@cluster0.kxtts.mongodb.net/cluster0?retryWres=true&w=majority")
        self.dbs = self.client.loggingface


    def check_finger(self, id):
        """
            Check id is saved or not in finger collection  

        args:
            name(str): Staffname 
        return:
            data(json): Staff infomation if name has been in db 
            None: New staff 
        """

        finger_dbs = self.dbs.fingerprint.find()
        for data in finger_dbs:
            if data['_id'] == id:
                return True, data
        return False, None

    def check_user(self, id):
        """
            TODO
        """
        user_dbs = self.dbs.user.find()
        for user_info in user_dbs:
            if user_info['_id'] == id:
                return True, user_info
        return False, None

    def _check_info(self, id):
        """
            TODO
        """
        # Check user id
        user_status, user_info = self.check_user(id)
        # Check finger id
        finger_status, finger_info = self.check_finger(id)
        # Synchronize
        if finger_status is False and user_status is False:
            status = {'finger': None, 'finger_info': finger_info,
                      'user': None, 'user_info': user_info}

        elif finger_status is False and user_status is True:
            status = {'finger': None, 'finger_info': finger_info,
                      'user': True, 'user_info': user_info}

        elif finger_status is True and user_status is False:
            status = {'finger': None, 'finger_info': finger_info,
                      'user': True, 'user_info': user_info}

        else:
            status = {'finger': True, 'finger_info': finger_info,
                      'user': True, 'user_info': user_info}

        return status


    def push_data(self, status, id, position_number, name, template):
        """ 
            Push or update userdata into dbs
        args:
            id(int): Staff ID
            positionNumber(int): index in memory of fingerprint
            name(str): Staff name
            template(str): staff sha template
        """

        if status is True:
            self.dbs.fingerprint.update_one(
                {'_id': id},
                { '$push': {'positionNumber': position_number}}
            )

            self.dbs.fingerprint.update_one(
                {'_id':id},
                { '$push': {'fingertemp': template}}
            )

            res = {'status': 'ok', 'massage': 'Update data successfully'}

        else:
            self.dbs.fingerprint.insert_one({
                '_id':id,
                'positionNumber': [position_number],
                'name': name,
                'fingertemp': [template]
            })
            res = {'status': 'ok', 'message': 'new Push data successfully'}

        return res

    def get_info(self, id, key):
        """
            Find data in database
        Return :
            data: value of key provided 
        """
        database = self.dbs.fingerprint.find()
        data = [data[key] for data in database]
        return data[0]
