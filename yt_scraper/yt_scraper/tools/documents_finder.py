from pymongo import MongoClient

#Class that contains various methods for getting documents from the database.
class DocumentsFinder:

    myClient = MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false") 
    db = myClient['greek-socialmedia-businesses']
    collection=db['youtube-businesses-toscrape']


    #Finds documents using filter, project, skip and limit
    def findDocumentsWithProjSkipLim(self, filter, project, skip_num, limit_num):
        return self.collection.find(filter, project).skip(skip_num).limit(limit_num)


    #Finds documents using filter, skip and limit
    def findDocumentsWithSkipLim(self, filter, skip_num, limit_num):
        return self.collection.find(filter).skip(skip_num).limit(limit_num)


    #Finds documents using filter, project and skip
    def findDocumentsWithProjSkip(self, filter, project, skip_num):
        return self.collection.find(filter, project).skip(skip_num)


    #Finds documents using filter and skip
    def findDocumentsWithSkip(self, filter, skip_num):
        return self.collection.find(filter).skip(skip_num)


    #Finds documents using filter, project and limit
    def findDocumentsWithProjLim(self, filter, project, limit_num):
        return self.collection.find(filter, project).limit(limit_num)


    #Finds documents using filter and limit
    def findDocumentsWithLim(self, filter, limit_num):
        return self.collection.find(filter).limit(limit_num)

    #Finds documents using filter
    def findDocuments(self, filter):
        return self.collection.find(filter)