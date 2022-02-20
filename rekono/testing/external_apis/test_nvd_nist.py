from django.test import TestCase
from findings.enums import Severity
from findings.nvd_nist import NvdNist


class NvdNistTest(TestCase):
    '''Test cases for NVD NIST API.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.cve = 'CVE-2021-44228'                                             # Log4shell CVE
        self.old_cve = 'CVE-2010-4422'                                          # CVE with only CVSS version 2
        self.not_found_cve = 'CVE-0000-0000'                                    # Not found CVE

    def get_cve_data(self, cve: str, severity: str) -> None:
        '''Get CVE data from NVD NIST and check response.

        Args:
            cve (str): CVE code
            severity (str): Expected severity
        '''
        nvd_nist = NvdNist(cve)
        self.assertEqual(cve, nvd_nist.cve)
        self.assertEqual(nvd_nist.cve_reference_pattern.format(cve=cve), nvd_nist.reference)
        self.assertEqual(severity, nvd_nist.severity)

    def test_get_cve_data(self) -> None:
        '''Test get CVE data from NVD NIST feature.'''
        self.get_cve_data(self.cve, Severity.CRITICAL)

    def test_cve_data_not_found(self) -> None:
        '''Test get not found CVE data from NVD NIST feature.'''
        self.get_cve_data(self.not_found_cve, Severity.MEDIUM)

    def test_get_old_cve_data(self) -> None:
        '''Test get old CVE data from NVD NIST feature.'''
        self.get_cve_data(self.old_cve, Severity.HIGH)
