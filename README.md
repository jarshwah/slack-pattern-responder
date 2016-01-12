# slack-regex-responder
Monitors all messages for regex patterns and returns a corresponding message.
I use this for turning ticket numbers into links.

## Work In Progress!

This is only toy code at the moment, as it's only my first time writing a
slack integration. The responses will be sent under the name of whatever user
registered the API token.

## Usage:

```
python responder.py -c ./responder.yaml
```

You want to make sure you've installed the requirements into a virtualenv
before running this though!

## Configuration:

See the `example.yaml` configuration file.


## Warning:

Make sure your regex pattern properly excludes your response from matching,
otherwise you'll get a nasty loop happening. I may add some checking to ensure
the response doesn't match the initial pattern, but this is all at your own
risk until then.

## Installation:

I'm not (yet) packaging this up, so I'm not providing any instructions. If you
can figure it out, then you can probably use it without my help.
