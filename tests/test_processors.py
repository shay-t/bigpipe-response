import os
import unittest

from bigpipe_response.bigpipe import Bigpipe
from tests.test_utils import TestUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data.settings')

settings_file = os.path.join(os.path.realpath(os.getcwd()), 'data', 'bigpipe_settings.py')
Bigpipe.init(settings_file)
TestUtils.empty_output_folder(Bigpipe.get().config.RENDERED_OUTPUT_PATH)


class TestBigpipeProcessor(unittest.TestCase):

    def tearDown(self):
        print('shutdown Bigpipe')
        Bigpipe.get().shutdown()

    def test_css_manager(self):
        self.assertRaises(ValueError, Bigpipe.get().processors.run_processor, Bigpipe.get().config.CSS_PROCESSOR_NAME, 'paramsadasd')
        processor_result = Bigpipe.get().processors.run_processor(Bigpipe.get().config.CSS_PROCESSOR_NAME, 'main')
        fp = open(processor_result.output_file, "r")
        content = fp.read()
        fp.close()

        self.assertNotEqual(content, None)
        self.assertNotEqual(content, '')

    def test_js_manager(self):
        # Not existing component
        self.assertRaises(ValueError, Bigpipe.get().processors.run_processor, Bigpipe.get().config.JS_PROCESSOR_NAME, 'dasdasdasd')

        # Existing working component
        processor_result = Bigpipe.get().processors.run_processor(Bigpipe.get().config.JS_PROCESSOR_NAME, 'TestMainPage')
        fp = open(processor_result.output_file, "r")
        content = fp.read()
        fp.close()

        self.assertNotEqual(content, None)
        self.assertNotEqual(content, '')
        self.assertNotEqual(content.index('var TestSecondPage'), -1)
        self.assertNotEqual(content.index('TestMainPage'), -1)

        # Component with error
        with self.assertRaises(ValueError):
            Bigpipe.get().processors.run_processor(Bigpipe.get().config.JS_PROCESSOR_NAME, 'ComponentWithError')

        try:
            Bigpipe.get().processors.run_processor(Bigpipe.get().config.JS_PROCESSOR_NAME, 'ComponentWithError')
        except Exception as e:
            self.assertGreater(str(e).index('Expected corresponding JSX closing tag'), 0)