import csv
import asyncio
from pprint import pprint

from sqlalchemy import insert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from data_imports_amirainvest_com.platforms.youtube import load_user_data as load_youtube
from data_imports_amirainvest_com.platforms.substack import load_user_data as load_substack
from data_imports_amirainvest_com.platforms.twitter import load_user_data as load_twitter
from data_imports_amirainvest_com.controllers.youtubers import create_youtuber
from data_imports_amirainvest_com.controllers.substack_users import create_substack_user
from common_amirainvest_com.schemas.schema import UsersModel, Users, generate_uuid_string
from common_amirainvest_com.utils.decorators import Session



@Session
async def create_husk_account(session: AsyncSession, husk_data: UsersModel) -> Row:
    return await session.execute(
        insert(Users).values(**husk_data).returning(Users)
    )



async def process_creator_file(file_path: str):
    with open(file_path) as f:
        failed = []
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            user_id = generate_uuid_string()
            user_row = {
                "id": user_id,
                "sub": "husk_account_"+user_id,
                "first_name": row.get("username"),
                "last_name": "", 
                "email": "husk_email_"+user_id,
                "username":row.get("username"),
                "personal_site_url":row.get("personal_website")
            }
            tags = []
            for tag in ['Tags1', 'Tags2', 'Tags3', 'Tags4']:
                if row.get(tag):
                    tags.append(row.get(tag))
            user_row['chip_labels']=tags
            husk_data = UsersModel(**user_row)
            platform = ''
            try:
                await create_husk_account(husk_data=husk_data.dict(exclude_none=True))
                if row.get("twitter_handle"):
                    platform = 'twitter'
                    await load_twitter(row.get("twitter_handle"), user_id)
                if row.get("youtube"):
                    platform = "youtube"
                    await load_youtube(row.get("youtube"), user_id)
                if row.get("substack_username"):
                    platform = "username"
                    await load_substack(row.get("substack_username"), user_id)
            except Exception as e:
                failed.append({'user':husk_data, 'exception':e, 'platform':platform})
    pprint(failed)


if __name__ == "__main__":
    asyncio.run(process_creator_file('src/data_imports_amirainvest_com/lib/data_imports_amirainvest_com/husk_accounts/creator_list.csv'))

