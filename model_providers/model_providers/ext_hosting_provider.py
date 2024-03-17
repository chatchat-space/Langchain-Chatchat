from flask import Flask

from model_providers.core.hosting_configuration import HostingConfiguration

hosting_configuration = HostingConfiguration()


def init_app(app: Flask):
    hosting_configuration.init_app(app)
