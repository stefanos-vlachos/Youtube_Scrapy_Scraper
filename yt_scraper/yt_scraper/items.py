# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ChannelItem(scrapy.Item):
    channel_data = scrapy.Field()
    videos = scrapy.Field()
    
class ChannelData(scrapy.Item):
    title = scrapy.Field()
    id = scrapy.Field()
    creation_date = scrapy.Field()
    view_count = scrapy.Field()
    subscriber_count = scrapy.Field()
    video_count = scrapy.Field()
    keywords = scrapy.Field()
    owned_by = scrapy.Field()

class VideoData(scrapy.Item):
    video_id = scrapy.Field()
    title = scrapy.Field()
    upload_date = scrapy.Field()
    duration = scrapy.Field()
    view_count = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    comment_count = scrapy.Field()
    video_category = scrapy.Field()
    tags = scrapy.Field()