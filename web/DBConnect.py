import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()

class MongoConnect():
    """ Class to set up and manage operations with Mongo DB.
    initializing the class will connect to given DB. 
    """
    def __init__(self, database_name):
        _mongo_user = os.getenv("MONGO_USER")
        _mongo_pass = os.getenv("MONGO_PASS")
        self._connection_string = f"mongodb+srv://{_mongo_user}:{_mongo_pass}@apiproject1.hivtahc.mongodb.net/"
        self._client = MongoClient(self._connection_string, tlsCAFile=certifi.where() )

        self._db_connect = self._client[database_name]
        print(f"Connected to the DB {database_name} succesfully. ")
        print("Following collections are available: ")
        for coll in self._db_connect.list_collection_names():
            print(coll)
        self.collection = ""


    def insert_into_collection(self, collection, document):
        """ Method to Insert the document intot the Mongo Collection.
        Parameters:
            - collection [str]: name of the collection to insert to
            - document [json]: the document in the required format
        """
        self.collection = self._db_connect[collection]
        self.collection.insert_one(document)
        print(f"Inserted object and new _id is: {id}")


    def read_doc_from_collection(self, collection, condition):
        """ Method to read any one document from the given collection."""
        self.collection = self._db_connect[collection]
        document = self.collection.find_one(condition)
        return document
    
    def count_documents_per_query(self, collection, condition):
        """Returns number of found documents. """
        self.collection = self._db_connect[collection]
        document = self.collection.count_documents(condition)
        print("Number of docuemnts found: ", document)
        return document

    def read_all_sentences(self, collection, condition):
        """ Method to read all documents from the given collection."""
        self.collection = self._db_connect[collection]
        documents = self.collection.find(filter=condition,
                                         projection={'_id': 0, 'Sentence':1})
        return list(documents)

    def update_collection(self, collection, _filter, _update):
        """ Method will filter documents from the given Collection 
           and will update found document."""
        self.collection = self._db_connect[collection]
        self.collection.update_one(_filter, _update)
