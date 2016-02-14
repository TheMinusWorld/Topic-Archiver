#!/usr/bin/env python
import sys
import json
import yaml
from datetime import datetime, timedelta
from os import linesep, sep, path, makedirs
from urllib.parse import urlencode


def main(argv, file):
    configfile = open('config.yaml', 'r')
    with configfile:
        config = yaml.load(configfile)
    if config.get('output', False):
        suggestions = open(config['output'], 'r')
    with suggestions:
        topics = json.load(suggestions)
    script_path = path.abspath(__file__)
    script_dir = path.split(script_path)[0]
    if not path.exists(sep.join([script_dir, 'topics'])):
        makedirs(sep.join([script_dir, 'topics']))
    for topic in topics:
        if topic.get('posts', False):
            posts = len(topic['posts'])
        else:
            posts = 0
        if posts > 0:
            threadfile = open(
                sep.join([
                    script_dir,
                    'topics',
                    str(topic['id']) + '.md']), 'w+')
            with threadfile:
                for post in topic['posts']:
                    post_url = config['post']['url'] + '?' +\
                        urlencode({
                            config['post']['attribute']: post['id']
                        })
                    if config['post'].get('hash', False):
                        post_url += '#' +\
                            str(config['post']['hash']).format(id=post['id'])
                    author_url = config['user']['url'] + '?' +\
                        urlencode({
                            config['user']['attribute']: post['author']['id'],
                            'mode': config['user']['mode'],
                        })
                    time = datetime.fromtimestamp(post['time']) + \
                        timedelta(hours=9)
                    time = time.strftime('%a %b %d, %Y %I:%M %p')
                    post_link = '[' + post['title'] + '](' + post_url + ')'
                    author_link =\
                        '[' + post['author']['name'] + '](' + author_url + ')'

                    post_lines = post['post'].split(linesep)
                    new_post_lines = []
                    for line in post_lines:
                        line = '> '+line
                        new_post_lines.append(line)
                    threadfile.write(
                        time + ' ' + post_link + ' by ' + author_link + ':' +
                        linesep
                    )
                    threadfile.write(
                        str(linesep).join(new_post_lines) +
                        2*linesep
                    )


if __name__ == "__main__":
    main(argv=sys.argv[1:], file=sys.argv[0])
