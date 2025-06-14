import math
import pandas as pd
import numpy as np
import random
import json
import datetime as dt
import collections

preloaded_globals = {
    "__builtins__": __builtins__,  # Allow built-in functions like len, range, etc.
    "pd": pd,
    "np": np,
    "math": math,
    "random": random,
    "json": json,
    "datetime": dt,
    "collections": collections,
}