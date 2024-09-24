import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from dags.update_company_info.download_listed_company import DownloadListedCompanies

class TestDownloadListedCompanies(unittest.TestCase):
    webdriver = DownloadListedCompanies.open_web_browser()
    
    def setUp(self):
        self = DownloadListedCompanies.open_web_browser
        
    def test_open_web_browser(self):
        self.assertEqual(self.webdriver.monoid[1], True)
        
    
    def test_close_web_browser(self):
        test_webdriver = DownloadListedCompanies.open_web_browser().value
        self.assertEqual(DownloadListedCompanies.close_web_browser(test_webdriver).monoid[1], True)
        
    def test_go_url(self):
        url = 'https://www.google.com'
        test_webdriver = DownloadListedCompanies.open_web_browser().value
        web = DownloadListedCompanies.go_url(url)(test_webdriver)
        result = web.value.driver.title
        self.assertEqual(result, 'Google')

if __name__ == '__main__':
    unittest.main()