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
    _gwriter_use_comments = None
    _gwriter_modes_support_alternate = None
    _gwriter_single_push = None

    def setUp(self):
        self.config = testing.setUp()

        # grab the config object, then modify in place
        settings = self.config.get_settings()
        settings['g_analytics_writer.account_id'] = self._gwriter_accountid
        settings['g_analytics_writer.mode'] = self._gwriter_mode
        if self._gwriter_use_comments is not None:
            settings['g_analytics_writer.use_comments'] = self._gwriter_use_comments
        if self._gwriter_modes_support_alternate is not None:
            settings['g_analytics_writer.modes_support_alternate'] = self._gwriter_modes_support_alternate
        if self._gwriter_single_push is not None:
            settings['g_analytics_writer.single_push'] = self._gwriter_single_push

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


class _TestSetup(_TestHarness):

    def test_pyramid_setup(self):
        """
        test the request property worked

        This has many variations, all designed to ensure the request vars are parsed as intended
        """
        self.assertTrue('g_analytics_writer' in self.request.__dict__)

        # we might supply a string, which is turned to an int
        self.assertEqual(self.request.g_analytics_writer.mode, int(self._gwriter_mode))

        # possible overrides
        if self._gwriter_use_comments is None:
            self.assertEqual(self.request.g_analytics_writer.use_comments, False)
        else:
            self.assertEqual(self.request.g_analytics_writer.use_comments, self._gwriter_use_comments)

        # possible overrides
        if self._gwriter_single_push is None:
            self.assertEqual(self.request.g_analytics_writer.single_push, False)
        else:
            self.assertEqual(self.request.g_analytics_writer.single_push, self._gwriter_single_push)

        # possible overrides
        if not self._gwriter_modes_support_alternate:
            self.assertEqual(self.request.g_analytics_writer.modes_support_alternate, None)
        else:
            _expected = []
            _input = self._gwriter_modes_support_alternate
            if type(_input) in (list, tuple):
                _expected = tuple([int(i) for i in _input])
            elif type(_input) is int:
                _expected = (_input, )
            else:
                _expected = tuple([int(i.strip()) for i in _input.split(',') if i.strip()])
            self.assertEqual(self.request.g_analytics_writer.modes_support_alternate, _expected)


class TestSetupSimple(_TestSetup, unittest.TestCase):
    pass


class TestSetupModeString(_TestSetup, unittest.TestCase):
    _gwriter_mode = str(g_analytics_writer.AnalyticsMode.GA_JS)


class TestSetupCommentsTrue(_TestSetup, unittest.TestCase):
    _gwriter_use_comments = True


class TestSetupCommentsFalse(_TestSetup, unittest.TestCase):
    _gwriter_use_comments = False


class TestSetupAlternateModesNullA(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = []


class TestSetupAlternateModesNullB(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = ''


class TestSetupAlternateModesSingleString(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = str(g_analytics_writer.AnalyticsMode.ANALYTICS)


class TestSetupAlternateModesSingleInt(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = g_analytics_writer.AnalyticsMode.ANALYTICS


class TestSetupAlternateModesMultipleString(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = str(','.join([str(i) for i in [g_analytics_writer.AnalyticsMode.ANALYTICS, g_analytics_writer.AnalyticsMode.GTAG]]))


class TestSetupAlternateModesMultipleTupleInt(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = (g_analytics_writer.AnalyticsMode.ANALYTICS, g_analytics_writer.AnalyticsMode.GTAG)


class TestSetupAlternateModesMultipleListInt(_TestSetup, unittest.TestCase):
    _gwriter_modes_support_alternate = [g_analytics_writer.AnalyticsMode.ANALYTICS, g_analytics_writer.AnalyticsMode.GTAG]


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
