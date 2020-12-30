from pymongo import MongoClient
"""
    Module to manage Mongodb database.
    Check and synchronize finger print and recognition userdata
"""
class DataManage():
    def __init__(self):
        self.client = MongoClient("mongodb+srv://thanh15dt2:thanh15dt2\
                        @cluster0.kxtts.mongodb.net/cluster0?retryWres=true&w=majority")
        self.dbs = self.client.loggingface


    def sync_name(self, name):
        """
            Check name in mongodb database
        
        args:
            name(str): staffname 

        return:
            data(json): Staff infomation if name has been in db 
            None: New staff 
        """

        finger_dbs = self.dbs.fingerprint.find(
        for data in finger_dbs:
            if data['staffname'] == name:
                return data
        return None

    def push_data(self, id, positionNumber, name, template):
        """
            Push userdata into dbs
        args:
            id(int): Staff ID
            positionNumber(int): index in memory of fingerprint
            name(str): Staff name
            template(str): staff sha template
        """
        push_status = self.db.fingerprint.insert_one(
            {   
                '_id': id,
                'positionNumber': positionNumber,
                'name': name,
                'fingertemp': template
            }
        )
        return push_status
