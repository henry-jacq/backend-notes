

# Under the Hood: HTTP

HTTP is a protocol built on top of TCP.

So, HTTP is basically a TCP connection with a defined structure for communication between systems over the internet.

## Request and Response

An HTTP request or response has a header and a body.

- The header carries information such as who is sending it, what kind of data is being sent, and where it is going.
- The body contains the actual data, also called the payload.

## Simple Server Idea

We can build our own HTTP server by opening a socket on a port and handling structured HTTP requests and responses. Once the server speaks the correct HTTP format, a browser can understand it.

## Behind Server Technologies

This is the basic working model behind server technologies such as Apache, Tomcat, and Nginx.

