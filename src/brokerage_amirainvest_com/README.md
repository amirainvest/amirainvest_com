# Brokerage Data

## Current/Future Thoughts
How do we differentiate between a Plaid transaction, or a Robinhood transaction? When you add in an account that overwrites a Plaid account, do we remove that Plaid data?
Or, do we try to overwrite + supplement the data
When we add a E-Trade, or Robinhood, or the like, that is considered an institution which will "overwrite" an institution we have registered
via Plaid, which will overwrite accounts
Thinking we just keep supplementing the same institution/account data and keep ids this way we can fall back if the service is down
and start pulling data via Plaid -- though this would only be for current holdings
Which is why we need to have a repository class tied to each brokerage on how they are adding data

