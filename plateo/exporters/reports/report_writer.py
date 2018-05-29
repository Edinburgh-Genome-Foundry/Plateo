from ...version import __version__
from pdf_reports import ReportWriter
from sequenticon import sequenticon
import os

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_PATH = os.path.join(THIS_PATH, "templates")

def template_path(name):
    return os.path.join(TEMPLATES_PATH, name)

report_writer = ReportWriter(
    plateo_logo_url=os.path.join(TEMPLATES_PATH, 'imgs', 'logo.png'),
    version=__version__,
    default_stylesheets=(template_path("default_style.css"),)
)
