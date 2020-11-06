import os
import random

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from bs4 import BeautifulSoup
import requests
from newsapi import NewsApiClient

import asyncio
from datetime import datetime, timedelta

import forecasting
import CONFIG


load_dotenv(verbose=True)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# DISCORD_TOKEN = CONFIG.VARIABLES['DISCORD_TOKEN']

# NEWSAPI_TOKEN = os.getenv('NEWSAPI_TOKEN')
NEWSAPI_TOKEN = CONFIG.VARIABLES['NEWSAPI_TOKEN']
newsapi = NewsApiClient(api_key=NEWSAPI_TOKEN)

def get_news(source="bbc-news"):
    top_headlines = newsapi.get_top_headlines(sources=source)
    news_articles = top_headlines['articles']
    embed = discord.Embed(
        title = 'News',
        colour = discord.Colour.green()
    )
    embed.set_footer(text="News from " + source)
    for l in news_articles:
        embed.add_field(name=l["title"], value=l["description"], inline=False)
        embed.add_field(name=l["url"], value=l["publishedAt"], inline=False)
    return embed


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("bot is ready")

@tasks.loop(hours=24)
async def called_once_a_day():
    URL = "https://finance.yahoo.com/quote/^QMI"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    premarket = ""
    try:
        current_price = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[0]
        change = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[1]
        premarket = "NASDAQ 100 Pre Market\t" + current_price.text + "\t" + change.text
    except:
        premarket = "No data found"

    for guild in bot.guilds:
        for channel in guild.channels:
            try:
                embed = get_news()
                await channel.send(embed=embed)
                await channel.send(premarket)
            except Exception:
                continue

@called_once_a_day.before_loop
async def before():
    n = datetime.now()
    tomorrow = datetime.now() + timedelta(1)
    morning = datetime(year=tomorrow.year, month=tomorrow.month, 
                        day=tomorrow.day, hour=13, minute=00, second=0)
    left = (morning - datetime.now()).seconds
    await asyncio.sleep(left)
    await bot.wait_until_ready()

@bot.command(name='chart', help='Returns a tradingview link of a given stock symbol.')
async def chart(ctx, quo="MSFT"):
    response = "https://www.tradingview.com/symbols/" + quo
    await ctx.send(response)

@bot.command(name='price', help='Returns the current price and percent change of a given stock.')
async def price(ctx, quo="MSFT"):
    URL = "https://finance.yahoo.com/quote/" + quo
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        current_price = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[0]
        change = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[1]
        await ctx.send(quo.upper() + "\t" + current_price.text + "\t" + change.text)
    except:
        await ctx.send("No data found")

@bot.command(name='profile', help='Returns the profile/about info of a given stock.')
async def profile(ctx, quo="MSFT"):
    URL = "https://finance.yahoo.com/quote/" + quo + "/profile"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        profile = soup.find_all("section", {"class": "quote-sub-section Mt(30px)"})[0].find_all("p")[0].text
        await ctx.send(profile)
    except:
        await ctx.send("No data found")

@bot.command(name='triple', help='Returns the current price and percent change of the three major index (NASDAQ, DJI, and S&P 500).')
async def triple(ctx):
    channel = ctx.message.channel
    embed = discord.Embed(
        title = 'Triple Index',
        colour = discord.Colour.blue()
    )

    embed.set_footer(text="Data from Yahoo Finance")
    await ctx.send("Searching for data...")

    three = [["NASDAQ", "^ixic"], ["DJI", "^dji"], ["S&P 500", "^gspc"]]
    indexname = ""
    indexprice = ""
    indexchange = ""
    for i in range(3):
        URL = "https://finance.yahoo.com/quote/" + three[i][1]
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            current_price = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[0]
            change = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[1]
            indexname += three[i][0] + "\n"
            indexprice += current_price.text + "\n"
            indexchange += change.text + "\n"
        except:
            indexname += three[i][0] + "\n"
            indexprice += "No data found\n"
            indexchange += "No data found\n"

    embed.add_field(name="Index", value=indexname, inline=True)
    embed.add_field(name="Price", value=indexprice, inline=True)
    embed.add_field(name="Change", value=indexchange, inline=True)
        
    await ctx.send(embed=embed)

@bot.command(name="news", help="Returns (usually 10) headline news from a given source. Default is bbc-news.")
async def news(ctx, source="bbc-news"):
    await ctx.send("Searching for news...")
    embed = get_news(source)
    await ctx.send(embed=embed)

@bot.command(name="snews", help="Returns the headline news of a given stock symbol.")
async def snews(ctx, quo="MSFT"):
    top_headlines = newsapi.get_everything(q=quo)
    news_articles = top_headlines['articles']
    embed = discord.Embed(
        title = 'News',
        colour = discord.Colour.green()
    )
    await ctx.send("Searching for news...")

    embed.set_footer(text="News for " + quo)
    for i in range(min(10, len(news_articles))):
        embed.add_field(name=news_articles[i]["title"], value="-", inline=False)
        embed.add_field(name=news_articles[i]["url"], value=news_articles[i]["publishedAt"], inline=False)
    await ctx.send(embed=embed)

@bot.command(name="forecast", help="Returns the forecast prices of the next 5 days, from top to bottom, for a given stock symbol.")
async def forecast(ctx, quo="MSFT"):
    await ctx.send("Training model...")
    await ctx.send(forecasting.forecasting_stock(quo))
    await ctx.send("Finished forecasting")

called_once_a_day.start()
bot.run(DISCORD_TOKEN)

