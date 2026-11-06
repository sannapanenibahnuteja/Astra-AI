import unittest
from unittest.mock import patch, Mock
from desktop.web_access import endpoint,fetch,PublicWeb,PageText,research_request


class PublicWebTests(unittest.TestCase):
    def dns(self,ip):return [(2,1,6,'',(ip,443))]
    def test_fetch_caps_body_and_closes_connection(self):
        response=Mock(status=200)
        response.getheader.side_effect=lambda name,default=None: {'Content-Type':'text/plain'}.get(name,default)
        response.read1.side_effect=[b'x'*16384]*17
        with patch('desktop.web_access.socket.getaddrinfo',return_value=self.dns('8.8.8.8')),patch('desktop.web_access.PinnedHTTPS') as factory:
            connection=factory.return_value;connection.getresponse.return_value=response
            with self.assertRaisesRegex(ValueError,'bounded reading limit'):fetch('https://example.com')
            connection.close.assert_called_once()
    def test_fetch_revalidates_redirect_before_private_connection(self):
        response=Mock(status=302);response.getheader.return_value='https://127.0.0.1/private'
        with patch('desktop.web_access.socket.getaddrinfo',side_effect=[self.dns('8.8.8.8'),self.dns('127.0.0.1')]),patch('desktop.web_access.PinnedHTTPS') as factory:
            factory.return_value.getresponse.return_value=response
            with self.assertRaisesRegex(ValueError,'private'):fetch('https://example.com')
            self.assertEqual(factory.call_count,1);factory.return_value.close.assert_called_once()
    def test_private_loopback_and_mixed_dns_never_connect(self):
        for address in ('127.0.0.1','192.168.1.1','169.254.169.254','::1','224.0.0.1'):
            with patch('desktop.web_access.socket.getaddrinfo',return_value=self.dns(address)),patch('desktop.web_access.PinnedHTTPS') as conn:
                with self.assertRaises(ValueError):fetch('https://example.com/private')
                conn.assert_not_called()
        with patch('desktop.web_access.socket.getaddrinfo',return_value=self.dns('8.8.8.8')+self.dns('10.0.0.1')):
            with self.assertRaises(ValueError):endpoint('https://example.com')
    def test_credentials_http_and_alternate_ports_are_rejected(self):
        for url in ('http://example.com','file:///private','https://user:pass@example.com','https://example.com:8787'):
            with self.assertRaises(ValueError):endpoint(url)
    def test_search_cache_is_bounded_and_snippets_are_untrusted(self):
        rss='<rss><channel><item><title>Docs</title><link>https://docs.python.org/3/</link><description>Public docs</description></item></channel></rss>'
        client=PublicWeb()
        with patch('desktop.web_access.fetch',return_value=(rss,'https://www.bing.com')) as network:
            a=client.search('Python docs');b=client.search('Python docs')
            self.assertEqual(a,b);network.assert_called_once()
            self.assertTrue(a['untrusted_public_web'])
            self.assertEqual(a['results'][0]['url'],'https://docs.python.org/3/')
    def test_page_scripts_are_excluded_and_excerpt_is_bounded(self):
        with patch('desktop.web_access.fetch',return_value=('<title>Title</title><script>steal()</script><p>'+('x '*4000)+'</p>','https://example.com')):
            result=PublicWeb().read('https://example.com')
        self.assertNotIn('steal()',result['excerpt']);self.assertLessEqual(len(result['excerpt']),2500)
    def test_empty_or_broken_search_never_fabricates_sources(self):
        for text in ('bad xml','<rss><channel/></rss>'):
            with patch('desktop.web_access.fetch',return_value=(text,'https://www.bing.com')):
                with self.assertRaises(ValueError):PublicWeb().search('latest news')
    def test_auto_research_uses_current_question_not_private_memory_requests(self):
        self.assertIsNotNone(research_request("What's the latest news about Python?"))
        self.assertIsNotNone(research_request('Summarize https://example.com please'))
        self.assertIsNone(research_request('What do you remember about my latest project?'))
        self.assertIsNone(research_request('Open Notepad'))
