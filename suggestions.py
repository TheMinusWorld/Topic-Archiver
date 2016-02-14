#!/usr/bin/env python
import sys
import regex
import requests
import time
import json
import yaml
from bs4 import BeautifulSoup
from html2text import html2text
from urllib.parse import urlencode


def local2utc(secs):
    if time.daylight:
        return secs - time.timezone - time.altzone
    else:
        return secs - time.timezone


def get_total_topics(soup):
    # Pass entire page soup, get the total topics
    count = soup.find(id="pagecontent")\
                .find('table')\
                .find_all('td')
    count_string = count[2].string
    count_match = regex.search('([\d,]+)', count_string)
    if count_match:
        count = count_match.group(1).replace(',', '')
    else:
        count = 0
    return int(count)


def get_topics(soup, topics):
    topic_rows = soup.find(id="pagecontent")\
        .find('table', {'class': 'tablebg'})\
        .find_all('tr')
    for topic in topic_rows:
        columns = topic.find_all('td')
        if len(columns) <= 1:
            continue
        last_post_date = time.strptime(columns[5].find('p').string,
                                       '%a %b %d, %Y %I:%M %p')
        topic_title = columns[1].a.string
        topic_number = regex.search('t=(\d+)', columns[1].a['href'])
        if topic_number:
            topic_number = int(topic_number.group(1))
            if not topics.get(topic_number, False):
                topic = {
                    'id': topic_number,
                    'title': topic_title,
                    'last_post': int(local2utc(
                        time.mktime(last_post_date)
                    )),
                }
                topics[topic_number] = topic
    return topics


def get_total_posts(soup):
    count = soup.find(id="pagecontent")\
                .find('table')\
                .find_all('td')
    count_string = count[2].string
    count_match = regex.search('([\d,]+)', count_string)
    if count_match:
        count = count_match.group(1).replace(',', '')
    else:
        count = 0
    return int(count)


def get_posts(soup, posts):
    post_tables = soup.find(id="pagecontent")\
        .find_all('table', {'class': 'intopic'})
    for post in post_tables:
        rows = post.find_all('tr')
        if len(rows) <= 1:
            continue
        postinfo = post.find('td', {'class': 'gensmall'})
        title = postinfo.find('div', {'style': 'float: left;'})
        if title is None:
            continue
        title = title.find_all(text=True)[2].strip()
        date = postinfo.find('div', {'style': 'float: right;'})\
            .find_all(text=True)[1].strip()
        date = time.strptime(date, '%a %b %d, %Y %I:%M %p')
        post_id = postinfo.find('div', {'style': 'float: right;'})\
                          .find('a')['href']
        post_id = regex.search('p=(\d+)', post_id)
        if post_id:
            post_id = int(post_id.group(1))
        else:
            continue
        post_content = post.find('div', {'class': 'postbody'})\
            .decode_contents(formatter="html")
        authorA = post.find('td', {'class': 'postheadercell'})\
            .find('a', {'class': 'postauthor'})
        author_name = authorA.string
        author_id = regex.search('u=(\d+)', authorA['href'])
        if author_id:
            author_id = int(author_id.group(1))
        else:
            continue
        post = {
            'id': post_id,
            'title': title,
            'author': {
                'id': author_id,
                'name': author_name,
            },
            'time': int(local2utc(time.mktime(date))),
            'post': html2text(post_content),
        }
        posts.append(post)
    return posts


def main(argv, file):
    configfile = open('config.yaml', 'r')
    with configfile:
        config = yaml.load(configfile)
    per_page = config['forum']['topics_per_page']
    time.sleep(config['sleep'])
    forum_url = config['forum']['url'] + '?' +\
        urlencode({
            config['forum']['attribute']: config['forum']['id']
        })
    suggestions = requests.get(forum_url)
    topics = {}
    if suggestions.status_code == 200:
        soup = BeautifulSoup(suggestions.text, 'html.parser')
        total_topics = get_total_topics(soup)
        topics = get_topics(soup, topics)
    current_page = per_page
    while current_page <= total_topics:
        time.sleep(config['sleep'])
        forum_page_url = config['forum']['url'] + '?' +\
            urlencode({
                config['forum']['attribute']: config['forum']['id'],
                config['page_attribute']: current_page,
            })
        suggestions = requests.get(forum_page_url)
        if suggestions.status_code == 200:
            soup = BeautifulSoup(suggestions.text, 'html.parser')
            topics = get_topics(soup, topics)
        current_page += per_page

    topics_list = []
    for i, topic in topics.items():
        if topic.get('last_post', False):
            topics_list.append(topic)
    topics_list.sort(key=lambda x: x['last_post'])
    topics = topics_list
    for topic in topics:
        per_page = config['topic']['posts_per_page']
        time.sleep(config['sleep'])
        topic_url = config['topic']['url'] + '?' +\
            urlencode({
                config['forum']['attribute']: config['forum']['id'],
                config['topic']['attribute']: topic['id'],
            })

        topic_page = requests.get(topic_url)
        posts = []
        if topic_page.status_code == 200:
            soup = BeautifulSoup(topic_page.text, 'html.parser')
            total_posts = get_total_posts(soup)
            if total_posts < 1:
                continue
            posts = get_posts(soup, posts)

        current_page = per_page
        while current_page <= total_posts:
            time.sleep(config['sleep'])
            topic_page_url = config['topic']['url'] + '?' +\
                urlencode({
                    config['forum']['attribute']: config['forum']['id'],
                    config['topic']['attribute']: topic['id'],
                    config['page_attribute']: current_page,
                })
            topic_page = requests.get(topic_page_url)
            if topic_page.status_code == 200:
                soup = BeautifulSoup(topic_page.text, 'html.parser')
                posts = get_posts(soup, posts)

            current_page += per_page

        topic['posts'] = posts

    output = open(config['output'], 'w')
    with output:
        output.write(json.dumps(topics))


if __name__ == "__main__":
    main(argv=sys.argv[1:], file=sys.argv[0])
