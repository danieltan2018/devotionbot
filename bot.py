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
from params import bottoken, channel
bot = telegram.Bot(token=bottoken)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global text
        if tag == 'p' or tag == 'br':
            tag = '\n'
        elif tag == 'strong' or tag == 'b':
            tag = '<b>'
        elif tag == 'em' or tag == 'i':
            tag = '<i>'
        elif tag == 'ul':
            tag = ''
        elif tag == 'li':
            tag = '- '
        else:
            tag = '<>'
        text += tag

    def handle_endtag(self, tag):
        global text
        if tag == 'strong' or tag == 'b':
            tag = '</b>'
        elif tag == 'em' or tag == 'i':
            tag = '</i>'
        elif tag == 'ul':
            tag = ''
        elif tag == 'li':
            tag = ''
        else:
            tag = ''
        text += tag

    def handle_data(self, data):
        global text
        text += data


def links(text):
    verses = re.findall(
        '[(](?:\d\s)?[A-Z][a-z]+[.]?\s\d+[:]\d+(?:[-]\d+)?[)]', text)
    for item in verses:
        item = item.strip('()')
        text = text.replace(
            item, '<a href="https://www.biblegateway.com/passage/?search={}&version=KJV">{}</a>'.format(item, item))
    return text


def new():
    global text
    text = ''
    feed = feedparser.parse("http://feeds.gty.org/gtystrengthfortoday&x=1")
    entry = feed.entries[0]
    title = entry.title
    title = '<b><u>{}</u></b>\n\n'.format(title)
    summary = entry.summary
    parser = MyHTMLParser()
    parser.feed(summary)
    text = text.split('<>')
    text = text[0].strip() + '\n\n<i>' + text[1] + 'www.crossway.com.</i>'
    text = links(text)
    text = title + text
    bot.send_message(chat_id=channel, text=text,
                     parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)


def main():
    schedule.every().day.at("07:00").do(new)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    main()
