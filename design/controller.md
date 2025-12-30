## Transaction Controllers

Category
- POST / - Create category
- GET /{uid} - Get category by ID
- GET / - Get all categories
- PUT /{uid} - Update category
- DELETE /{uid} - Delete category

Account
- POST / - Create account
- GET /{uid} - Get account by ID
- GET / - Get all accounts
- PUT /{uid} - Update account
- DELETE /{uid} - Delete account

Transaction
- POST / - Create transaction
- GET /{uid} - Get transaction by ID
- GET / - Get all transactions
- PUT /{uid} - Update transaction
- DELETE /{uid} - Delete transaction


## Subscription Controllers

Subscription
- POST / - Create subscription
- GET /{uid} - Get subscription by ID
- GET / - Get all subscriptions
- PUT /{uid} - Update subscription
- DELETE /{uid} - Delete subscription

SubscriptionInstance
- POST / - Create subscription instance
- GET /{uid} - Get subscription instance by ID
- GET / - Get all subscription instances
- PUT /{uid} - Update subscription instance
- DELETE /{uid} - Delete subscription instance


## Investment Controllers

Investment
- POST / - Create investment
- GET /{uid} - Get investment by ID
- GET / - Get all investments
- PUT /{uid} - Update investment
- DELETE /{uid} - Delete investment

InvestmentValueSnapshot
- POST / - Create investment snapshot
- GET /{uid} - Get investment snapshot by ID
- GET / - Get all investment snapshots
- PUT /{uid} - Update investment snapshot
- DELETE /{uid} - Delete investment snapshot

InvestmentPlan
- POST / - Create investment plan
- GET /{uid} - Get investment plan by ID
- GET / - Get all investment plans
- PUT /{uid} - Update investment plan
- DELETE /{uid} - Delete investment plan

InvestmentPlanInstance
- POST / - Create investment plan instance
- GET /{uid} - Get investment plan instance by ID
- GET / - Get all investment plan instances
- PUT /{uid} - Update investment plan instance
- DELETE /{uid} - Delete investment plan instance


## Export/Import Controllers

Transaction Export/Import
- GET /export/csv - Export all transactions to CSV
- POST /export/csv - Import transactions from CSV

Subscription Export/Import
- GET /export/csv - Export all subscriptions to CSV
- POST /export/csv - Import subscriptions from CSV
