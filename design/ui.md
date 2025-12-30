## Money Manager UI Design

### Pages

**Home**
- Dashboard overview
- Quick links to API documentation
- System status

**Accounts**
- List all accounts
- Create new account
- Update/Delete account

**Categories**
- List all categories
- Create new category
- Update/Delete category

**Transactions**
- List all transactions with account and category names
- Create new transaction (select account and category)
- Update/Delete transaction
- Export transactions to CSV
- Import transactions from CSV

**Subscriptions**
- List all subscriptions
- Create new subscription (frequency, interval, due_day, due_month, status)
- Update/Delete subscription
- Export subscriptions to CSV
- Import subscriptions from CSV

**Subscription Instances**
- List all subscription instances
- Create new instance (linked to subscription)
- Update/Delete instance
- Mark as paid (link to transaction)

**Investments**
- List all investments
- Create new investment
- Update/Delete investment

**Investment Snapshots**
- List all value snapshots for investments
- Create new snapshot (date, current_value)
- Update/Delete snapshot

**Investment Plans**
- List all investment plans
- Create new plan (linked to investment)
- Update/Delete plan

**Investment Plan Instances**
- List all plan instances
- Create new instance (linked to plan)
- Update/Delete instance
- Mark as executed (link to transaction)

### UI Components

**Forms**
- Input validation
- Dropdown selects for foreign keys
- Date pickers
- Number inputs with validation
- Status/frequency radio buttons

**Tables**
- Sortable columns
- Search/filter
- Pagination
- Action buttons (Edit, Delete)

**Export/Import**
- Download CSV button
- Upload CSV file
- Import results display (created/failed counts, errors)

### Navigation
- Sidebar with page links
- Grouped by domain (Transactions, Subscriptions, Investments)
- Quick links to API docs and health check