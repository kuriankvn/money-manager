# money manager

## phase 1
### user 
- user fields uid(UUID), name(str)
- should be able to do cruds on user
### transaction
- type enum income/expense
- category fields uid(UUID) type(TYPE), name(str), parent_category(CATEGORY | None)
- transaction fields uid(UUID), user_id(uid(UUID)), amount(float), date_time(float), type(Type) and category(CATEGORY)