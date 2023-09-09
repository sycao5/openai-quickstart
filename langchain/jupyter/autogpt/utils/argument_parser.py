import argparse

class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='A translation tool that supports translations in any language pair.')
        self.parser.add_argument('--config_file', type=str, default='config.yaml', help='Configuration file with API keys.')
        self.parser.add_argument('--SERPAPI_API_KEY', type=str, help='serpapi api key.')
        self.parser.add_argument('--OPENAI_API_KEY', type=str, help='openai api key.')

    def parse_arguments(self):
        args = self.parser.parse_args()
        return args
