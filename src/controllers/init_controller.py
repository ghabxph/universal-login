from flask import Response


class InitController:

    def __init__(self):
        pass

    def index(self):

        # Returns the html page
        with open('/html/init/index.html') as html:
            return html.read()
