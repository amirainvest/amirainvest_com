from typing import List

from fastapi import APIRouter, Depends, status

from backend_amirainvest_com.api.backend.notifications.controller import (  # create_controller,
    create_settings_controller,
    get_settings_controller,
    list_controller,
    update_controller,
    update_settings_controller,
)
from backend_amirainvest_com.api.backend.notifications.model import (  # CreateModel,
    CreateSettingsModel,
    InitReturnSettingsModel,
    NotificationSettingsModel,
    NotificationsModel,
    UpdateModel,
    UpdateSettingsModel,
)
from backend_amirainvest_com.controllers.auth import auth_depends_user_id


router = APIRouter(prefix="/notifications", tags=["Notifications / Settings"])


# Notifications are created from various jobs. They are read and updated via the API


@router.post(
    "/list",
    summary="Retrieve All User Notifications",
    description="This should run when you initialize the Notifications tab",
    status_code=status.HTTP_200_OK,
    response_model=List[NotificationsModel],
)
async def list_route(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    all_notifications = await list_controller(user_id)
    return [notification.__dict__ for notification in all_notifications]


@router.post(
    "/update",
    summary="Update User Notifications",
    description="Use this to delete a notification or to mark it as read",
    status_code=status.HTTP_200_OK,
    response_model=NotificationsModel,
)
async def update_route(update_data: UpdateModel, token=Depends(auth_depends_user_id)):
    return (
        await update_controller(
            user_id=token["https://amirainvest.com/user_id"],
            update_data=update_data,
        )
    )._asdict()


# notification settings


@router.post(
    "/settings/get",
    summary="Retrieve User Notification Settings",
    description="This should run when you enter a user's profile allowing them to see their notifications settings",
    status_code=status.HTTP_200_OK,
    response_model=NotificationSettingsModel,
)
async def get_settings_route(token=Depends(auth_depends_user_id)):
    user_id = token["https://amirainvest.com/user_id"]
    return (await get_settings_controller(user_id)).__dict__


@router.post(
    "/settings/update",
    summary="Updates user's notification settings",
    description="Runs when user makes change to their notification settings",
    status_code=status.HTTP_200_OK,
    response_model=NotificationSettingsModel,
)
async def update_settings_route(update_data: UpdateSettingsModel, token=Depends(auth_depends_user_id)):
    return (
        await update_settings_controller(
            user_id=token["https://amirainvest.com/user_id"],
            update_data=update_data,
        )
    )._asdict()


@router.post(
    "/settings/create",
    summary="Create a settings record on creation of a new user",
    description="This runs when a new user profile is created",
    status_code=status.HTTP_200_OK,
    response_model=InitReturnSettingsModel,
)
async def create_settings_route(create_data: CreateSettingsModel, token=Depends(auth_depends_user_id)):
    settings_id = await (
        create_settings_controller(user_id=token["https://amirainvest.com/user_id"], create_data=create_data)
    )
    return InitReturnSettingsModel(id=settings_id)
