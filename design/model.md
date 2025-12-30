## Transaction Model

Category
- id
- name

Account
- id
- name

Transaction
- id
- name
- amount
- date
- account_id
- category_id


## Subscription Model

Subscription
- id
- name
- amount
- frequency (monthly, yearly)
- interval
- status (active, cancelled)

SubscriptionInstance
- id
- subscription_id
- amount
- due_date
- transaction_id (nullable)
- status ('due', 'paid', 'overdue')


## Investment Model

Investment
- id
- name
- start_date
- status (active, closed)

InvestmentValueSnapshot
- id
- investment_id
- date
- current_value

InvestmentPlan
- id
- investment_id
- amount
- frequency (monthly, yearly)
- interval
- status (active, closed)

InvestmentPlanInstance
- id
- investment_plan_id
- amount
- due_date
- transaction_id (nullable)
- status ('planned', 'executed', 'skipped')
