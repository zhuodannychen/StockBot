# StockBot

## Motivation
Financial illiteracy is an increasingly problem among college students. College students, mostly Amateurs, are afraid to trade and invest themselves because they have no experience, so discussing their thought process in a group of like-minded students is a good starting approach.

However, the problem with many group chats such as discord is that it doesn't offer resources to provide a clean way to discuss stocks. Example of some problems:
* Amateurs like to look at or follow Guru trades. However, in discord, it's hard for Guru's to specify when they will enter a trade and at what price (live trading). In this case, a discord bot command can specify the current price of a stock, and the Guru can use a bot command rather than using buy @here. This also allows amateurs to look at the trade afterwards and keep track of their paper trades.
* Amateurs want to know if their trade is successful, and one way is to use a bot stock forecast. However, note that markets are made up with emotions of greed and fear, which makes forecasting stock prices unreliable (at least of right now).
* Amateurs usually don't know what to pay attention to in premarket. Thus, the bot provides news and NASDAQ futures at 8:00 am for better preparation when market opens.

All of these functionalities will make it easier to discuss stocks on the discord group chat.

## Technical Documentation
#### To use the bot locally
1. Install Python 3.6 or above. Install Python [here](https://www.python.org/).

2. If using git, run ```git clone https://github.com/zhuodannychen/StockBot```
3. Run ```pip3 install -r requirements.txt``` to install dependencies.
4. Edit the required TOKENS with your own tokens in ```CONFIG.py```.
5. Run the bot with ```python3 bot.py```.
#### To invite the bot to a server
6. To add the bot to your server, go to this link and follow instructions. <https://discord.com/oauth2/authorize?client_id=759616214536028200&permissions=0&scope=bot>

#### How the Bot Works
For getting real time data, like the !price command, !triple, and !profile, the data is scrapped from [Yahoo Finance](https://finance.yahoo.com/) using [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).

For commands like !news and !snews, the [newsapi](https://newsapi.org/docs/client-libraries/python) is used to get headline news.

For sending news everyday at 8:00 am CDT, we use asyncio and datetime libraries to calculate the time until 8:00 am, then we call on commands of !news and !price.

For the forecast command, a LSTM model created with [Tensorflow](https://www.tensorflow.org/) was used to forecast the stock prices. The data comes from [alpha-vantage API](https://www.alphavantage.co/documentation/). alpha-vantage provides all historical data in [pandas](https://pandas.pydata.org/) format. However, we are only using the past 1200 days because the model trains quicker with a smaller data set. We also used an adam optimizer with mean squared error for loss.

## User Documentation
**!** prefix

**chart** - Returns a tradingview link of a given stock symbol. Tradingview provides advanced charts and indicators for trading.

--- Example: !chart tsla

**news** - Returns (usually 10) headline news from a given source. Default is bbc-news. Here are a list of credible sources:
* business-insider
* cbc-news
* cnn
* fortune
* google-news
* hacker-news
* nbc-news
* reuters

--- Example: !news

--- Example: !news cnn

**snews** -  Returns the headline news of a given stock symbol.

--- Example: !snews msft

**price** -  Returns the current price and percent change of a given stock.

--- Example: !price aapl

**profile** - Returns the profile/about info of a given stock.

--- Example: !profile AMZN

**triple** - Returns the current price and percent change of the three major index (NASDAQ, DJI, and S&P 500).

--- Example: !triple

**forecast** - Returns the forecast prices of the next 5 days, from top to bottom, for a given stock symbol. Note: this command can take up to 30 seconds before returning results.

--- Example: !forecast msft

If no stock symbol is inputted for any commands, MSFT will be used by default.

In addition, the bot sends news headlines and the premarket movement of NASDAQ 100 everyday at 8:00 am CDT.

## Improvements
* The current stock forecasting model is not very accurate, so a better model can be developed.
* The current forecasting command takes a long time to execute because we're training it on the command. Saving the model after training and then predicting could lead to a better result and faster execution. The only problem is we don't want to overfitt the data.
* The current training data does not provide adjusted open, adjusted high, and adjusted low, so stocks with recent splits cannot be accurately predicted.
* Matplotlib plots cannot be sent over discord messages, so plotting the day or week trend of a stock cannot be created using a command. Implementation for directly displaying charts on discord messages is still needed.
* More commands can be implemented, such as earnings data, analyst recommendations, etc.
