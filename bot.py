# pip install feedparser
import feedparser
from html.parser import HTMLParser
import re

# pip install python-telegram-bot
# pip install schedule
import telegram
import logging
import schedule
import time
from params import bottoken
bot = telegram.Bot(token=bottoken)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


feed1 = 'http://feeds.gty.org/gtystrengthfortoday&x=1'
channel1 = '@strengthfortoday'

feed2 = 'http://feeds.gty.org/gtydrawingnear&x=1'
channel2 = '@drawingnear'


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global text
        if tag == 'p' or tag == 'br':
            tag = '\n'
        elif tag == 'strong' or tag == 'b' or tag.startswith('h'):
            tag = '<b>'
        elif tag == 'em' or tag == 'i':
            tag = '<i>'
        elif tag == 'ul':
            tag = ''
        elif tag == 'li':
            tag = '- '
        elif tag == 'g':
            tag = ''
        else:
            tag = '<>'.format(tag)
        text += tag

    def handle_endtag(self, tag):
        global text
        if tag == 'strong' or tag == 'b' or tag.startswith('h'):
            tag = '</b>'
        elif tag == 'em' or tag == 'i':
            tag = '</i>'
        elif tag == 'ul':
            tag = ''
        elif tag == 'li':
            tag = ''
        elif tag == 'p':
            tag = ''
        else:
            tag = ''
        text += tag

    def handle_data(self, data):
        global text
        text += data


def links(text):
    text = text.split('\n')
    newtext = []
    for passage in text:
        verses = re.findall(
            '(?:\d\s)?[A-Z][a-z]+[.]?\s\d+[:]\d+(?:[-]\d+)?(?:[—]\d+[:]\d+)?(?:[,]\s\d+)?(?:[;]\s\d+[:]\d+(?:[-]\d+)?)?', passage)
        verses = set(verses)
        for item in verses:
            passage = passage.replace(
                item, '<a href="https://www.biblegateway.com/passage/?search={}&version=KJV">{}</a>'.format(item, item))
        newtext.append(passage)
    newtext = '\n'.join(newtext)
    return newtext


def getfeed(feedurl):
    global text
    text = ''
    feed = feedparser.parse(feedurl)
    entry = feed.entries[0]
    title = entry.title
    title = '<b><u>{}</u></b>\n\n'.format(title)
    summary = entry.summary
    parser = MyHTMLParser()
    parser.feed(summary)
    splittext = text.split('<>')
    text = []
    for item in splittext:
        if item.strip() != '':
            text.append(item)
    text = text[0].strip() + '\n\n<i>' + text[1] + 'www.crossway.com.</i>'
    text = links(text)
    text = title + text
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    while '  ' in text:
        text = text.replace('  ', ' ')


def send(channel):
    bot.send_message(chat_id=channel, text=text,
                     parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)


def command():
    getfeed(feed1)
    try:
        send(channel1)
    except:
        bot.send_message(chat_id=channel1, text='_We are facing technical difficulties and are unable to send this message_',
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)

    getfeed(feed2)
    try:
        send(channel2)
    except:
        bot.send_message(chat_id=channel2, text='_We are facing technical difficulties and are unable to send this message_',
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)


def override():
    getfeed(feed1)
    print(text)
    send(channel1)


def main():

    schedule.every().day.at("06:00").do(command)
    print("Bot running: task scheduled.")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    main()
