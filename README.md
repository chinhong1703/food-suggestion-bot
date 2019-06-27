# Food Suggestions Bot

This is a Telegram chatbot that provides the user with a suggestion of food options from Singapore. 

Main features are:
- Food suggestion from a database of local food
- Users can also add food into the database 
- Option to log the suggested food, or log and add your own food 

This is my personal project to experiment with the telegram bot API, using SQLalchemy with Postgresql and deploying to heroku using docker.

Database of food options are from the decomissioned [@dontthinkjusteat](https://t.me/dontthinkjusteat). Many thanks to the creators, this is just my implementation of their idea with a few of my own tweaks. 

## Getting Started

To create a telegram bot, you first need to create one from the system by talking to the Telegram Bot called BotFather. Then you will get an API token, which you must put it into the environment variable TOKEN. 

Antoher env variable MODE must be selected from 2 values: `dev`, and `prod` for the 2 ways of work: development (local) and production (heroku)

`HEROKU_APP_NAME` is the name of your application that you have created in Heroku. This is only used when deployed to heroku


Some codes are adapted from [this page](https://medium.com/python4you/creating-telegram-bot-and-deploying-it-on-heroku-471de1d96554)

### Prerequisites

```
Docker
```

### Installing

First make sure to install all the requirements using 
```
pip install -r requirements.txt
```

Then you have to set the environment variables:
```
MODE=dev
TOKEN=<your TOKEN from botfather>
```

And run application.py

```
python application.py
```

## Deployment

To deploy to heroku, you can follow the Heroku section from [this page](https://medium.com/python4you/creating-telegram-bot-and-deploying-it-on-heroku-471de1d96554)
