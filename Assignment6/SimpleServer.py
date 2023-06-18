import http.server
from urllib.parse import urlparse, unquote_plus

'''
File: SimpleServer.py
Author: Chris Piech
---------------------
This file makes it so that students can easily turn their python
program into a dead-simple HTTP server. The server only handles
GET HTTP requests (which is more than enough really). To use this,
in your program implement a class that has a function called

  handle_request

Then you can call the run_server function and pass in an instance
of that class. Every time a GET request is made, the request will
be forwarded on to your class! It is a good time. Welcome to the
world of backend servers, friend.
'''

# the default port on which you run your server
DEFAULT_PORT = 8000

def run_server(server_handler, port=8000):
    """
    This is the public function that you should use. Call this function
    and pass in an instance of a class that supports handle_request. You
    can optionally specify a port to run the server on. This function
    does not return. Instead it serves forever. Anytime a request comes
    in it gets passed to your server_handler
    """
    # build the class that has the handler bound to the get request
    server_class = _make_server_class(server_handler)
    # run the server on localhost
    server_address = ('', port)
    # built off the python http.server module
    httpd = http.server.HTTPServer(server_address, server_class)
    print('Server running on port ' + str(port) + '...')
    httpd.serve_forever()

class Request:
    """
    The request class packages the key information from an internet request.
    An internet request has both a command and a dictionary of parameters.
    This class defines a special function __str__ which means if you have an
    instance of a request you can put it in a print function.
    """
    def __init__(self, request_command, request_params):
        # every request has a command (string)
        self.command = request_command
        # every request has params (dictionary). Can be {}
        self.params = request_params

    def get_params(self):
        # a 'getter' method to get the params
        return self.params

    def get_command(self):
        # a 'getter' method to get the command
        return self.command

    def __str__(self):
        # a special method which overrides what happens when you 'print' a request
        return str(self.__dict__)

class _SimpleServer(http.server.BaseHTTPRequestHandler):
    """
    This SimpleServer handles GET requests! But it must be overloaded
    by a class that implements handle_request
    """

    def get_query_params(self):
        """
        Turn the query parameters into a nice dictionary to pass back
        to the handle_request function!
        """
        query = urlparse(self.path).query
        query_dict = {}
        parts = query.split('&')
        for part in parts:
            if '=' not in part:
                continue
            key = part.split('=')[0]
            # url strings are encoded (eg space becomes a +). This decodes.
            value = unquote_plus(part.split('=')[1])
            query_dict[key] = value
        return query_dict

    def do_GET(self):
        # who cares about a favicon... :-)
        if self.path == '/favicon.ico':
            return

        # extract the command
        raw_command = urlparse(self.path).path
        command = raw_command.replace('/', '')

        # extract the query parameters
        query_params = self.get_query_params()

        # make the request object
        request = Request(command, query_params)

        # call handle_request (this re-routes to the user fn)!
        reply = self.handle_request(request)

        # package the response up in order to send it back to the requester
        reply = reply.encode()
        # build a successful response with proper headers
        self.send_response(200)
        self.send_header("Content-type", "text")
        # necessary if you want requests from other sources!
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        # the wfile is the stream to which the internet is connected...
        self.wfile.write(reply)

    def log_message(self, format, *args):
        # this function silences the server so it doesn't print out messages
        return

def _make_server_class(server_handler):
    """
    This class is terribly important 'glue'. It serves the purpose of
    binding the student's class (which implements handle_request) into
    a subclass of _SimpleServer.
    """
    class _CustomServer(_SimpleServer):
        def handle_request(self, request):
            return server_handler.handle_request(request)

    # Returns a class. Wild.
    return _CustomServer


