## Assignment 1 - REST service
A minimal URL shortening service built with **Python Flask** and **Base62 encoding**.

Code was written on macOS Tahoe 26.2 and the following commands are based on `zsh`.

## Setup
Create a local virtual python environment
```zsh
python3 -m venv venv
```

Start up the local environment
```zsh
source venv/bin/activate
```

Download the required modules
```zsh
pip install -r requirements.txt
```

## Running the code
Start up the rest service for local host
```zsh
python3 rest_service.py
```

Now either make Postman requests, use terminal using curl or modify the `tester.py` file to do the requests for you. For starters, you can run the `tester.py` to simply see it add `google.com` as the first source and print what the first source in the dictionary is. After running unmodified `tester.py`, you can test it in your browser by typing in `http://127.0.0.1:5000/1`.