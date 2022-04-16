from pymongo import MongoClient

class DocumentsDeleter:

    myClient = MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false") 
    db = myClient['greek-socialmedia-businesses']
    collection=db['youtube-businesses-toscrape']

    #Deletes the wanted document from the database
    def deleteDocument(self,id):
        self.collection.delete_one({"channel_data.id":id})