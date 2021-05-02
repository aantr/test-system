#!/usr/bin/python3
import os
import sys
import logging

logging.basicConfig(stream=sys.stderr)
path = os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0, path)
from main import app as application
