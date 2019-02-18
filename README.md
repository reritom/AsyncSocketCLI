# Async Socket CLI

AsyncSocketCLI is a simple python3 command line interface for connecting to a socket server and sending and receiving messages.

## How to use

This CLI has one mandatory parameter, the socket server port, and one optional parameter, the address/host.
If the address isn't specified, the localhost address will be determined and targetted.

From the command line run:
`python socket_cli.py -a XXXXX -p YYYYY`

or just:
`python socket_cli.py -p YYYYY`

Assuming a successful connection, you will then be prompted to send messages through the command line.
To exit, either enter '/kill', '/exit' or '' (an empty input).
In the case that the connection has been closed, any value you enter will result in the session ending.

### Logging
To support asynchronous messages from the socket server, the 'read' messages aren't logged in the command line, and are instead logged, with the request messages, in a app.log.

It is adviced to run the CLI in one terminal, and then use something like tails in another terminal to monitor the complete exchanges:

`tail -f app.log`
