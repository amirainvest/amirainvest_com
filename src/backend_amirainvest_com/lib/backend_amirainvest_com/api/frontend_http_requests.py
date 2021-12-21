""""""

# ACCOUNT PAGE
"""
ON LOAD
    GET f"https://api.amirainvest.com/user_profile/subscriptions?amira_id=<amira_id>"

UPDATE PROFILE BUTTON
    POST "https://api.amirainvest.com/user_profile"
           {
            'amira_id': amira_id,
            'twitter_username': twitterHandle,
            'youtube_username': youtubeChannel,
            'substack_username': substackURL,
            'linkedin_profile': linkedinURL,
            'personal_site_url': personalSite,
            'bio': userBio
        }
"""

# BOOKMARK PAGE
"""
ON LOAD
    GET "https://api.amirainvest.com/get_cards/bookmarks?amira_id=<amira_id>"
"""

# CREATE ACCOUNT
"""
CREATE ACCOUNT BUTTON
    POST "https://api.amirainvest.com/user_profile"
        {
            "benchmark": "Lorem ipsum",
            "email": "Lorem ipsum",
            "email_verified": true,
            "interests_diversify": 123,
            "interests_growth": true,
            "interests_long_term": true,
            "interests_value": true,
            "intersts_short_term": true,
            "is_claimed": true,
            "linkedin_profile": "Lorem ipsum",
            "name": "Lorem ipsum",
            "personal_site_url": "Lorem ipsum",
            "public_hold": true,
            "public_perf": true,
            "public_profile": true,
            "public_trad": true,
            "sub": "6237ea82-854e-4242-a8db-21632c23d143",
            "substack_username": "Lorem ipsum",
            "twitter_username": "Lorem ipsum",
            "username": "Lorem ipsum",
            "youtube_username": "Lorem ipsum"
        }

    GET "https://api.amirainvest.com/user_profile?amira_id=<amira_id>"
"""

# CREATOR PROFILE PAGE

"""
ON LOAD
    GET "https://api.amirainvest.com/creator_profile?amira_id=<amira_id>&creator_id=<creator_id>"
    GET "https://api.amirainvest.com/creator_profile/posts?amira_id=<amira_id>&creator_id<creator_id>"

DATA REQUEST CLICK
    POST "https://api.amirainvest.com/subscribe/request"
        {
            "amira_id": <amira_id>,
            "creator_id": <creator_id>
        }

LOAD MORE POSTS
    GET "https://api.amirainvest.com/get_cards?token=<feedToken>&amira_id=<amira_id>"

"""

# DISCOVER PAGE
"""
ON LOAD
    GET "https://api.amirainvest.com/search_activate"
    GET "https://api.amirainvest.com/discovery?amira_id=<amira_id>"
"""

# FEED
"""
ON LOAD
    GET "https://api.amirainvest.com/get_cards?amira_id=<amira_id>"

LOAD MORE POSTS
    GET "https://api.amirainvest.com/get_cards?token=<feedToken>&amira_id=<amira_id>"

"""

# LOGIN LOADING
"""
# ON LOAD
    POST "https://dev-0nn4c3x4.us.auth0.com/oauth/token"
        {
            "code": <AuthorizationCode>,
            "client_id": 'KlaSnTv49C4Td1XulqYMui0ZdpR23Cwa',
            "code_verifier": <code_verifier>,
            "redirect_uri": 'sapappgyver://auth?code=246709',
            "grant_type": "authorization_code"
        }
    GET "https://dev-0nn4c3x4.us.auth0.com/userinfo"
    POST "https://api.amirainvest.com/login/check_user"
        {
            "sub": <currentUser.id>  # SUB IN USERS TABLE
        }
    GET "https://api.amirainvest.com/user_profile?amira_id=<amira_id>"


"""

# NO HTTP CALLS
"""
FEED FILTER
CREATE ACCOUNT 1 & 2
CLICK ON TRADE PAGE
COMPETITIONS PROFILE PAGE
NOTIFICATIONS
PLAID
SEARCH RESULT
SINGLE WATCHLIST PAGE
USER PORTFOLIO
WATCHLISTS PAGE
WELCOME SCREEN
"""
