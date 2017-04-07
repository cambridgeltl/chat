import logging

from flask import Flask

from config import DEBUG, INDEX_PATH

from DataController import DataController

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)

controller = DataController(INDEX_PATH)
controller.open()
logging.debug('controller.open() returned')

app = Flask(__name__)

from dbconnector import views
