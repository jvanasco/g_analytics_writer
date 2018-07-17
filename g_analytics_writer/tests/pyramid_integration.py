import g_analytics_writer
import g_analytics_writer.pyramid_integration

# core testing facility
import unittest

# pyramid testing requirements
from pyramid import testing
from pyramid.interfaces import IRequestExtensions


# testing needs
from webob.multidict import MultiDict


class _TestHarness(object):

    _gwriter_accountid = 'UA-12345678987654321-12'
    _gwriter_mode = g_analytics_writer.AnalyticsMode.GA_JS

    def setUp(self):
        self.config = testing.setUp()

        # grab the config object, then modify in place
        settings = self.config.get_settings()
        settings['g_analytics_writer.account_id'] = self._gwriter_accountid
        settings['g_analytics_writer.mode'] = self._gwriter_mode

        self.config.include('g_analytics_writer.pyramid_integration')
        self.context = testing.DummyResource()
        self.request = testing.DummyRequest()

        # intiialize a writer for the request
        exts = self.config.registry.getUtility(IRequestExtensions)
        self.assertTrue('g_analytics_writer' in exts.descriptors)
        request_writer = exts.descriptors['g_analytics_writer'].wrapped(self.request)
        # copy the writer onto the request...
        self.request.g_analytics_writer = request_writer

    def tearDown(self):
        testing.tearDown()


class TestSetup(_TestHarness, unittest.TestCase):

    def test_pyramid_setup(self):
        """test the request property worked"""
        self.assertTrue('g_analytics_writer' in self.request.__dict__)


class _TestPageviews(_TestHarness):
    """
    core class for tests.
    subclass this with data and a configred _gwriter_mode
    """
    _gwriter_mode = None  # reset to Null
    data__test_pageview__html = None

    def test_render_page(self):
        """test the request property worked"""
        as_html = self.request.g_analytics_writer.render()
        self.assertEqual(as_html, self.data__test_pageview__html)


class TestGA(_TestPageviews, unittest.TestCase):
    _gwriter_mode = g_analytics_writer.AnalyticsMode.GA_JS
    # --
    data__test_pageview__html = """\
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-12345678987654321-12']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>"""


class TestAnalytics(_TestPageviews, unittest.TestCase):
    _gwriter_mode = g_analytics_writer.AnalyticsMode.ANALYTICS
    # --
    data__test_pageview__html = """\
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-12345678987654321-12','auto');
ga('send','pageview');
</script>"""
