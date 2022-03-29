# Conversion Server
Module maintained by @NevisKing

This module exists to recieve npy files in the form of HTTP request bodys, convert them to a specific JSON format and then
serve that json as a response body.

To run the server use  
``python ConversionServer/mysite/manage.py runserver``  
To expose the server to the internet use  
``ngrok HTTP 8000``  
Then send requests to either address but make sure to add the  '/convert/' endpoint
to the url