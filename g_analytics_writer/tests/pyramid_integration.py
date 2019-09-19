import g_analytics_writer
import g_analytics_writer.pyramid_integration

from g_analytics_writer import AnalyticsWriter
from g_analytics_writer import GtagDimensionsStrategy

# core testing facility
import unittest

# pyramid testing requirements
from pyramid import testing
from pyramid.interfaces import IRequestExtensions


# testing needs
from webob.multidict import MultiDict
from ._utils import custom_json_dumps_sorted


class _TestHarness(object):

    _gwriter_accountid = "UA-12345678987654321-12"
    _gwriter_mode = g_analytics_writer.AnalyticsMode.GA_JS
    _gwriter_use_comments = None
    _gwriter_single_push = None
    _gwriter_amp_clientid_integration = None
    _gwriter_gtag_dimensions_strategy = None
    _gwriter_global_custom_data = None
    _expected_setup_fail = None

    def setUp(self):
        self.config = testing.setUp()

        # grab the config object, then modify in place
        settings = self.config.get_settings()
        settings["g_analytics_writer.account_id"] = self._gwriter_accountid
        settings["g_analytics_writer.mode"] = self._gwriter_mode
        settings[
            "g_analytics_writer.json_dumps_callable"
        ] = custom_json_dumps_sorted  # needed for testing because it sorts
        if self._gwriter_use_comments is not None:
            settings["g_analytics_writer.use_comments"] = self._gwriter_use_comments
        if self._gwriter_single_push is not None:
            settings["g_analytics_writer.single_push"] = self._gwriter_single_push
        if self._gwriter_global_custom_data is not None:
            settings[
                "g_analytics_writer.global_custom_data"
            ] = self._gwriter_global_custom_data
        if self._gwriter_gtag_dimensions_strategy is not None:
            settings[
                "g_analytics_writer.gtag_dimensions_strategy"
            ] = self._gwriter_gtag_dimensions_strategy
        if self._gwriter_amp_clientid_integration is not None:
            settings[
                "g_analytics_writer.amp_clientid_integration"
            ] = self._gwriter_amp_clientid_integration

        if self._expected_setup_fail:
            self.assertRaises(
                ValueError,
                self.config.include,
                "g_analytics_writer.pyramid_integration",
            )
            return

        self.config.include("g_analytics_writer.pyramid_integration")
        self.context = testing.DummyResource()
        self.request = testing.DummyRequest()

        # intiialize a writer for the request
        exts = self.config.registry.getUtility(IRequestExtensions)
        self.assertTrue("g_analytics_writer" in exts.descriptors)
        request_writer = exts.descriptors["g_analytics_writer"].wrapped(self.request)
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
        if self._expected_setup_fail:
            raise unittest.SkipTest(
                "This test should have successfully failed during setUp; no further testing needed"
            )

        self.assertTrue("g_analytics_writer" in self.request.__dict__)

        # we might supply a string, which is turned to an int
        self.assertEqual(self.request.g_analytics_writer.mode, int(self._gwriter_mode))

        # possible overrides
        if self._gwriter_use_comments is None:
            self.assertEqual(
                self.request.g_analytics_writer.use_comments,
                AnalyticsWriter.use_comments,
            )
        else:
            self.assertEqual(
                self.request.g_analytics_writer.use_comments, self._gwriter_use_comments
            )

        # possible overrides
        if self._gwriter_single_push is None:
            self.assertEqual(
                self.request.g_analytics_writer.single_push, AnalyticsWriter.single_push
            )
        else:
            self.assertEqual(
                self.request.g_analytics_writer.single_push, self._gwriter_single_push
            )

        # possible overrides
        if self._gwriter_global_custom_data is None:
            self.assertEqual(
                self.request.g_analytics_writer.global_custom_data,
                AnalyticsWriter.global_custom_data,
            )
        else:
            self.assertEqual(
                self.request.g_analytics_writer.global_custom_data,
                self._gwriter_global_custom_data,
            )

        # possible overrides
        if self._gwriter_gtag_dimensions_strategy is None:
            self.assertEqual(
                self.request.g_analytics_writer.gtag_dimensions_strategy,
                AnalyticsWriter.gtag_dimensions_strategy,
            )
        else:
            self.assertEqual(
                self.request.g_analytics_writer.gtag_dimensions_strategy,
                self._gwriter_gtag_dimensions_strategy,
            )

        # possible overrides
        if self._gwriter_amp_clientid_integration is None:
            self.assertEqual(
                self.request.g_analytics_writer.amp_clientid_integration,
                AnalyticsWriter.amp_clientid_integration,
            )
        else:
            self.assertEqual(
                self.request.g_analytics_writer.amp_clientid_integration,
                self._gwriter_amp_clientid_integration,
            )


