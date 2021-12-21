from datetime import datetime
from random import choice, randint

from faker import Faker

from common_amirainvest_com.schemas.schema import (
    Bookmarks,
    BroadcastRequests,
    Posts,
    SubstackArticles,
    SubstackUsers,
    Tweets,
    TwitterUsers,
    UserMediaErrors,
    Users,
    UserSubscriptions,
    YouTubers,
    YouTubeVideos,
)
from common_amirainvest_com.utils.async_utils import run_async_function_synchronously
from common_amirainvest_com.utils.decorators import Session


fake = Faker()


def get_fake_user():
    return Users(
        id=fake.uuid4(),
        sub="Sub",
        name=fake.name(),
        bio="Bio",
        username=fake.user_name(),
        picture_url=fake.url(),
        email=fake.email(),
        personal_site_url=fake.url(),
        linkedin_profile=fake.url(),
        email_verified=choice([False, True]),
        interests_value=choice([False, True]),
        interests_growth=choice([False, True]),
        interests_long_term=choice([False, True]),
        interests_short_term=choice([False, True]),
        interests_diversification_rating=100,
        benchmark=choice(["S&P500", "Dow", "Nasdaq"]),
        public_profile=choice([False, True]),
        public_performance=choice([False, True]),
        public_holdings=choice([False, True]),
        public_trades=choice([False, True]),
        is_claimed=choice([False, True]),
        is_deactivated=choice([False, True]),
        is_deleted=choice([False, True]),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@Session
async def create_fake_user(session):
    user = get_fake_user()
    session.add(user)
    return user


async def get_fake_user_subscription(subscriber=None, creator=None):
    subscriber = subscriber if subscriber else await create_fake_user()
    creator = creator if creator else await create_fake_user()
    return UserSubscriptions(
        subscriber_id=subscriber.id,
        creator_id=creator.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_deleted=choice([False, True]),
    )


@Session
async def create_fake_user_subscription(session, subscriber=None, creator=None):
    user_subscription = await get_fake_user_subscription(subscriber, creator)
    session.add(user_subscription)
    return user_subscription


async def get_fake_user_media_error(user=None):
    user = user if user else await create_fake_user()
    return UserMediaErrors(
        user_id=user.id,
        platform=choice(["twitter", "youtube", "substack"]),
        error_at="Error At",
        updated_at=datetime.utcnow(),
    )


@Session
async def create_fake_user_media_error(session, user=None):
    user_media_error = await get_fake_user_media_error(user)
    session.add(user_media_error)
    return user_media_error


async def get_fake_post(platform="twitter", creator=None):
    platform_id, platform_user_id = "", ""
    if platform == "twitter":
        twitter_user = await create_fake_twitter_user()
        tweet = await create_fake_tweet(twitter_user=twitter_user)
        platform_user_id = twitter_user.twitter_user_id
        platform_id = tweet.tweet_id
    elif platform == "youtube":
        youtuber = await create_fake_youtuber()
        youtube_video = await create_fake_youtube_video(youtuber=youtuber)
        platform_user_id = youtuber.channel_id
        platform_id = youtube_video.video_id
    elif platform == "substack":
        substack_user = await create_fake_substack_user()
        substack_article = await create_fake_substack_article(substack_user=substack_user)
        platform_user_id = substack_user.username
        platform_id = substack_article.url
    creator = creator if creator else await create_fake_user()
    return Posts(
        id=randint(0, 1000000),
        text="Text",
        html="HMTL",
        platform=platform,
        platform_user_id=platform_user_id,
        platform_post_id=platform_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        creator_id=creator.id,
    )


@Session
async def create_fake_post(session, platform="twitter", creator=None):
    post = await get_fake_post(platform, creator)
    session.add(post)
    return post


async def get_fake_substack_user(creator=None, username=None):
    creator = creator if creator else await create_fake_user()
    return SubstackUsers(username=fake.uuid4() if username is None else username, creator_id=creator.id)


@Session
async def create_fake_substack_user(session, creator=None, username=None):
    substack_user = await get_fake_substack_user(creator, username)
    session.add(substack_user)
    return substack_user


async def get_fake_substack_article(substack_user=None):
    substack_user = substack_user if substack_user else await create_fake_substack_user()
    return SubstackArticles(
        article_id=fake.uuid4(),
        url=fake.url(),
        title="Title",
        summary="Summary",
        author="Author",
        created_at=datetime.utcnow(),
        username=substack_user.username,
    )


@Session
async def create_fake_substack_article(session, substack_user=None):
    substack_article = await get_fake_substack_article(substack_user)
    session.add(substack_article)
    return substack_article


async def get_fake_tweet(twitter_user=None):
    twitter_user = twitter_user if twitter_user else await create_fake_twitter_user()
    return Tweets(
        tweet_id=fake.uuid4(),
        twitter_user_id=twitter_user.twitter_user_id,
        language="Language",
        text="Text",
        possibly_sensitive=choice([False, True]),
        created_at=datetime.utcnow(),
        retweet_count=choice([1, 2, 3, 4, 5]),
        like_count=choice([1, 2, 3, 4, 5]),
        quote_count=choice([1, 2, 3, 4, 5]),
        tweet_url=fake.url(),
        embed=fake.url(),
    )


@Session
async def create_fake_tweet(session, twitter_user=None):
    tweet = await get_fake_tweet(twitter_user)
    session.add(tweet)
    return tweet


async def get_fake_twitter_user(creator=None, twitter_user_id=None):
    creator = creator if creator else await create_fake_user()
    return TwitterUsers(
        twitter_user_id=fake.uuid4() if twitter_user_id is None else twitter_user_id,
        creator_id=creator.id,
        name=creator.name,
        username="Username",
        profile_img_url=fake.url(),
        profile_url=fake.url(),
        follower_count=choice([1, 2, 3, 4, 5]),
        following_count=choice([1, 2, 3, 4, 5]),
        tweet_count=choice([1, 2, 3, 4, 5]),
    )


@Session
async def create_fake_twitter_user(session, creator=None, twitter_user_id=None):
    twitter_user = await get_fake_twitter_user(creator, twitter_user_id)
    session.add(twitter_user)
    return twitter_user


async def get_fake_youtube_video(youtuber=None):
    youtuber = youtuber if youtuber else await create_fake_youtuber()
    return YouTubeVideos(
        video_id=fake.uuid4(),
        title="Title",
        published_at=datetime.utcnow(),
        video_url=fake.url(),
        embed_url=fake.url(),
        playlist_id=fake.uuid4(),
        channel_id=youtuber.channel_id,
    )


@Session
async def create_fake_youtube_video(session, youtuber=None):
    youtube_video = await get_fake_youtube_video(youtuber)
    session.add(youtube_video)
    return youtube_video


async def get_fake_youtuber(creator=None, channel_id=None):
    creator = creator if creator else await create_fake_user()
    return YouTubers(
        channel_id=fake.uuid4() if channel_id is None else channel_id,
        creator_id=creator.id,
        title="Title",
        channel_username="Channel Username",
        profile_img_url=fake.url(),
        description="Description",
        subscriber_count=choice([1, 2, 3, 4, 5]),
        video_count=choice([1, 2, 3, 4, 5]),
    )


@Session
async def create_fake_youtuber(session, creator=None, channel_id=None):
    youtuber = await get_fake_youtuber(creator, channel_id)
    session.add(youtuber)
    return youtuber


async def get_fake_broadcast_request(subscriber=None, creator=None):
    subscriber = subscriber if subscriber else await create_fake_user()
    creator = creator if creator else await create_fake_user()
    return BroadcastRequests(
        id=randint(0, 100000),
        subscriber_id=subscriber.id,
        creator_id=creator.id,
        created_at=datetime.utcnow(),
    )


@Session
async def create_fake_broadcast_request(session, subscriber=None, creator=None):
    broadcast_request = await get_fake_broadcast_request(subscriber, creator)
    session.add(broadcast_request)
    return broadcast_request


async def get_fake_bookmark(user=None, post=None):
    user = user if user else await create_fake_user()
    post = post if post else await create_fake_post()
    return Bookmarks(
        user_id=user.id,
        post_id=post.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_deleted=choice([False, True]),
    )


@Session
async def create_fake_bookmark(session, user=None, post=None):
    bookmark = await get_fake_bookmark(user, post)
    session.add(bookmark)
    return bookmark


async def generate_data_import_test_data():
    creator = await create_fake_user()
    await create_fake_substack_user(creator, username="jonahlupton")
    await create_fake_twitter_user(creator, twitter_user_id="JonahLupton")
    await create_fake_youtuber(creator, channel_id="UCnNV58dwf5X7dkrvCE18Djw")


async def generate_data():
    for i in range(0, 100):
        try:
            # await create_fake_user()
            # await create_fake_youtuber()
            # await create_fake_bookmark()
            # await create_fake_twitter_user()
            # await create_fake_substack_user()
            await create_fake_post()
            # await create_fake_broadcast_request()
            # await create_fake_substack_article()
            # await create_fake_tweet()
            # await create_fake_user_media_error()
            # await create_fake_user_subscription()
            # await create_fake_youtube_video()
        except Exception:
            pass


if __name__ == "__main__":
    print(
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
        run_async_function_synchronously(generate_data),
        ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
        sep="\n",
    )
