import os
import shutil

from django.test import TestCase
from rekono.settings import LOGGING_DIR, REKONO_HOME, REPORTS_DIR, WORDLIST_DIR
from system.models import System


class RekonoTestCase(TestCase):
    '''Base test case for all tests.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.system = System.objects.first()
        self.system.defect_dojo_url = 'http://127.0.0.1:8080'                   # Testing URL due to coverage reasons
        self.system.upload_files_max_mb = 1                                     # Reduce max size allowed
        self.system.save(update_fields=['defect_dojo_url', 'upload_files_max_mb'])
        for dir in [REKONO_HOME, REPORTS_DIR, WORDLIST_DIR, LOGGING_DIR]:       # Initialize directories if needed
            if not os.path.isdir(dir):
                os.mkdir(dir)

    def tearDown(self) -> None:
        '''Run code after run tests.'''
        super().tearDown()
        if os.path.isdir(REKONO_HOME):                                          # Remove testing directories if exist
            shutil.rmtree(REKONO_HOME)
