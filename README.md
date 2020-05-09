# PersistentDict
## Python dictionary-like object with SQLite connection

It uses a sqlite table as a key-value store with serialization providing a dictionary-like interface.

Initialize:
```python
my_persistent_dict = PersistentDict('./persists.db')
```
and this dict will keep values between executions.

Extra method 'replace': you can clone a normal dict into a persistent one:
```python
my_persistent_dict.replace(some_other_ephemeral_dict)
```

Use it as a normal dict otherwise.

Be aware that the keys and the values get pickled on the way to the DB.
