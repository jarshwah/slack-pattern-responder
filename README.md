# slack_responder
Monitors all messages for regex patterns and returns a corresponding message.
I use this for turning ticket numbers into links.

## Work In Progress!

This is only toy code at the moment, as it's only my first time writing a
slack integration. The responses will be sent under the name of whatever user
registered the API token.

## Usage:

Create yourself a bot user, paste the token given to you into your config
file (just copy the example.yaml), and run.

```
python slack_responder.py -c ./responder.yaml
```

## Configuration:

See the `example.yaml` configuration file.


## Warning:

Make sure your regex pattern properly excludes your response from matching,
otherwise you'll be told to fix your pattern. There's probably a better way
of checking this (like detecting the username..) but I haven't looked too hard.

## Installation:

I'm not (yet) packaging this up, so I'm not providing any instructions. If you
can figure it out, then you can probably use it without my help.

## TODO:

- Docs
- Way more tests
- travis test integration
- pypi
- logging (click.echo)

