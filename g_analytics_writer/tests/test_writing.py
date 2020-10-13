# -*- coding: utf-8 -*-
from __future__ import print_function
import pdb

"""
NOTE FOR TESTS

Instead of "Green" we use a unicode string "Greeñ". 
This means the string in Python2 must be marked with a u, and for testing concerns
it stays with a u prefix for Python3

note that we strings are still prefixed with `u` for Python2
"""


import g_analytics_writer
from g_analytics_writer import AnalyticsWriter
from g_analytics_writer import AnalyticsMode
from g_analytics_writer import GtagDimensionsStrategy

# import g_analytics_writer.pyramid_integration

# core testing facility
import unittest
import re
import os
from ._utils import custom_json_dumps_sorted

# regexes to test against
re_refresh_15 = re.compile('<meta http-equiv="refresh" content="15"/>')
re_other_charset = re.compile('<meta charset="utf8"/>')

# used for writing tests
# export g_analytics_writer_debug=1
# export g_analytics_writer_debug=0
PRINT_RENDERS = bool(int(os.environ.get("g_analytics_writer_debug", 0)))

# pyramid testing requirements
# from pyramid import testing


class CoreTests(object):
    maxDiff = None  # test authoring

    mode = None
    _test_single_push = None
    data_gtag_dimensions_strategies = None
    data_global_custom_data = None
    data__test_force_ssl = None
    data__test_amp_clientid_integration = None
    data__test_amp_clientid_integration_head = None

    def test_pageview(self):
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_pageview__html)

        writer.set_account_additional__add("UA-123123-3")
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_pageview_multi__html)

    def test_multiple_accounts(self):
        """
        tests to see
            * switching accounts works
            * usig multiple accounts works
        """
        a = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        # switch account
        a.set_account("UA-123123-2")
        # add account
        a.set_account_additional__add("UA-123123-3")
        html_rendered = a.render()
        if PRINT_RENDERS:
            print(html_rendered)
        self.assertEqual(html_rendered, self.data__test_multiple_accounts__html)

    def test_comments(self):
        """
        just tests to see the framing comments toggle works
        """
        comments = AnalyticsWriter(
            "UA-123123-1",
            mode=self.mode,
            use_comments=True,
            json_dumps_callable=custom_json_dumps_sorted,
        )
        html_comments = comments.render()
        if PRINT_RENDERS:
            print(html_comments)
        self.assertEqual(html_comments, self.data__test_comments__html_comments)

        nocomments = AnalyticsWriter(
            "UA-123123-1",
            mode=self.mode,
            use_comments=False,
            json_dumps_callable=custom_json_dumps_sorted,
        )
        html_nocomments = nocomments.render()
        if PRINT_RENDERS:
            print(html_nocomments)
        self.assertEqual(html_nocomments, self.data__test_comments__html_nocomments)

    def test_transaction_good(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        writer.add_transaction(self.data__transaction_dict_good)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_transaction_good__html)

    def test_transaction_bad(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        self.assertRaises(
            ValueError, writer.add_transaction, self.data__transaction_dict_bad
        )

    def test_transaction_item_bad(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        writer.add_transaction(self.data__transaction_dict_good)
        self.assertRaises(
            ValueError,
            writer.add_transaction_item,
            self.data__transaction_item_dict_bad,
        )

    def test_transaction_good_single_push(self):
        """
        just tests to see the framing comments toggle works
        """
        if not self._test_single_push:
            raise unittest.SkipTest(
                "single_push not tested on %s" % self.__class__.__name__
            )
        writer = AnalyticsWriter(
            "UA-123123-1",
            mode=self.mode,
            single_push=True,
            json_dumps_callable=custom_json_dumps_sorted,
        )
        writer.add_transaction(self.data__transaction_dict_good)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_transaction_good_single_push__html)

    def test_track_event(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        writer.track_event(self.data__event_good_1)
        writer.track_event(self.data__event_good_2)
        writer.track_event(self.data__event_good_3)
        writer.track_event(self.data__event_good_4)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_track_event__html)

    def test_crossdomain(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        writer.set_crossdomain_tracking("foo.example.com")
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_crossdomain__html)

        link_attrs = writer.render_crossdomain_link_attrs(
            "https://example.com/foo.html"
        )
        if PRINT_RENDERS:
            print(link_attrs)
        self.assertEqual(link_attrs, self.data__test_crossdomain__html_link_attrs)

        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        writer.set_crossdomain_tracking(domains=["foo.example.com", "bar.example.com"])
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_crossdomain__html_multi)

    def test_custom_variables(self):
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        (index, name, value, opt_scope) = self.data__custom_variables
        writer.set_custom_variable(index, name, value, opt_scope=opt_scope)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_custom_variables__html)

        if self.data_gtag_dimensions_strategies:
            # cache for reset
            _existing__gtag_dimensions_strategy = writer.gtag_dimensions_strategy
            _existing__global_custom_data = writer.global_custom_data
            for (
                gtag_dimensions_strategy,
                global_custom_data,
                expected_html,
            ) in self.data_gtag_dimensions_strategies:
                writer.gtag_dimensions_strategy = gtag_dimensions_strategy
                writer.global_custom_data = global_custom_data
                as_html = writer.render()
                if PRINT_RENDERS:
                    print(as_html)
                self.assertEqual(as_html, expected_html)
            # reset
            writer.gtag_dimensions_strategy = _existing__gtag_dimensions_strategy
            writer.global_custom_data = _existing__global_custom_data

        if self.data_global_custom_data:
            # cache for reset
            _existing = writer.global_custom_data
            for (strategy, expected_html) in self.data_global_custom_data:
                writer.global_custom_data = strategy
                as_html = writer.render()
                if PRINT_RENDERS:
                    print(as_html)
                self.assertEqual(as_html, expected_html)
            # reset
            writer.global_custom_data = _existing

        writer.global_custom_data = True
        as_html_global = writer.render()
        if PRINT_RENDERS:
            print(as_html_global)
        self.assertEqual(as_html_global, self.data__test_custom_variables__global__html)

    def test_advanced(self):
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )

        # make sure this is True by default
        self.assertTrue(writer.global_custom_data)

        (index, name, value, opt_scope) = self.data__custom_variables
        # crossdomain
        writer.set_crossdomain_tracking("foo.example.com")
        # add account
        writer.set_account_additional__add("UA-123123-2")
        writer.set_account_additional__add("UA-123123-3")
        writer.set_custom_variable(index, name, value, opt_scope=opt_scope)
        writer.track_event(self.data__event_good_1)
        writer.track_event(self.data__event_good_2)
        writer.track_event(self.data__event_good_3)
        writer.track_event(self.data__event_good_4)
        writer.add_transaction(self.data__transaction_dict_good)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)

        # by default, these use global data
        self.assertEqual(as_html, self.data__test_advanced__html)

        # let's try nonglobal data
        writer.global_custom_data = False
        as_html_global = writer.render()
        if PRINT_RENDERS:
            print(as_html_global)
        self.assertEqual(as_html_global, self.data__test_advanced__nonglobal__html)

    def test_advanced_single_push(self):
        if not self._test_single_push:
            raise unittest.SkipTest(
                "single_push not tested on %s" % self.__class__.__name__
            )
        writer = AnalyticsWriter(
            "UA-123123-1",
            mode=self.mode,
            single_push=True,
            json_dumps_callable=custom_json_dumps_sorted,
        )
        (index, name, value, opt_scope) = self.data__custom_variables
        # crossdomain
        writer.set_crossdomain_tracking("foo.example.com")
        # add account
        writer.set_account_additional__add("UA-123123-2")
        writer.set_account_additional__add("UA-123123-3")
        writer.set_custom_variable(index, name, value, opt_scope=opt_scope)
        writer.track_event(self.data__event_good_1)
        writer.track_event(self.data__event_good_2)
        writer.track_event(self.data__event_good_3)
        writer.track_event(self.data__event_good_4)
        writer.add_transaction(self.data__transaction_dict_good)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_advanced_single_push__html)

    def test_userid_prerender(self):
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        writer.set_user_id("cecil")
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_prerender__html)

        # multiple accounts
        writer.set_account_additional__add("UA-123123-3")
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_prerender_multi__html)

    def test_userid_postrender(self):
        writer = AnalyticsWriter(
            "UA-123123-1", mode=self.mode, json_dumps_callable=custom_json_dumps_sorted
        )
        as_html = writer.setrender_user_id("cecil")
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_postrender__html)

        # multiple accounts
        writer.set_account_additional__add("UA-123123-3")
        as_html = writer.setrender_user_id("cecil")
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_postrender_multi__html)

    def test_force_ssl(self):
        if self.data__test_force_ssl:
            for (force_ssl, expected_html) in self.data__test_force_ssl:
                writer = AnalyticsWriter(
                    "UA-123123-1",
                    mode=self.mode,
                    force_ssl=force_ssl,
                    json_dumps_callable=custom_json_dumps_sorted,
                )
                as_html = writer.render()
                if PRINT_RENDERS:
                    print(as_html)
                self.assertEqual(as_html, expected_html)
        else:
            raise unittest.SkipTest(
                "force_ssl not tested on %s" % self.__class__.__name__
            )

    def test_amp_clientid_integration(self):
        writer = AnalyticsWriter(
            "UA-123123-1",
            mode=self.mode,
            amp_clientid_integration=True,
            json_dumps_callable=custom_json_dumps_sorted,
        )
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_amp_clientid_integration)

        for (
            kwarg,
            expected_html,
        ) in self.data__test_amp_clientid_integration_head.items():
            writer = AnalyticsWriter(
                "UA-123123-1",
                mode=self.mode,
                amp_clientid_integration=kwarg,
                json_dumps_callable=custom_json_dumps_sorted,
            )
            as_html = writer.render_head()
            if PRINT_RENDERS:
                print(as_html)
            self.assertEqual(as_html, expected_html)


