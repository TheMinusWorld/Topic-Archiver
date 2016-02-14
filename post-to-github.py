#!/usr/bin/env python
import sys
import json
import yaml
from github import Github
from datetime import datetime, timedelta
from os import linesep
from urllib.parse import urlencode


def main(argv, file):
    configfile = open('config.yaml', 'r')
    with configfile:
        config = yaml.load(configfile)
    if config.get('output', False):
        suggestions = open(config['output'], 'r')
    github_user = input("Enter Github username: ")
    github_password = input("Enter Github password: ")
    g = Github(github_user, github_password)
    try:
        g.get_user().name
    except:
        print('Invalid Credentials')
        exit(1)
    print('Successful Login!')
    try:
        g.get_repo(config['repo']).name
    except:
        print('Invalid repo!')
        exit(1)
    repo = g.get_repo(config['repo'])
    print(repo.name, 'loaded')
    label = None
    for l in repo.get_labels():
        if l.name == config['label']['name']:
            label = l
        print(l.name)
    if label is None:
        label = repo.create_label(
            name=config['label']['name'],
            color=config['label']['color']
        )
        print(label.name, 'created')
    with suggestions:
        topics = json.load(suggestions)
    for topic in topics:
        if topic.get('posts', False):
            posts = len(topic['posts'])
        else:
            posts = 0
        if posts > 0:
            author = topic['posts'][0]['author']
            topic_string =\
                str(topic['id']) + ' ' + str(posts) + ' ' + topic['title'] +\
                ' by ' + author['name']
            import_thread = input('Import ' + topic_string + '? [y/N] ')
            if import_thread[0].lower() == 'y':
                issue_title = 'Imported: ' + topic['title']
                issue_contents = 'Imported issue' + linesep + linesep
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
                    issue_contents +=\
                        time + ' ' + post_link + ' by ' + author_link + ':' +\
                        linesep
                    issue_contents +=\
                        str(linesep).join(new_post_lines) +\
                        2*linesep
                repo.create_issue(
                    issue_title,
                    body=issue_contents,
                    labels=[label]
                )


if __name__ == "__main__":
    main(argv=sys.argv[1:], file=sys.argv[0])
