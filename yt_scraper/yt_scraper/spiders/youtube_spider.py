from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
import isodate
from ..items import ChannelItem
from ..items import ChannelData
from ..items import VideoData
from ..tools.documents_deleter import DocumentsDeleter
from ..tools.resources_importer import ResourcesImporter
import json

class YoutubeSpider(Spider):

    name = 'YoutubeSpider'
    allowed_domains = ['googleapis.com','youtube.com']
    youtube_url = 'https://www.googleapis.com/youtube/v3'
    subs_limit = 0
    handle_httpstatus_list = [403]
    channels_to_scrape = []
    channel_items = {}
    API_keys = {}
    video_categories = {}

    #Populate channels_to_scrape with channel IDs from json file
    #ChannelsImporter.importChannelsFromJSON(channels_to_scrape)
    #Populate channels_to_scrape with channel IDs from database
    channels_to_scrape = ResourcesImporter.importChannelsFromDatabase(ResourcesImporter)
    API_keys = ResourcesImporter.importAPIKeys(ResourcesImporter)
    video_categories = ResourcesImporter.importVideoCategories(ResourcesImporter)


    #Sends request for each channel
    def start_requests(self):
        for channel in self.channels_to_scrape:
            API_key = self.get_active_API()
            requested_url = self.get_url(channel["id"], "channel", API_key)
            yield Request(requested_url, callback=self.parse, meta={"channel_id": channel["id"], "usedAPI": API_key})


    #Receives response for each channel
    def parse(self, r):
        response = json.loads(r.text)

        #Error handling
        if "error" in response:
            #Checks if API key exceeded
            if response['error']['errors'][0]['reason'] == "quotaExceeded":
                self.handle_API_error(r.meta["channel_id"], None, r.meta["usedAPI"], "parse")
        elif "items" in response:
            #Checks if channel has public subscribers count and subs count is bigger than the limit
            if "subscriberCount" in response['items'][0]['statistics'] and int(response['items'][0]['statistics']['subscriberCount']) > self.subs_limit:
                channel_data = ChannelData()
                channel_data['id'] = response['items'][0]['id']
                channel_data['title'] = response['items'][0]['snippet']['title']

                self.channel_items.update({channel_data['id']: ChannelItem(channel_data=[], videos=[])})

                #Checks if channel has keywords
                if "keywords" in response['items'][0]['brandingSettings']['channel']:
                    keywords = response['items'][0]['brandingSettings']['channel']['keywords']
                    words = keywords.split("\"")
                    words = list(filter(lambda x: x != " ", words))
                    keywords_list = []
                    for word in words:
                        splitwords = word.split(" ")
                        if len(splitwords) == 2:
                            keywords_list.append(word)
                        else:
                            keywords_list.extend(splitwords)
                    keywords_list = list(filter(None, keywords_list))
                    channel_data['keywords'] = keywords_list

                channel_data['creation_date'] = response['items'][0]['snippet']['publishedAt']

                #Checks if channel has public total views count
                if "viewCount" in response['items'][0]['statistics']:
                    channel_data['view_count'] = int(response['items'][0]['statistics']['viewCount'])

                channel_data['subscriber_count'] = int(response['items'][0]['statistics']['subscriberCount'])
                channel_data['video_count'] = int(response['items'][0]['statistics']['videoCount'])

                self.channel_items[channel_data['id']]['channel_data'] = channel_data

                yield Request(self.get_url(channel_data['id'], "videos_list", r.meta["usedAPI"]), 
                                callback=self.parse_videos, meta={"channel_id": channel_data['id'], "usedAPI": r.meta["usedAPI"]})
            else:
                print("ABORTED/(Private/Low Subscribers/): "+response['items'][0]['snippet']['title']+"\n\n")
                #DocumentsDeleter.deleteDocument(DocumentsDeleter, response['items'][0]['id'])
                

    #Asks for the videos of the channel 
    def parse_videos(self,r):
        response = json.loads(r.text)
        channel_id = r.meta["channel_id"]

        if "error" in response:
            if response['error']['errors'][0]['reason']=="quotaExceeded":
                self.handle_API_error(channel_id, None, r.meta["usedAPI"], "parse_videos")
        else:
            #Checks if the channel has videos
            if not response['items'] and not "prevPageToken" in response:
                print("ABORTED (Has no videos): "+channel_id+"\n\n\n")
                #DocumentsDeleter.deleteDocument(DocumentsDeleter, channel_id)
            else:
                for item in response['items']:
                    video_id = item['id']['videoId']
                    #Checks if the video has already been scraped
                    if not any(video['video_id'] == video_id for video in self.channel_items[channel_id]["videos"]):
                        yield Request(self.get_url(video_id, "video", r.meta["usedAPI"]), callback=self.parse_video_stats, 
                                            meta={"channel_id":channel_id, "video_id":video_id, "usedAPI":r.meta["usedAPI"]})
                #Checks if the channel has more videos                                
                if 'nextPageToken' in response:
                    yield Request(self.get_url(channel_id+","+response['nextPageToken'], "next_page", r.meta["usedAPI"]), callback=self.parse_videos, 
                                        meta={"channel_id": channel_id, "usedAPI": r.meta["usedAPI"]})


    #Receives the videos of the channel
    def parse_video_stats(self,r):
        response = json.loads(r.text)

        if "error" in response:
            if response["error"]["errors"][0]["reason"]=="quotaExceeded":
                self.handle_API_error(r.meta["channel_id"], r.meta["video_id"], r.meta["usedAPI"], "parse_video_stats")
        else:
            video_data = VideoData(tags=[])

            channel_id = r.meta["channel_id"]

            #Checks if the video has hashtags
            if "tags" in response['items'][0]['snippet']:
                for tag in response['items'][0]['snippet']['tags']:
                    if not tag in video_data['tags']:
                        video_data['tags'].append(tag)

            video_data['video_category'] = self.video_categories.get(response['items'][0]['snippet']['categoryId'])
            video_data['video_id'] = response['items'][0]['id']
            video_data['title'] = response['items'][0]['snippet']['title']
            video_data['upload_date'] = response['items'][0]['snippet']['publishedAt']
            
            video_data['duration'] = int(isodate.parse_duration(response['items'][0]["contentDetails"]["duration"]).total_seconds())

            #Checks if the video has public views count
            if 'viewCount' in response['items'][0]['statistics']:
                video_data['view_count'] = int(response['items'][0]['statistics']['viewCount'])

            #Checks if the video has public likes count  
            if "likeCount" in response['items'][0]['statistics']: 
                video_data['like_count'] = int(response['items'][0]['statistics']['likeCount'])
           
            #Checks if the video has public dislikes count
            if "dislikeCount" in response['items'][0]['statistics']:
                video_data['dislike_count'] = int(response['items'][0]['statistics']['dislikeCount'])

            #Checks if the video has public comments count  
            if "commentCount" in response['items'][0]['statistics']:
                video_data['comment_count'] = int(response['items'][0]['statistics']['commentCount'])

            self.channel_items[channel_id]['videos'].append(video_data)

            yield self.channel_items[channel_id]


    #Returns a non-exceeded API key
    def get_active_API(self):
        for key in self.API_keys:
            if self.API_keys[key] == "active":
                return key
        raise CloseSpider('All API keys exceeded.')


    #Returns the appropriate url
    def get_url(self, id, return_type, API_key):
        published_before = "&publishedBefore=2020-12-31T00%3A00%3A00Z"
        published_after = "&publishedAfter=2020-01-01T00%3A00%3A00Z"

        if return_type == "videos_list":
            return f"{self.youtube_url}/search?key={API_key}&channelId={id}&part=id&order=date&type=video"+published_after+published_before+"&maxResults=50"
        elif return_type == "video":
            return f"{self.youtube_url}/videos?key={API_key}&id={id}&part=statistics,id,snippet,contentDetails&fields=items(id,snippet/publishedAt,snippet/title,snippet/categoryId,snippet/tags,contentDetails/duration,contentDetails/licensedContent,contentDetails/caption,statistics)"
        elif return_type == "next_page":
            words = id.split(",")
            return f"{self.youtube_url}/search?key={API_key}&channelId={words[0]}&part=id&order=date&type=video"+published_after+published_before+"&maxResults=50&pageToken={words[1]}"
        elif return_type == "channel":
            return f"{self.youtube_url}/channels?key={API_key}&part=snippet,id,statistics,brandingSettings&fields=items(brandingSettings/channel/keywords,snippet/title,snippet/publishedAt,statistics,id)&id={id}"


    #Handles errors during scraping
    def handle_API_error(self, channel_id, video_id, used_API, callback_function):
        self.API_keys[used_API] = "inactive"
        new_API = self.get_active_API()

        if callback_function == "parse":
            yield Request(self.get_url(channel_id, "channel", new_API), callback=self.parse, meta={"usedAPI": new_API, "channel_id": channel_id})
            return
        elif callback_function == "parse_videos":
            yield Request(self.get_url(channel_id, "videosList", new_API), callback=self.parse_videos, meta={"channel_id": channel_id, "usedAPI": new_API})
            return
        
        yield Request(self.get_url(channel_id, "video", new_API), callback=self.parse_video_stats, meta={"channel_id":channel_id, "video_id":video_id, "usedAPI":new_API})
        return