# global dicts used for tests
# this lets us compare the different formats
data__transaction_dict_bad = {
    # missing data; should raise an error on add
}
data__transaction_dict_1 = {
    "*id": 1234,
    "*affiliation": "ga.js",
    "*total": "100.00",
    "*tax": "10.00",
    "*shipping": "5.00",
    "*city": "brooklyn",
    "*state": "new york",
    "*country": "usa",
}
data__transaction_dict_2 = {
    "*id": 1234,
    "*affiliation": "analytics.js",
    "*revenue": "115.00",
    "*tax": "10.00",
    "*shipping": "5.00",
}
data__transaction_item_dict = {
    "*transaction_id": 1234,  # transaction_id
    "*name": "T-Shirt",  # Product name. Required
    "*sku": "DD44",  # SKU/code
    "*category": u"Greeñ Medium",  # Category or variation
    "*price": "100.00",  # Unit price
    "*quantity": "1",
}

data__transaction_item_dict_bad = {
    "*id": 1234  # transaction_id presented incorrectly; should raise an error on add
}

data__event_1 = {
    "*category": "Videos",
    "*action": "Play",
    "*label": "action",
    "*value": 47,
    "*non_interaction": True,
}
data__event_2 = {
    "*category": "Videos",
    "*action": "Play",
    "*label": "action",
    "*value": 47,
    "*non_interaction": None,
}
data__event_3 = {
    "*category": "Videos",
    "*action": "Play",
    "*label": "action",
    "*value": 47,
    "*non_interaction": False,
}
data__event_4__ANALYTICS_hit = {
    "*category": "category",
    "*action": "action",
    "metric18": 8000,
}
data__custom_variables__GA = (
    6,
    "author",
    "jonathan",
    1,
)  # index, name, value, opt_scope=None)
data__custom_variables__ANALYTICS = (
    "dimension9",
    "name",
    "jonathan",
    None,
)  # index, name, value, opt_scope=None)


