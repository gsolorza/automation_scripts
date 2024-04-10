from genie import testbed
from pprint import pprint

testbed = testbed.load('testbed.yaml')
devices = testbed.connect()