class TestSetupSimple(_TestSetup, unittest.TestCase):
    pass


class TestSetupModeString(_TestSetup, unittest.TestCase):
    _gwriter_mode = str(g_analytics_writer.AnalyticsMode.GA_JS)


class TestSetupCommentsTrue(_TestSetup, unittest.TestCase):
    _gwriter_use_comments = True


class TestSetupCommentsFalse(_TestSetup, unittest.TestCase):
    _gwriter_use_comments = False


class TestSetupGlobalCustomDataTrue(_TestSetup, unittest.TestCase):
    _gwriter_global_custom_data = True


class TestSetupGlobalCustomDataFalse(_TestSetup, unittest.TestCase):
    _gwriter_global_custom_data = False


class TestSetupGtagDimensionsStrategySetConfig(_TestSetup, unittest.TestCase):
    _gwriter_gtag_dimensions_strategy = GtagDimensionsStrategy.SET_CONFIG


class TestSetupGtagDimensionsStrategyConfignopageviewSetEvent(
    _TestSetup, unittest.TestCase
):
    _gwriter_gtag_dimensions_strategy = (
        GtagDimensionsStrategy.CONFIGNOPAGEVIEW_SET_EVENT
    )


class TestSetupGtagDimensionsStrategyBad(_TestSetup, unittest.TestCase):
    _gwriter_gtag_dimensions_strategy = 100
    _expected_setup_fail = True


class TestSetupAmpClientidIntegrationTrue(_TestSetup, unittest.TestCase):
    _gwriter_amp_clientid_integration = True


class TestSetupAmpClientidIntegrationFalse(_TestSetup, unittest.TestCase):
    _gwriter_amp_clientid_integration = False


class _TestPageviews(_TestHarness):
    """
    core class for tests.
    subclass this with data and a configred _gwriter_mode
    """

    _gwriter_mode = None  # reset to Null
    data__test_pageview__html = None
    data__test_pageview_alt__html = None

    def test_render_page(self):
        """test the request property worked"""
        as_html = self.request.g_analytics_writer.render()
        self.assertEqual(as_html, self.data__test_pageview__html)

    def test_render_pageview_alt(self):
        """test the request property worked"""
        self.request.g_analytics_writer.set_custom_variable(1, "section", "account")
        self.request.g_analytics_writer.set_custom_variable(2, "pagetype", "-")
        self.request.g_analytics_writer.set_custom_variable(
            5, "is_known_user", "1", 1
        )  # 1 (visitor-level), 2 (session-level), or 3 (page-level)

        # overwrite
        self.request.g_analytics_writer.set_custom_variable(2, "pagetype", "home")
        as_html = self.request.g_analytics_writer.render()
        self.assertEqual(as_html, self.data__test_pageview_alt__html)


class TestGA(_TestPageviews, unittest.TestCase):
    _gwriter_mode = g_analytics_writer.AnalyticsMode.GA_JS
    # --
    data__test_pageview__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-12345678987654321-12']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_pageview_alt__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-12345678987654321-12']);
_gaq.push(['_setCustomVar',1,'section','account']);
_gaq.push(['_setCustomVar',2,'pagetype','home']);
_gaq.push(['_setCustomVar',5,'is_known_user','1',1]);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""


class TestAnalytics(_TestPageviews, unittest.TestCase):
    _gwriter_mode = g_analytics_writer.AnalyticsMode.ANALYTICS
    # --
    data__test_pageview__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-12345678987654321-12','auto');
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_pageview_alt__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-12345678987654321-12','auto');
ga('set',{"dimension1":"account","dimension2":"home","dimension5":"1"});
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""


class TestGtag(_TestPageviews, unittest.TestCase):
    _gwriter_mode = g_analytics_writer.AnalyticsMode.GTAG
    # --
    data__test_pageview__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-12345678987654321-12"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-12345678987654321-12');
</script>
<!-- End Google Analytics -->"""
    data__test_pageview_alt__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-12345678987654321-12"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('set',{"is_known_user":"1","pagetype":"home","section":"account"});
gtag('config','UA-12345678987654321-12',{"custom_map":{"dimension1":"section","dimension2":"pagetype","dimension5":"is_known_user"}});
</script>
<!-- End Google Analytics -->"""


class TestAnalytics_Case1(TestAnalytics, unittest.TestCase):
    _gwriter_mode = 2
    _gwriter_use_comments = False
    _gwriter_global_custom_data = True
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
    data__test_pageview_alt__html = """\
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-12345678987654321-12','auto');
ga('set',{"dimension1":"account","dimension2":"home","dimension5":"1"});
ga('send','pageview');
</script>"""
