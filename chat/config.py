# Flask debug mode
DEBUG = False    # True

# Development mode (error message detail)
DEVEL = True

# Dummy DBs (development feature)
DUMMY_DBS = False

# Port to listen on
PORT = 80    # 5001


# Parameter idenfitying the pmids string
PMIDS_PARAMETER = 'pmids'

# Parameter idenfitying the query string
QUERY_PARAMETER = 'q'

# Parameter identifying the hallmark filter
HALLMARK_PARAMETER = 'hm'

# http://jinja.pocoo.org/docs/templates/#whitespace-control
TRIM_BLOCKS = True

# Number of seconds to sleep after a request (being nice to NCBI services).
ESEARCH_WAIT_TIME = 1

# Directories containing documents in subdirectories corresponding to
# filename prefixes.
PUBMED_TEXT_DIR = '/srv/chat/pubmed-texts'
PUBMED_ANN_DIR = '/srv/chat/hallmark-annotations'

# Path to Lucene index
try:
    from localconfig import INDEX_PATH
except ImportError:
    INDEX_PATH = '/srv/chat/INDEX/'

# Default chart settings
DEFAULT_CHART = 'doughnut'
DEFAULT_MEASURE = 'npmi'
