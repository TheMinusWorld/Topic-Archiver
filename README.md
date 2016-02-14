# Minus World Topic Archiver

This script parses Minus World forums. It relies on the Minus World HTML
template, which is custom, so it probably won't work anywhere else.

It has 3 parts:

1. Download topics and their contents and save it to a json file.
    (JSON is great for computers, not so much people)
2. Parse the json file into markdown files containing the
    entireity of the topic.
3. Alternatively, do the above but instead of saving markdown
    files add to github as issues.

You can also edit the config.yaml file to suit your needs, if it makes sense
to change any of it.

## Usage Example

After installing, make sure you're in the correct virtualenv:
`source venv/bin/activate`

### Read the suggestions forum

`./suggestions.py`

This'll generate a suggestions.json file. It'll take a while as it waits 5
seconds between each request by default! This is to not hammer the Minus World
server.

### Parse `suggestions.json` file

`./create-topic-markdown.py`

This'll generate a `topics` folder and make markdown files for each topic included, in the format of [topic number].md (example: `topics/20.md` would be the 'How to Suggest Things' thread)

### Post to Github Issues

`./post-to-github.py`

This'll ask for your github credentials and add issues to the
repo specified in `config.yaml`.
Github has a rate limit of about 60 requests per hour and will ban your account
if it detects you as a bot for some reason so use this with great care.


## Installation

This is built on Fedora 23 with this
[Python 3.5 COPR](https://synfo.github.io/2015/11/13/Python-3.5-in-Fedora/).
It'll probably work fine on other unix-like environments with the right
packages installed, and maybe even Windows if you know how to do that.

Mainly you'll need Python3.5, virtualenv, and pip to get started.

If you meet those requirements you can Install the other requirements with:

1. `virtualenv -p /usr/bin/python3.5 venv`
2. `source venv/bin/activate`
3. `/usr/bin/env python3.5 -m pip install -r ./requirements.txt`
4. `./update-requirements.sh`
    - (optional) for updating requirements to current version
        (may break things)
