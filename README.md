# slack_responder
Monitors all messages for regex patterns and returns a corresponding message.
I use this for turning ticket numbers into links.

## Installation:

`pip3 install slack_responder`

## Configuration:

See the `example.yaml` configuration file. Sorry, that's not a lot of help,
but docs are on my todo list below :)

## Usage:

Create yourself a bot user, paste the token given to you into your config
file (just copy the example.yaml), and run.

```
slack_responder ./responder.yaml
```

See `config/upstart.conf` for an example of running this as a service. Pay
particular attention to the environment variables `LC_ALL` and `LANG` when
running under python 3.

## TODO:

- Docs
- Way more tests
- travis test integration
