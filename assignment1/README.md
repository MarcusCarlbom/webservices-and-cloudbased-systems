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

## Starting DB
Remember to start MongoDB on the config port (by default 27420)                                                                                                                                                                      
```
mongod --port 27420
```
Specify the db path with
```
mongod --port 27420 --dbpath [path to db folder]
```

## Running the code
Start up the rest service for local host
```zsh
python3 rest_service.py
```

## Inspecting DB
You can inspect the DB using DataGrip or something else at the following connection string (by default):
`mongodb://localhost:27420/url_shortener`

## Swagger UI Testing
The API includes interactive documentation via Swagger UI. Once the service is running, access it at:
```
http://127.0.0.1:5000/apidocs/
```
From the Swagger UI, you can view all available endpoints with documentation. You can test each endpoint interactively, see request/response schemas and examples. You can also access the raw specification at `http://127.0.0.1:5000/apisepc.json`

## Manual Testing
You can also make Postman requests, use terminal with curl, or modify the `tester.py` file to do the requests for you. For starters, you can run the `tester.py` to simply see it add `google.com` as the first source and print what the first source in the dictionary is. After running unmodified `tester.py`, you can test it in your browser by typing in `http://127.0.0.1:5000/1`.