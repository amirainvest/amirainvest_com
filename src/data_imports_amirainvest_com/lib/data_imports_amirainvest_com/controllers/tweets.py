from sqlalchemy import select

from common_amirainvest_com.schemas.schema import Tweets
from common_amirainvest_com.utils.decorators import Session


def all_user_tweets(twitter_user_id):
    return select(Tweets).where(Tweets.twitter_user_id == twitter_user_id)


@Session
async def create_tweet(session, tweet_data: dict):
    tweet = Tweets(**tweet_data)
    session.add(tweet)
    return tweet


@Session
async def get_most_recent_tweet_for_twitter_user(session, twitter_user_id):
    tweet = await session.execute(all_user_tweets(twitter_user_id).order_by(Tweets.created_at.desc()).limit(1))
    return tweet.scalars().one()


@Session
async def get_tweets_for_creator(session, twitter_user_id: str):
    tweets = await session.execute(all_user_tweets(twitter_user_id))
    return tweets.scalars().all()
