import os
import json
from .documents_finder import DocumentsFinder

class ResourcesImporter:

    #Resources folder directory
    resources_dir = os.path.abspath(os.curdir) + "\\resources"


    #Imports channel credentials from JSON File
    def importChannelsFromJSON(self, channels_to_scrape):
        file_directory = self.resources_dir + "\\BusinessChannels.json"
        with open(file_directory, encoding='utf8') as json_file:
            data = json.load(json_file)
            for channel in data["Channels"]:
                channels_to_scrape.append(channel["Id"])


    #Imports channel credentials from database
    #Use the appropriate find method for your needs
    def importChannelsFromDatabase(self):
        return list(DocumentsFinder.findDocuments(DocumentsFinder, {}))


    #Imports API keys from JSON file
    def importAPIKeys(self):
        API_keys = {}
        API_keys_file = self.resources_dir + "\\APIkeys.json"
        with open(API_keys_file, encoding='utf8') as json_file:
            data = json.load(json_file)
            for key in data["Keys"]:
                API_keys[key["Id"]]="active"
        return API_keys


    #Imports Video Categories from JSON file
    def importVideoCategories(self):
        video_categories_file = self.resources_dir + "\\CategoryIDs.json"
        with open(video_categories_file, encoding='utf8') as json_file:
            return json.load(json_file)