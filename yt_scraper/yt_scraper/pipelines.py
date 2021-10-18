# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class DatabasePipeline:

    myClient=MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
    db=myClient['Thesis']
    collection=db['YouTubeChannels']

    def process_item(self, item, spider):
        channel_id = item['channel_data']['id']

        self.collection.replace_one(
            {'channel_data.id': channel_id},
            item, upsert = True)
