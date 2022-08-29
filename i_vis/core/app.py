from typing import Optional
import os

from flask import Flask
import pandas as pd

from .config import variable_name, Default as DefaultConfig, MissingConfig


def create(name: str, config: Optional[type] = None) -> Flask:
    app = Flask(name)
    app.config.from_object(DefaultConfig)

    # dispatch on provided config type
    if config:
        app.config.from_object(config)
    else:
        # load configuration
        config_fname = variable_name("CONF")
        if os.environ.get(config_fname):
            app.config.from_envvar(config_fname)
        else:
            raise MissingConfig(f"Missing environment variable: '{config_fname}'")

    if app.config.get("TESTING"):
        pd.options.mode.chained_assignment = "raise"

    return app
