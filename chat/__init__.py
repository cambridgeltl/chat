import logging

from flask import Flask

from config import DEBUG, DUMMY_DBS, TRIM_BLOCKS
from config import PUBMED_TEXT_DIR, PUBMED_ANN_DIR, INDEX_PATH

from fsstore import PubmedStore, AnnotationStore

if DUMMY_DBS:
    from dummydb import DataController
else:
    from DataController import DataController

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)

pubmed_text_store = PubmedStore(PUBMED_TEXT_DIR)
pubmed_ann_store = AnnotationStore(PUBMED_ANN_DIR)

db_controller = DataController(INDEX_PATH)
db_controller.open()

app = Flask(__name__)
app.jinja_env.trim_blocks = TRIM_BLOCKS

from chat import views
