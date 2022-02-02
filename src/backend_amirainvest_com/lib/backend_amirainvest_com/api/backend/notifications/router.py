import uuid

from fastapi import APIRouter, Depends, Security, status
from backend_amirainvest_com.api.backend.notifications.controller import (
    create_controller,
    get_controller,
    update_controller,
    create_settings_controller,
    get_settings_controller,
    update_settings_controller
)
from backend_amirainvest_com.api.backend.notifications.model import (
    CreateModel, GetModel, UpdateModel,
    CreateSettingsModel, GetSettingsModel, UpdateSettingsModel
)
from backend_amirainvest_com.controllers.auth import auth_dep, auth_depends_user_id

router = APIRouter(prefix="/notifications", tags=["Notifications / Settings"] )#, dependencies=[Security(auth_dep, scopes=[])])



# Notifications are created from various jobs. They are read and updated via the API

@router.post("/get", 
    summary='Retrieve User Notifications', 
    description='This should run when you initialize the Notifications tab', status_code=status.HTTP_200_OK, 
    response_model=GetModel
    )
async def get_route(user_id: uuid.UUID):
    return (
        await get_controller(user_id)
    )._asdict()


@router.post("/update", 
    summary='Update User Notifications', 
    description='Use this to delete a notification or to mark it as read',
    status_code=status.HTTP_200_OK, 
    response_model=GetModel
    )
async def update_route(user_id: uuid.UUID, update_data: UpdateModel):
    return (
        await update_controller(
            user_id,
            update_data,
        )
    )._asdict()


#notification settings

@router.post("/settings/get",
    summary='Retrieve User Notification Settings', 
    description='This should run when you enter a user\'s profile allowing them to see their notifications settings', 
    status_code=status.HTTP_200_OK, 
    response_model=GetSettingsModel
    )
async def get_settings_route(user_id: uuid.UUID): 
    return (
        await get_settings_controller(user_id)
    )._asdict()

@router.post("/settings/update", 
    summary='Updates user\'s notification settings',
    description='This should run when a user makes a change to any of their notification settings within their account profile',
    status_code=status.HTTP_200_OK, 
    response_model=GetSettingsModel
    )
async def update_settings_route(user_id: uuid.UUID, update_data: UpdateSettingsModel):
    return (
        await update_settings_controller(
            user_id,
            update_data,
        )
    )._asdict()

@router.post("/settings/create",
    summary='Create a settings record on creation of a new user',
    description='This runs when a new user profile is created. It creates a record in the settings table with their specific settings. All are True by default',
    status_code=status.HTTP_200_OK, 
    response_model=GetSettingsModel
    )
async def create_settings_controller(user_id: uuid.UUID, create_data: CreateSettingsModel):
    return (
        await create_settings_controller(
            user_id,
            create_data,
        )
    )._asdict()
