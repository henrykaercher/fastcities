# Fastcities

Fastcities.py is a CLI-like Python script that automates page uploads to NeoCities.
It checks for recently modified files and uploads only the changed ones, instead
of pushing the entire blog every time.

## Notes
- This script still needs some work regarding error handling.
- 'last_update' need to be check when first open the script.
- API Key does not work for uploads yet, so use your password instead.
- I know this is not 'python standard', and it will keep that way.

## How to use

Just download the 'fastcities.py' wennever you like and open it:
```python
python fastcities.py
```

The aplicaton has 4 options:
- [1]: Resgiter new path
- [2]: Resgiter new API
- [3]: Push updates to NeoCities
- [4]: Exit

## Requirements
- Python 3
- 'curl' available in the system
- A NeoCities account

