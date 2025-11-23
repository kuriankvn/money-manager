# money manager

## phase 1 (cli app)
### user 
- user fields uid(UUID), name(str)
- should be able to do cruds on user
### category
- type enum income/expense
- category fields uid(UUID), name(str), type(TYPE)
### transaction
- transaction fields uid(UUID), name(str), amount(float), datetime(float), user(USER), category(CATEGORY)
