
## Run Locally

- Clone the project

```bash
  git clone https://github.com/Daneil98/Algorithmic_Trading
```


- Go to the project directory

```bash
  cd Algorithmic_Trading
```


- Install the dependencies

```bash
  pip install -r requirements.txt

```

- Go to the folder directory

```bash
  cd Mean Reversion Bot
```


- Start the Trading Bot

```bash
  python3 reversion_bot.py
```


## Features

- A Trading bot that connects to MetaTrader5 via Blueberry and uses the mean reversion strategy on the preselected commodity and gives live trade updates every second in the terminal.

## Environment Variables

To run this project, you will need to register an account with Blueberry(MetaTrader5) and add the following environment variables to your config files in both subfolders
  
login_number = xxxxxx (Gotten from Blueberry Account) 
path = r'' (Gotten from Installed Blueberry App)
