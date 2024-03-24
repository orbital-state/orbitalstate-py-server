def main(config_object=None):
    """Main entry point for web-server implementing orbital-protocol."""
    from .api import create_app
    if not config_object:
        config_object = "orbitalstate.server.config.BaseConfig"
    app = create_app(config_object)
    app.run()
