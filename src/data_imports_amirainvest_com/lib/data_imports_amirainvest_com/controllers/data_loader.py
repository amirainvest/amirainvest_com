from common_amirainvest_com.utils.logger import log
from data_imports_amirainvest_com.platforms import substack, twitter, youtube


async def load_platform_user_data(platform, platform_unique_id, creator_id):
    log.info(f"{platform_unique_id} loading into {platform}")
    if platform == "twitter":
        await twitter.load_user_data(platform_unique_id, creator_id)
    elif platform == "youtube":
        await youtube.load_user_data(platform_unique_id, creator_id)
    elif platform == "substack":
        await substack.load_user_data(platform_unique_id, creator_id)
