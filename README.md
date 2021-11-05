YouTube Scrapy Web Scraper
==========================

Overview
---------
This repository provides with a web scraper based on the Scrapy framework that is designed to extract public data from YouTube channels communicating with the YouTube Data API.

The present web scraper is part of my thesis with the title of "From digital footprints to facts: mining social data for marketing practices", whose aim was to collect public data from popular Greek Instagram and YouTube profiles and draw conclusions about:
1. the digital behavior and preferences of the Greek Instagram and YouTube community
2. the activity of Greek businesses on social media
3. the impact of COVID-19 on the digital behavior of the users

Requirements
------------
In order to use this web scraper you have to:
1. Install Python 3.6+
2. Install Scrapy
3. Install MongoDB and create a MongoDB database
- (Optional) Create your own YouTube Data API credentials

Description
---------------------------

#### Structure
---------------------------

This web scraper has the basic stracture of a Scrapy spider with the addition of two folders: 
* the "resources" folder 
    >created to store files that contain important data for the scraping mechanism, such as names of Instagram profiles or API keys.
* the "tools" folder.
    >created to store files that contain frequently used functions, such as functions that carry out the communication with the database.

####  Features
-----------------------------

The provided web scraper reads as input usernames of YouTube users from:
* a database collection
* a JSON file 
    >located in the "resources" folder


Due to the fact that this mechanism was created in the context of my thesis, it has a few specific features:
* it scrapes channels with a number of subscribers higher than 5.000 
* it scrapes profiles that have uploaded at least one video in 2020
* it scrapes only the videos that were uploaded during the year 2020
* it uses multiple API keys in order to achieve higher daily requests threshold
    >All the above parameters can be modified.


From each profile, the scraping mechanism collects:
* General Information:
    * **Channel title**
    * **Channel ID**
    * **Channel creation date**
    * **Total number of views**
    * **Number of subscribers**
    * **Number of videos**
    * **List of channel keywords**
    * **Gender**
        >It was manually populated, beacause YouTube Data API does not provide this field
* Fields of each uploaded channel:
    * **Video ID**
    * **Video title** 
    * **Upload date**
    * **Video duration**
    * **Number of Comments**
        >if this field is public
    * **Number of Views**
        >if this field is public
    * **Number of Likes**
        >if this field is public
    * **Number of Dislikes**
        >if this field is public
    * **Video category**
    * **Video hashtags**


In order to handle YouTube Data API's tactic that divides the videos of each channel at subsections videos, the collection of the fields mentioned above was completed via the following methods:
* **parse()**
    >Collects the general information of each channel and asks for the list of the uploaded videos by this channel 
* **parse_videos()**
    >Iterates over the list and asks for the available information about each video
* **parse_video_stats()**
    >Collects the necessary fields of each video


As it was mentioned above, the mechanism uses multiple YouTube Data API keys that are handled with the following methods :
* **get_active_API()**
    >Selects an API key that has not surpassed its daily requests threshold
* **handle_API_error()**
    >Deactivates an API key that has surpassed its daily requests threshold and selects another that is available


As soon as all the necessary fields have been collected, they are being grouped and stored as documents in the MongoDB database, using the file "pipelines.py". The structure of each document is declared in the "items.py" file and it is as follows:
* **ChannelData**
    >An object containing all the collected general information about a channel
* **VideoData**
    >An array containing all the collected general information about the videos of a channel


How to Use
---------------------------
1. Download the project
2. Open the file "yputube_spider.py" that is located in the folder "spiders"
3. Comment/Uncomment one of the provided methods to populate the list "channels_to_scrape"
    >Import names from file or database
4. Open the file "pipelines.py"
5. Upload the variables "myclient", "db" and "collection", based on the address of your database
6. Open the file "documents_finder.py", located in the folder "tools"
7. Upload the variables "myclient", "db" and "collection", based on the address of your database
8. Open the file "documents_deleter.py", located in the folder "tools"
9. Upload the variables "myclient", "db" and "collection", based on the address of your database
10. Open Command Line
11. **cd** to the path of the project
12. Run:
```
scrapy crawl YoutubeSpider
```
- (Optional): Update the file "APIkeys.py" in the folder "resources" with your own YouTube Data API keys
