from typing import Optional

import requests

from common_amirainvest_com.schemas.schema import MediaPlatform, SubscriptionLevel
from common_amirainvest_com.utils.datetime_utils import parse_iso_8601_from_string
from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.consts import YOUTUBE_API_KEY_ENV, YOUTUBE_API_URL
from data_imports_amirainvest_com.controllers import posts
from data_imports_amirainvest_com.controllers.youtube_videos import create_youtube_video, get_videos_for_channel
from data_imports_amirainvest_com.controllers.youtubers import create_youtuber, get_youtuber
from data_imports_amirainvest_com.platforms.platforms import PlatformUser


HEADERS = {
    "Cache-Control": "no-cache",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


class YouTuber(PlatformUser):
    def __init__(self, _id, creator_id, playlist="uploads"):
        super().__init__()
        self._id = _id  # _ID CAN BE CHANNEL_USERNAME OR CHANNEL_ID
        self.creator_id = creator_id
        self.channel_username: str = ""
        self.channel_id: str = ""
        self.get_channel_id()
        self.playlist = playlist
        self.title: str = ""
        self.description: str = ""
        self.profile_img_url: str = ""
        self.uploads_id: str = ""
        self.subscriber_count: Optional[int] = None
        self.video_count: Optional[int] = None

    def __repr__(self):
        return f"<{self.channel_username} : {self.title}>"

    def get_unique_id(self):
        return self.channel_id

    def get_upload_playlist_id(self):
        if not self.channel_id:
            self.get_youtube_channel_data()
        return f"UU{self.channel_id[2:]}"

    def get_channel_id(self):
        log.info(f"Getting channel id for {self._id}")
        try:
            self.channel_id = (
                requests.get(f"https://www.youtube.com/c/{self._id}").text.split('externalId":"')[1].split('",')[0]
            )
            self.channel_username = self._id
            log.info(f"{self._id} is a channel username.")
        except IndexError:
            log.info(f"{self._id} is a channel id.")
            self.channel_id = self._id
            self.channel_username = self._id
        return self.channel_id

    def get_youtube_channel_data(self):
        log.info(f"Getting channel data for {self.channel_username}")
        if not self.channel_id:
            self.get_channel_id()
        channel_data = requests.request(
            "GET",
            f"{YOUTUBE_API_URL}/channels",
            headers=HEADERS,
            params={
                "part": "snippet,contentDetails,id,statistics",
                "id": self.channel_id,
                "key": YOUTUBE_API_KEY_ENV,
            },
        ).json()["items"][0]
        self.title = channel_data["snippet"]["title"]
        self.description = channel_data["snippet"]["description"]
        self.profile_img_url = channel_data["snippet"]["thumbnails"]["default"]["url"]
        self.uploads_id = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]
        self.subscriber_count = int(channel_data["statistics"]["subscriberCount"])
        self.video_count = int(channel_data["statistics"]["videoCount"])
        del self._id
        del self.uploads_id

    async def get_stored_channel_from_database(self):
        log.info(f"Getting stored channel data for {self.channel_username}")
        if not self.channel_id:
            self.get_channel_id()

        user_channel_data = await get_youtuber(channel_id=self.channel_id)
        if user_channel_data:
            self.title = user_channel_data.title
            self.description = user_channel_data.description
            self.profile_img_url = user_channel_data.pic
            self.uploads_id = user_channel_data.uploads_id
            self.subscriber_count = user_channel_data.subscriber_count
            self.video_count = user_channel_data.video_count

    async def get_stored_youtube_videos_from_database(self):
        if not self.channel_id:
            self.get_channel_id()
        return await get_videos_for_channel(self.channel_id)

    async def get_youtube_videos_from_url(self):
        videos = []
        video_posts = []
        stored_videos = await self.get_stored_youtube_videos_from_database()
        log.info(f"Getting videos for {self.channel_username}")
        next_token = True
        found_existing = False
        if self.playlist == "uploads":
            self.playlist = self.get_upload_playlist_id()
        params = {
            "part": "snippet,contentDetails",
            "playlistId": self.playlist,
            "maxResults": 50,  # MAX 50
            "key": YOUTUBE_API_KEY_ENV,
        }
        while next_token and not found_existing:
            playlist_data = requests.request(
                "GET",
                f"{YOUTUBE_API_URL}/playlistItems",
                headers=HEADERS,
                params=params,
            ).json()
            next_token = "nextPageToken" in playlist_data
            if next_token:
                params["pageToken"] = playlist_data["nextPageToken"]
            for video_data in playlist_data.get("items", []):
                created_at = parse_iso_8601_from_string(video_data["contentDetails"]["videoPublishedAt"])
                count = 0
                if video_data["contentDetails"]["videoId"] not in [x.video_id for x in stored_videos] and count < 5:
                    videos.append(
                        YouTubeVideo(
                            channel_id=self.channel_id,
                            title=video_data["snippet"]["title"],
                            published_at=created_at,
                            video_id=video_data["contentDetails"]["videoId"],
                            video_url=f"https://www.youtube.com/{video_data['contentDetails']['videoId']}",
                            embed_url=f"https://www.youtube.com/embed/{video_data['contentDetails']['videoId']}",
                        )
                    )
                    video_posts.append(
                        {
                            "creator_id": self.creator_id,
                            "subscription_level": SubscriptionLevel.standard,
                            "title": video_data["snippet"]["title"],
                            "content": f"https://www.youtube.com/embed/{video_data['contentDetails']['videoId']}",
                            "photos": [],
                            "platform": MediaPlatform.youtube,
                            "platform_display_name": self.channel_username,
                            "platform_user_id": self.channel_id,
                            "platform_img_url": self.profile_img_url,
                            "platform_profile_url": f"https://www.youtube.com/channel/{self.channel_id}",
                            "twitter_handle": None,
                            "platform_post_id": video_data["contentDetails"]["videoId"],
                            "platform_post_url": f"https://www.youtube.com/{video_data['contentDetails']['videoId']}",
                            "created_at": created_at,
                            "updated_at": created_at,
                        }
                    )
                else:
                    found_existing = True
        del self.playlist
        return videos, video_posts

    async def store_user_data(self):
        self.get_youtube_channel_data()
        videos, video_posts = await self.get_youtube_videos_from_url()
        youtuber_exists = await self.get_user_platform_pair_exists("youtube", self.get_unique_id())
        if not youtuber_exists:
            log.info(f"Added new YouTuber: {self.channel_username}")
            await create_youtuber(self.__dict__)
        if videos:
            log.info(f"New videos found for YouTuber: {self.channel_username}")
            for video in videos:
                await video.store_video_data()
            for video_post in video_posts:
                await posts.create_post(video_post)
                # posts.put_post_on_creators_redis_feeds(video_post)
                # await posts.put_post_on_subscriber_redis_feeds(video_post)


class YouTubeVideo:
    def __init__(
        self,
        channel_id,
        title,
        video_id,
        video_url,
        embed_url,
        published_at,
    ):
        log.info(f"Video: {title} (id: {video_id})")
        self.channel_id: str = channel_id
        self.title: str = title
        self.video_id: str = video_id
        self.video_url: str = video_url
        self.embed_url: str = embed_url
        self.published_at: str = published_at

    def __repr__(self):
        return f"<{self.channel_id} : {self.title}>"

    async def store_video_data(self):
        await create_youtube_video(self.__dict__)


async def load_user_data(channel_id, creator_id):
    youtuber = YouTuber(_id=channel_id, creator_id=creator_id)
    await youtuber.store_user_data()
