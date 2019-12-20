import os
import re
import json
from django.utils.translation.trans_real import DjangoTranslation

from bigpipe_response.processors.base_processor import BaseProcessor
from bigpipe_response.processors.processor_result import ProcessorResult


class I18nProcessor(BaseProcessor):

    def __init__(self, processor_name: str):
        BaseProcessor.__init__(self, processor_name, 'json')

    def run(self, source: str, options: dict = {}, include_dependencies: list = [], exclude_dependencies: list = []):
        super().run(source, options, include_dependencies, exclude_dependencies)

        if not options: raise ValueError('I18nProcessor [options] must be set')
        if 'i18n_dependencies' not in options or not options['i18n_dependencies']: raise ValueError('I18nProcessor expect options to contain \'i18n_dependencies\' list to filter')
        if 'language' not in options or not options['language']: raise ValueError('I18nProcessor expect options to contain \'language\' ')

        input_file = '{}_{}'.format(source.replace('.', '_'), options['language'])
        output_file = self.build_output_file_path(input_file, include_dependencies, exclude_dependencies)
        if not os.path.isfile(output_file):
            self.process_resource(source, output_file, include_dependencies, exclude_dependencies, options)

        return ProcessorResult([], output_file)

    def render(self, source: str, context: dict, i18n: dict):
        return self.render_resource(source, context, i18n)

    def process_resource(self, source: str, output_file: str, include_dependencies: list, exclude_dependencies: list, options: dict = {}):
        translation = DjangoTranslation(options['language'])
        new_pattern = '|'.join(['({})'.format(pattern) for pattern in options['i18n_dependencies']])
        result = {}
        for key, value in translation._catalog.items():
            if isinstance(key, str) and re.match(new_pattern, key):
                result[key] = value

        with open(output_file, 'w+') as fp:
            json.dump(result, fp)
            fp.close()

    def render_resource(self, input: str, context: dict, i18n: dict):
        raise ValueError('render is not supported for internalization')