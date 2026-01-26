"""
Global Property of the Instrument.
"""

from .utility import load_json


PROPERTIES: dict = {

}


# Load global setting from json file.
PROPERTIES_FILENAME: str = "vt_instrument_property.json"
PROPERTIES.update(load_json(PROPERTIES_FILENAME))