class TestGA(CoreTests, unittest.TestCase):
    mode = AnalyticsMode.GA_JS
    _test_single_push = True
    data__transaction_dict_good = data__transaction_dict_1
    data__transaction_dict_bad = data__transaction_dict_bad
    data__transaction_item_dict = data__transaction_item_dict
    data__transaction_item_dict_bad = data__transaction_item_dict_bad
    data__custom_variables = data__custom_variables__GA
    data__event_good_1 = data__event_1
    data__event_good_2 = data__event_2
    data__event_good_3 = data__event_3
    data__event_good_4 = data__event_4__ANALYTICS_hit
    data__test_pageview__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_pageview_multi__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
_gaq.push(['trkr0._setAccount','UA-123123-3']);
_gaq.push(['trkr0._trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_multiple_accounts__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-2']);
_gaq.push(['_trackPageview']);
_gaq.push(['trkr0._setAccount','UA-123123-3']);
_gaq.push(['trkr0._trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_comments = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_nocomments = """\
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>"""
    data__test_transaction_good__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
_gaq.push(['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['_addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1']);
_gaq.push(['_trackTrans']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""

    data__test_transaction_good_single_push__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(
['_setAccount','UA-123123-1'],
['_trackPageview'],
['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['_addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1'],
['_trackTrans']
);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_track_event__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
_gaq.push(['_trackEvent','Videos','Play','action',47,true]);
_gaq.push(['_trackEvent','Videos','Play','action',47]);
_gaq.push(['_trackEvent','Videos','Play','action',47,false]);
_gaq.push(['_trackEvent','category','action']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_setDomainName','foo.example.com']);
_gaq.push(['_setAllowLinker',true]);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_multi = (
        data__test_crossdomain__html  # this doesn't support it the same way
    )
    data__test_crossdomain__html_link_attrs = '''onclick="_gaq.push(['_link','https://example.com/foo.html']); return false;"'''
    data__test_custom_variables__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_setCustomVar',6,'author','jonathan',1]);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_custom_variables__global__html = data__test_custom_variables__html
    data__test_advanced__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_setDomainName','foo.example.com']);
_gaq.push(['_setAllowLinker',true]);
_gaq.push(['_setCustomVar',6,'author','jonathan',1]);
_gaq.push(['_trackPageview']);
_gaq.push(['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['_addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1']);
_gaq.push(['_trackTrans']);
_gaq.push(['_trackEvent','Videos','Play','action',47,true]);
_gaq.push(['_trackEvent','Videos','Play','action',47]);
_gaq.push(['_trackEvent','Videos','Play','action',47,false]);
_gaq.push(['_trackEvent','category','action']);
_gaq.push(['trkr0._setAccount','UA-123123-2']);
_gaq.push(['trkr0._setDomainName','foo.example.com']);
_gaq.push(['trkr0._setAllowLinker',true]);
_gaq.push(['trkr0._setCustomVar',6,'author','jonathan',1]);
_gaq.push(['trkr0._trackPageview']);
_gaq.push(['trkr0._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['trkr0._addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1']);
_gaq.push(['trkr0._trackTrans']);
_gaq.push(['trkr0._trackEvent','Videos','Play','action',47,true]);
_gaq.push(['trkr0._trackEvent','Videos','Play','action',47]);
_gaq.push(['trkr0._trackEvent','Videos','Play','action',47,false]);
_gaq.push(['trkr0._trackEvent','category','action']);
_gaq.push(['trkr1._setAccount','UA-123123-3']);
_gaq.push(['trkr1._setDomainName','foo.example.com']);
_gaq.push(['trkr1._setAllowLinker',true]);
_gaq.push(['trkr1._setCustomVar',6,'author','jonathan',1]);
_gaq.push(['trkr1._trackPageview']);
_gaq.push(['trkr1._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['trkr1._addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1']);
_gaq.push(['trkr1._trackTrans']);
_gaq.push(['trkr1._trackEvent','Videos','Play','action',47,true]);
_gaq.push(['trkr1._trackEvent','Videos','Play','action',47]);
_gaq.push(['trkr1._trackEvent','Videos','Play','action',47,false]);
_gaq.push(['trkr1._trackEvent','category','action']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_advanced__nonglobal__html = data__test_advanced__html
    data__test_advanced_single_push__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(
['_setAccount','UA-123123-1'],
['_setDomainName','foo.example.com'],
['_setAllowLinker',true],
['_setCustomVar',6,'author','jonathan',1],
['_trackPageview'],
['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['_addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1'],
['_trackTrans'],
['_trackEvent','Videos','Play','action',47,true],
['_trackEvent','Videos','Play','action',47],
['_trackEvent','Videos','Play','action',47,false],
['_trackEvent','category','action'],
['trkr0._setAccount','UA-123123-2'],
['trkr0._setDomainName','foo.example.com'],
['trkr0._setAllowLinker',true],
['trkr0._setCustomVar',6,'author','jonathan',1],
['trkr0._trackPageview'],
['trkr0._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['trkr0._addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1'],
['trkr0._trackTrans'],
['trkr0._trackEvent','Videos','Play','action',47,true],
['trkr0._trackEvent','Videos','Play','action',47],
['trkr0._trackEvent','Videos','Play','action',47,false],
['trkr0._trackEvent','category','action'],
['trkr1._setAccount','UA-123123-3'],
['trkr1._setDomainName','foo.example.com'],
['trkr1._setAllowLinker',true],
['trkr1._setCustomVar',6,'author','jonathan',1],
['trkr1._trackPageview'],
['trkr1._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['trkr1._addItem','1234','DD44','T-Shirt','Greeñ Medium','100.00','1'],
['trkr1._trackTrans'],
['trkr1._trackEvent','Videos','Play','action',47,true],
['trkr1._trackEvent','Videos','Play','action',47],
['trkr1._trackEvent','Videos','Play','action',47,false],
['trkr1._trackEvent','category','action']
);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_userid_prerender__html = data__test_pageview__html
    data__test_userid_prerender_multi__html = data__test_pageview_multi__html
    data__test_userid_postrender__html = ""
    data__test_userid_postrender_multi__html = ""
    # force_ssl, expected_html
    data__test_force_ssl = (
        (
            False,
            """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->""",
        ),
        (
            True,
            """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_gat._forceSSL']);
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->""",
        ),
    )
    data__test_amp_clientid_integration = (
        data__test_pageview__html  # not sure this functionality is possible under ga.js
    )
    data__test_amp_clientid_integration_head = {True: "", False: ""}


class TestAnalytics(CoreTests, unittest.TestCase):
    mode = AnalyticsMode.ANALYTICS
    data__transaction_dict_good = data__transaction_dict_2
    data__transaction_dict_bad = data__transaction_dict_bad
    data__transaction_item_dict = data__transaction_item_dict
    data__transaction_item_dict_bad = data__transaction_item_dict_bad
    data__custom_variables = data__custom_variables__ANALYTICS
    data__event_good_1 = data__event_1
    data__event_good_2 = data__event_2
    data__event_good_3 = data__event_3
    data__event_good_4 = data__event_4__ANALYTICS_hit
    data__test_pageview__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_pageview_multi__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview');
ga('create','UA-123123-3','auto','trkr0');
ga('trkr0.send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_multiple_accounts__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-2','auto');
ga('send','pageview');
ga('create','UA-123123-3','auto','trkr0');
ga('trkr0.send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_comments = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_nocomments = """\
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview');
</script>"""
    data__test_transaction_good__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('require','ecommerce');
ga('send','pageview');
ga('ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('ecommerce:send');
</script>
<!-- End Google Analytics -->"""

    data__test_crossdomain__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"allowLinker":true});
ga('require','linker');
ga('linker:autoLink',['foo.example.com']);
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_multi = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"allowLinker":true});
ga('require','linker');
ga('linker:autoLink',['foo.example.com','bar.example.com']);
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_track_event__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview');
ga('send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('send','event','Videos','Play','action',47);
ga('send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('send','event','category','action');
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_link_attrs = ""  # empty string
    data__test_custom_variables__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('set',{"dimension9":"jonathan"});
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data_global_custom_data = (
        (
            True,
            """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('set',{"dimension9":"jonathan"});
ga('send','pageview');
</script>
<!-- End Google Analytics -->""",
        ),
        (
            False,
            """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview',{"dimension9":"jonathan"});
</script>
<!-- End Google Analytics -->""",
        ),
    )
    data__test_custom_variables__global__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('set',{"dimension9":"jonathan"});
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_advanced__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"allowLinker":true});
ga('require','linker');
ga('linker:autoLink',['foo.example.com']);
ga('require','ecommerce');
ga('set',{"dimension9":"jonathan"});
ga('send','pageview');
ga('ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('ecommerce:send');
ga('send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('send','event','Videos','Play','action',47);
ga('send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('send','event','category','action');
ga('create','UA-123123-2','auto','trkr0',{"allowLinker":true});
ga('trkr0.set',{"dimension9":"jonathan"});
ga('trkr0.send','pageview');
ga('trkr0.ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('trkr0.ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('trkr0.ecommerce:send');
ga('trkr0.send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('trkr0.send','event','Videos','Play','action',47);
ga('trkr0.send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('trkr0.send','event','category','action');
ga('create','UA-123123-3','auto','trkr1',{"allowLinker":true});
ga('trkr1.set',{"dimension9":"jonathan"});
ga('trkr1.send','pageview');
ga('trkr1.ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('trkr1.ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('trkr1.ecommerce:send');
ga('trkr1.send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('trkr1.send','event','Videos','Play','action',47);
ga('trkr1.send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('trkr1.send','event','category','action');
</script>
<!-- End Google Analytics -->"""
    data__test_advanced__nonglobal__html = u"""\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"allowLinker":true});
ga('require','linker');
ga('linker:autoLink',['foo.example.com']);
ga('require','ecommerce');
ga('send','pageview',{"dimension9":"jonathan"});
ga('ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('ecommerce:send');
ga('send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('send','event','Videos','Play','action',47);
ga('send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('send','event','category','action');
ga('create','UA-123123-2','auto','trkr0',{"allowLinker":true});
ga('trkr0.send','pageview',{"dimension9":"jonathan"});
ga('trkr0.ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('trkr0.ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('trkr0.ecommerce:send');
ga('trkr0.send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('trkr0.send','event','Videos','Play','action',47);
ga('trkr0.send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('trkr0.send','event','category','action');
ga('create','UA-123123-3','auto','trkr1',{"allowLinker":true});
ga('trkr1.send','pageview',{"dimension9":"jonathan"});
ga('trkr1.ecommerce:addTransaction',{"affiliation":"analytics.js","id":"1234","revenue":"115.00","shipping":"5.00","tax":"10.00"})
ga('trkr1.ecommerce:addItem',{"category":"Greeñ Medium","id":"1234","name":"T-Shirt","price":"100.00","quantity":"1","sku":"DD44"})
ga('trkr1.ecommerce:send');
ga('trkr1.send','event','Videos','Play','action',47,{"nonInteraction":true});
ga('trkr1.send','event','Videos','Play','action',47);
ga('trkr1.send','event','Videos','Play','action',47,{"nonInteraction":false});
ga('trkr1.send','event','category','action');
</script>
<!-- End Google Analytics -->"""
    data__test_userid_prerender__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"userId":"cecil"});
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_userid_prerender_multi__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"userId":"cecil"});
ga('send','pageview');
ga('create','UA-123123-3','auto','trkr0',{"userId":"cecil"});
ga('trkr0.send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_userid_postrender__html = """\
ga('set','userId','cecil');
ga('send','event','authentication','user-id available');"""
    data__test_userid_postrender_multi__html = """\
ga('set','userId','cecil');
ga('send','event','authentication','user-id available');
ga('trkr0.set','userId','cecil');
ga('trkr0.send','event','authentication','user-id available');"""
    data__test_amp_clientid_integration = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto',{"useAmpClientId":true});
ga('send','pageview');
</script>
<!-- End Google Analytics -->"""
    data__test_amp_clientid_integration_head = {True: "", False: ""}


class TestGtag(CoreTests, unittest.TestCase):
    """
    python -munittest g_analytics_writer.tests.writing.TestGtag.test_track_event

    python -munittest g_analytics_writer.tests.writing.TestGtag
    python -munittest g_analytics_writer.tests.writing.TestGtag.test_advanced
    python -munittest g_analytics_writer.tests.writing.TestGtag.test_crossdomain
    """

    mode = AnalyticsMode.GTAG
    data__transaction_dict_good = data__transaction_dict_2
    data__transaction_dict_bad = data__transaction_dict_bad
    data__transaction_item_dict = data__transaction_item_dict
    data__transaction_item_dict_bad = data__transaction_item_dict_bad
    data__custom_variables = data__custom_variables__ANALYTICS
    data__event_good_1 = data__event_1
    data__event_good_2 = data__event_2
    data__event_good_3 = data__event_3
    data__event_good_4 = data__event_4__ANALYTICS_hit
    data__test_pageview__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
</script>
<!-- End Google Analytics -->"""
    data__test_pageview_multi__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
gtag('config','UA-123123-3');
</script>
<!-- End Google Analytics -->"""
    data__test_multiple_accounts__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-2');
gtag('config','UA-123123-3');
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_comments = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_nocomments = """\
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
</script>"""
    data__test_transaction_good__html = u"""\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
gtag('event', 'purchase', {"affiliation":"analytics.js","items":[{"category":"Greeñ Medium","id":"DD44","name":"T-Shirt","price":"100.00","quantity":"1"}],"shipping":"5.00","tax":"10.00","transaction_id":"1234","value":"115.00"}
</script>
<!-- End Google Analytics -->"""

    data__test_crossdomain__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"linker":{"domains":["foo.example.com"]}});
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_multi = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"linker":{"domains":["foo.example.com","bar.example.com"]}});
</script>
<!-- End Google Analytics -->"""
    data__test_track_event__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
gtag('event','Play',{"event_category":"Videos","event_label":"action","non_interaction":true,"value":47}
gtag('event','Play',{"event_category":"Videos","event_label":"action","value":47}
gtag('event','Play',{"event_category":"Videos","event_label":"action","non_interaction":false,"value":47}
gtag('event','action',{"event_category":"category"}
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_link_attrs = ""  # empty string
    data__test_custom_variables__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('set',{"name":"jonathan"});
gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"}});
</script>
<!-- End Google Analytics -->"""
    # gtag_dimensions_strategy, global_custom_data, expected_html
    data_gtag_dimensions_strategies = (
        (
            GtagDimensionsStrategy.SET_CONFIG,
            True,
            """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('set',{"name":"jonathan"});
gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"}});
</script>
<!-- End Google Analytics -->""",
        ),
        (
            GtagDimensionsStrategy.SET_CONFIG,
            False,
            """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"}});
gtag('event','pageview',{"name":"jonathan"});
</script>
<!-- End Google Analytics -->""",
        ),
        (
            GtagDimensionsStrategy.CONFIGNOPAGEVIEW_SET_EVENT,
            True,
            """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"},"send_page_view":false});
gtag('set',{"name":"jonathan"});
gtag('event','pageview');
</script>
<!-- End Google Analytics -->""",
        ),
        (
            GtagDimensionsStrategy.CONFIGNOPAGEVIEW_SET_EVENT,
            False,
            """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"},"send_page_view":false});
gtag('event','pageview',{"name":"jonathan"});
</script>
<!-- End Google Analytics -->""",
        ),
    )
    data__test_custom_variables__global__html = data__test_custom_variables__html
    data__test_advanced__html = u"""\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('set',{"name":"jonathan"});
gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"},"linker":{"domains":["foo.example.com"]}});
gtag('config','UA-123123-2',{"custom_map":{"dimension9":"name"},"linker":{"domains":["foo.example.com"]}});
gtag('config','UA-123123-3',{"custom_map":{"dimension9":"name"},"linker":{"domains":["foo.example.com"]}});
gtag('event', 'purchase', {"affiliation":"analytics.js","items":[{"category":"Greeñ Medium","id":"DD44","name":"T-Shirt","price":"100.00","quantity":"1"}],"shipping":"5.00","tax":"10.00","transaction_id":"1234","value":"115.00"}
gtag('event','Play',{"event_category":"Videos","event_label":"action","non_interaction":true,"value":47}
gtag('event','Play',{"event_category":"Videos","event_label":"action","value":47}
gtag('event','Play',{"event_category":"Videos","event_label":"action","non_interaction":false,"value":47}
gtag('event','action',{"event_category":"category"}
</script>
<!-- End Google Analytics -->"""
    data__test_advanced__nonglobal__html = u"""\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"},"linker":{"domains":["foo.example.com"]}});
gtag('config','UA-123123-2',{"custom_map":{"dimension9":"name"},"linker":{"domains":["foo.example.com"]}});
gtag('config','UA-123123-3',{"custom_map":{"dimension9":"name"},"linker":{"domains":["foo.example.com"]}});
gtag('event','pageview',{"name":"jonathan"});
gtag('event', 'purchase', {"affiliation":"analytics.js","items":[{"category":"Greeñ Medium","id":"DD44","name":"T-Shirt","price":"100.00","quantity":"1"}],"shipping":"5.00","tax":"10.00","transaction_id":"1234","value":"115.00"}
gtag('event','Play',{"event_category":"Videos","event_label":"action","non_interaction":true,"value":47}
gtag('event','Play',{"event_category":"Videos","event_label":"action","value":47}
gtag('event','Play',{"event_category":"Videos","event_label":"action","non_interaction":false,"value":47}
gtag('event','action',{"event_category":"category"}
</script>
<!-- End Google Analytics -->"""
    data__test_userid_prerender__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"user_id":"cecil"});
</script>
<!-- End Google Analytics -->"""
    data__test_userid_prerender_multi__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"user_id":"cecil"});
gtag('config','UA-123123-3',{"user_id":"cecil"});
</script>
<!-- End Google Analytics -->"""
    data__test_userid_postrender__html = """\
gtag('config', 'UA-123123-1', {'user_id': 'cecil'});"""
    data__test_userid_postrender_multi__html = """\
gtag('config', 'UA-123123-1', {'user_id': 'cecil'});
gtag('config', 'UA-123123-3', {'user_id': 'cecil'});"""
    data__test_amp_clientid_integration = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"use_amp_client_id":true});
</script>
<!-- End Google Analytics -->"""
    data__test_amp_clientid_integration_head = {True: "", False: ""}


class TestAmp(CoreTests, unittest.TestCase):
    """
    python -munittest g_analytics_writer.tests.writing.TestAmp.test_track_event

    python -munittest g_analytics_writer.tests.writing.TestAmp
    python -munittest g_analytics_writer.tests.writing.TestAmp.test_advanced
    python -munittest g_analytics_writer.tests.writing.TestAmp.test_crossdomain
    """

    mode = AnalyticsMode.AMP
    data__transaction_dict_good = data__transaction_dict_2
    data__transaction_dict_bad = data__transaction_dict_bad
    data__transaction_item_dict = data__transaction_item_dict
    data__transaction_item_dict_bad = data__transaction_item_dict_bad
    data__custom_variables = data__custom_variables__ANALYTICS
    data__event_good_1 = data__event_1
    data__event_good_2 = data__event_2
    data__event_good_3 = data__event_3
    data__event_good_4 = data__event_4__ANALYTICS_hit
    data__test_pageview__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_pageview_multi__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_multiple_accounts__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-2"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_comments__html_comments = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""

    data__test_comments__html_nocomments = """\
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>"""
    data__test_transaction_good__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""

    data__test_crossdomain__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_multi = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_track_event__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_link_attrs = ""  # empty string
    data__test_custom_variables__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""

    # gtag_dimensions_strategy, global_custom_data, expected_html
    data_gtag_dimensions_strategies = (
        (
            GtagDimensionsStrategy.SET_CONFIG,
            True,
            """<!-- Google Analytics -->\n<amp-analytics type="googleanalytics">\n<script type="application/json">\n{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}\n</script>\n</amp-analytics>\n<!-- End Google Analytics -->""",
        ),
        (
            GtagDimensionsStrategy.SET_CONFIG,
            False,
            """<!-- Google Analytics -->\n<amp-analytics type="googleanalytics">\n<script type="application/json">\n{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}\n</script>\n</amp-analytics>\n<!-- End Google Analytics -->""",
        ),
        (
            GtagDimensionsStrategy.CONFIGNOPAGEVIEW_SET_EVENT,
            True,
            """<!-- Google Analytics -->\n<amp-analytics type="googleanalytics">\n<script type="application/json">\n{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}\n</script>\n</amp-analytics>\n<!-- End Google Analytics -->""",
        ),
        (
            GtagDimensionsStrategy.CONFIGNOPAGEVIEW_SET_EVENT,
            False,
            """<!-- Google Analytics -->\n<amp-analytics type="googleanalytics">\n<script type="application/json">\n{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}\n</script>\n</amp-analytics>\n<!-- End Google Analytics -->""",
        ),
    )
    data__test_custom_variables__global__html = data__test_custom_variables__html
    data__test_advanced__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_advanced__nonglobal__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"extraUrlParams":{"cd9":"jonathan"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_userid_prerender__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"extraUrlParams":{"user_id":"cecil"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_userid_prerender_multi__html = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"extraUrlParams":{"user_id":"cecil"},"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_userid_postrender__html = ""
    data__test_userid_postrender_multi__html = ""
    data__test_amp_clientid_integration = """\
<!-- Google Analytics -->
<amp-analytics type="googleanalytics">
<script type="application/json">
{"triggers":{"trackPageview":{"on":"visible","request":"pageview"}},"vars":{"account":"UA-123123-1"}}
</script>
</amp-analytics>
<!-- End Google Analytics -->"""
    data__test_amp_clientid_integration_head = {
        True: """<meta name="amp-google-client-id-api" content="googleanalytics">\n<script async custom-element="amp-analytics" src="https://cdn.ampproject.org/v0/amp-analytics-0.1.js"></script>""",
        False: """<script async custom-element="amp-analytics" src="https://cdn.ampproject.org/v0/amp-analytics-0.1.js"></script>""",
    }


class TestSetup(unittest.TestCase):
    def test_defaults(self):
        writer = AnalyticsWriter(
            "UA-123123-1", json_dumps_callable=custom_json_dumps_sorted
        )
        self.assertEqual(writer.mode, AnalyticsMode._default)
        self.assertEqual(AnalyticsMode._default, AnalyticsMode.ANALYTICS)
        self.assertTrue(writer.use_comments)
        self.assertFalse(writer.single_push)
        self.assertIsNone(writer.force_ssl)
        self.assertTrue(writer.global_custom_data)

    def test_passin(self):
        writer = AnalyticsWriter(
            "UA-123123-1",
            json_dumps_callable=custom_json_dumps_sorted,
            mode=AnalyticsMode.GA_JS,
            use_comments=False,
            single_push=True,
            force_ssl=True,
            global_custom_data=False,
        )
        self.assertEqual(writer.mode, AnalyticsMode.GA_JS)
        self.assertFalse(writer.use_comments)
        self.assertTrue(writer.single_push)
        self.assertTrue(writer.force_ssl)
        self.assertFalse(writer.global_custom_data)
