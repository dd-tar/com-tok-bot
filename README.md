## Available Scripts

In the project directory, you can run:

### `python server.py`

Runs the bot locally.


### `python -m flask run`

Deploy the API endpoint for the site locally.  
  
  
To use a docker container:
```
docker build -t comtok ./
docker run -d --name tg -v /local_project_path/db:/home/db comtok
```
_Note: don\'t forget to fill in your env variables first_

