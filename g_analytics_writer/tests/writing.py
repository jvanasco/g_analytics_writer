from __future__ import print_function

from g_analytics_writer import AnalyticsWriter
from g_analytics_writer import AnalyticsMode
# import g_analytics_writer.pyramid_integration

# core testing facility
import unittest
import re

# regexes to test against
re_refresh_15 = re.compile('<meta http-equiv="refresh" content="15"/>')
re_other_charset = re.compile('<meta charset="utf8"/>')

# used for writing tests
PRINT_RENDERS = 1

# pyramid testing requirements
# from pyramid import testing

"""
class AnalyticsMode(object):
    GA_JS = 1
    ANALYTICS = 2
    GTAG = 4
"""

class CoreTests(object):

    mode = None
    _test_single_push = None
    
    def test_pageview(self):
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_pageview__html)

        writer.set_account_additional__add('UA-123123-3')
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
        a = AnalyticsWriter('UA-123123-1', mode=self.mode)
        # switch account
        a.set_account('UA-123123-2')
        # add account
        a.set_account_additional__add('UA-123123-3')
        html_rendered = a.render()
        if PRINT_RENDERS:
            print(html_rendered)
        self.assertEqual(html_rendered, self.data__test_multiple_accounts__html)

    def test_comments(self):
        """
        just tests to see the framing comments toggle works
        """
        comments = AnalyticsWriter('UA-123123-1', mode=self.mode, use_comments=True)
        html_comments = comments.render()
        if PRINT_RENDERS:
            print(html_comments)
        self.assertEqual(html_comments, self.data__test_comments__html_comments)
        
        nocomments = AnalyticsWriter('UA-123123-1', mode=self.mode, use_comments=False)
        html_nocomments = nocomments.render()
        if PRINT_RENDERS:
            print(html_nocomments)
        self.assertEqual(html_nocomments, self.data__test_comments__html_nocomments)

    def test_transaction_good(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
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
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        writer.add_transaction(self.data__transaction_dict_bad)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_transaction_bad__html)

    def test_transaction_good_single_push(self):
        """
        just tests to see the framing comments toggle works
        """
        if not self._test_single_push:
            raise unittest.SkipTest("single_push not tested on %s" % self.__class__.__name__)
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode, single_push=True)
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
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        writer.track_event(self.data__event_good_1)
        writer.track_event(self.data__event_good_2)
        writer.track_event(self.data__event_good_3)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_track_event__html)

    def test_crossdomain(self):
        """
        just tests to see the framing comments toggle works
        """
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        writer.set_crossdomain_tracking('foo.example.com')
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_crossdomain__html)

        link_attrs = writer.render_crossdomain_link_attrs("https://example.com/foo.html")
        if PRINT_RENDERS:
            print(link_attrs)
        self.assertEqual(link_attrs, self.data__test_crossdomain__html_link_attrs)

        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        writer.set_crossdomain_tracking('foo.example.com', all_domains='bar.example.com')
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_crossdomain__html_multi)

    def test_custom_variables(self):
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        (index, name, value, opt_scope) = self.data__custom_variables
        writer.set_custom_variable(index, name, value, opt_scope=opt_scope)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_custom_variables__html)

        writer.global_custom_data = True
        as_html_global = writer.render()
        if PRINT_RENDERS:
            print(as_html_global)
        self.assertEqual(as_html_global, self.data__test_custom_variables__global__html)

    def test_advanced(self):
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        (index, name, value, opt_scope) = self.data__custom_variables
        # crossdomain
        writer.set_crossdomain_tracking('foo.example.com')
        # add account
        writer.set_account_additional__add('UA-123123-2')
        writer.set_account_additional__add('UA-123123-3')
        writer.set_custom_variable(index, name, value, opt_scope=opt_scope)
        writer.track_event(self.data__event_good_1)
        writer.track_event(self.data__event_good_2)
        writer.track_event(self.data__event_good_3)
        writer.add_transaction(self.data__transaction_dict_good)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_advanced__html)

        writer.global_custom_data = True
        as_html_global = writer.render()
        if PRINT_RENDERS:
            print(as_html_global)
        self.assertEqual(as_html_global, self.data__test_advanced__global__html)
    
    def test_advanced_single_push(self):
        if not self._test_single_push:
            raise unittest.SkipTest("single_push not tested on %s" % self.__class__.__name__)
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode, single_push=True)
        (index, name, value, opt_scope) = self.data__custom_variables
        # crossdomain
        writer.set_crossdomain_tracking('foo.example.com')
        # add account
        writer.set_account_additional__add('UA-123123-2')
        writer.set_account_additional__add('UA-123123-3')
        writer.set_custom_variable(index, name, value, opt_scope=opt_scope)
        writer.track_event(self.data__event_good_1)
        writer.track_event(self.data__event_good_2)
        writer.track_event(self.data__event_good_3)
        writer.add_transaction(self.data__transaction_dict_good)
        writer.add_transaction_item(self.data__transaction_item_dict)
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_advanced_single_push__html)

    def test_userid_prerender(self):
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        writer.set_user_id('cecil')
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_prerender__html)

        # multiple accounts
        writer.set_account_additional__add('UA-123123-3')
        as_html = writer.render()
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_prerender_multi__html)

    def test_userid_postrender(self):
        writer = AnalyticsWriter('UA-123123-1', mode=self.mode)
        as_html = writer.setrender_user_id('cecil')
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_postrender__html)

        # multiple accounts
        writer.set_account_additional__add('UA-123123-3')
        as_html = writer.setrender_user_id('cecil')
        if PRINT_RENDERS:
            print(as_html)
        self.assertEqual(as_html, self.data__test_userid_postrender_multi__html)


# global dicts used for tests
# this lets us compare the different formats
data__transaction_dict_GA = {
    'transactionId': 1234,
    'affiliation': 'ga.js',
    'total': '100.00',
    'tax': '10.00',
    'shipping': '5.00',
    'city': 'brooklyn',
    'state': 'new york',
    'country': 'usa',
}
data__transaction_dict_Analytics = {
    'id': 1234,
    'affiliation': 'analytics.js',
    'revenue': '115.00',
    'tax': '10.00',
    'shipping': '5.00',
}
data__transaction_item_dict = {
    'id': 1234,  # transaction_id
    'name': 'T-Shirt',                # Product name. Required
    'sku': 'DD44',                    # SKU/code
    'category': 'Green Medium',       # Category or variation
    'price': '100.00',                 # Unit price
    'quantity': '1'
}

data__event_1__GA = {
    'category': 'Videos',
    'action': 'Play',
    'opt_label': 'action',
    'opt_value': 47,
    'opt_noninteraction': 1,
    }
data__event_2__GA = {
    'category': 'Videos',
    'action': 'Play',
    'opt_label': 'action',
    'opt_value': 47,
    'opt_noninteraction': None
    }
data__event_3__ANALYTICS_hit = {
    'category': 'category',
    'action': 'action',
    'metric18': 8000,
}
data__custom_variables__GA = (6, 'author', 'jonathan', 1, ) # index, name, value, opt_scope=None)
data__custom_variables__ANALYTICS = ('dimension9', 'name', 'jonathan', None, ) # index, name, value, opt_scope=None)

               
class TestGA(CoreTests, unittest.TestCase):
    mode = AnalyticsMode.GA_JS
    _test_single_push = True
    data__transaction_dict_good = data__transaction_dict_GA
    data__transaction_dict_bad = data__transaction_dict_Analytics
    data__transaction_item_dict = data__transaction_item_dict
    data__custom_variables = data__custom_variables__GA
    data__event_good_1 = data__event_1__GA
    data__event_good_2 = data__event_2__GA
    data__event_good_3 = data__event_3__ANALYTICS_hit
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
    data__test_transaction_good__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
_gaq.push(['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['_addItem','1234','DD44','T-Shirt','Green Medium','100.00','1']);
_gaq.push(['_trackTrans']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_transaction_bad__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_trackPageview']);
_gaq.push(['_addTrans',undefined,'analytics.js',undefined,'10.00','5.00',undefined,undefined,undefined]);
_gaq.push(['_addItem','1234','DD44','T-Shirt','Green Medium','100.00','1']);
_gaq.push(['_trackTrans']);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_transaction_good_single_push__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(
['_setAccount','UA-123123-1'],
['_trackPageview'],
['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['_addItem','1234','DD44','T-Shirt','Green Medium','100.00','1'],
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
_gaq.push(['_trackEvent','Videos','Play','action','47',true]);
_gaq.push(['_trackEvent','Videos','Play','action','47',false]);
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
    data__test_crossdomain__html_multi = data__test_crossdomain__html  # this doesn't support it the same way
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
    data__test_advanced__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount','UA-123123-1']);
_gaq.push(['_setDomainName','foo.example.com']);
_gaq.push(['_setAllowLinker',true]);
_gaq.push(['_setCustomVar',6,'author','jonathan',1]);
_gaq.push(['_trackPageview']);
_gaq.push(['_addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['_addItem','1234','DD44','T-Shirt','Green Medium','100.00','1']);
_gaq.push(['_trackTrans']);
_gaq.push(['_trackEvent','Videos','Play','action','47',true]);
_gaq.push(['_trackEvent','Videos','Play','action','47',false]);
_gaq.push(['trkr0._setAccount','UA-123123-3']);
_gaq.push(['trkr0._setDomainName','foo.example.com']);
_gaq.push(['trkr0._setAllowLinker',true]);
trkr0._gaq.push(['trkr0._setCustomVar',6,'author','jonathan',1]);
_gaq.push(['trkr0._trackPageview']);
_gaq.push(['trkr0._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['trkr0._addItem','1234','DD44','T-Shirt','Green Medium','100.00','1']);
_gaq.push(['trkr0._trackTrans']);
_gaq.push(['trkr0._trackEvent','Videos','Play','action','47',true]);
_gaq.push(['trkr0._trackEvent','Videos','Play','action','47',false]);
_gaq.push(['trkr1._setAccount','UA-123123-2']);
_gaq.push(['trkr1._setDomainName','foo.example.com']);
_gaq.push(['trkr1._setAllowLinker',true]);
trkr1._gaq.push(['trkr1._setCustomVar',6,'author','jonathan',1]);
_gaq.push(['trkr1._trackPageview']);
_gaq.push(['trkr1._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa']);
_gaq.push(['trkr1._addItem','1234','DD44','T-Shirt','Green Medium','100.00','1']);
_gaq.push(['trkr1._trackTrans']);
_gaq.push(['trkr1._trackEvent','Videos','Play','action','47',true]);
_gaq.push(['trkr1._trackEvent','Videos','Play','action','47',false]);
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>
<!-- End Google Analytics -->"""
    data__test_advanced__global__html = data__test_advanced__html
    data__test_advanced_single_push__html = """\
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
['_addItem','1234','DD44','T-Shirt','Green Medium','100.00','1'],
['_trackTrans'],
['_trackEvent','Videos','Play','action','47',true],
['_trackEvent','Videos','Play','action','47',false],
['trkr0._setAccount','UA-123123-3'],
['trkr0._setDomainName','foo.example.com'],
['trkr0._setAllowLinker',true],
['trkr0._setCustomVar',6,'author','jonathan',1],
['trkr0._trackPageview'],
['trkr0._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['trkr0._addItem','1234','DD44','T-Shirt','Green Medium','100.00','1'],
['trkr0._trackTrans'],
['trkr0._trackEvent','Videos','Play','action','47',true],
['trkr0._trackEvent','Videos','Play','action','47',false],
['trkr1._setAccount','UA-123123-2'],
['trkr1._setDomainName','foo.example.com'],
['trkr1._setAllowLinker',true],
['trkr1._setCustomVar',6,'author','jonathan',1],
['trkr1._trackPageview'],
['trkr1._addTrans','1234','ga.js','100.00','10.00','5.00','brooklyn','new york','usa'],
['trkr1._addItem','1234','DD44','T-Shirt','Green Medium','100.00','1'],
['trkr1._trackTrans'],
['trkr1._trackEvent','Videos','Play','action','47',true],
['trkr1._trackEvent','Videos','Play','action','47',false]
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
    data__test_userid_postrender__html = ''
    data__test_userid_postrender_multi__html = ''

class TestAnalytics(CoreTests, unittest.TestCase):
    mode = AnalyticsMode.ANALYTICS
    data__transaction_dict_good = data__transaction_dict_Analytics
    data__transaction_dict_bad = data__transaction_dict_GA
    data__transaction_item_dict = data__transaction_item_dict
    data__custom_variables = data__custom_variables__ANALYTICS
    data__event_good_1 = data__event_1__GA
    data__event_good_2 = data__event_2__GA
    data__event_good_3 = data__event_3__ANALYTICS_hit
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
    data__test_transaction_good__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('require','ecommerce');
ga('send','pageview');
ga('ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('ecommerce:send');
</script>
<!-- End Google Analytics -->"""
    data__test_transaction_bad__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('require','ecommerce');
ga('send','pageview');
ga('ecommerce:addTransaction',{"affiliation":"ga.js","tax":"10.00","id":"1234","shipping":"5.00"})
ga('ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
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
ga('linker:autoLink',['bar.example.com','foo.example.com']);
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
ga('send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('send','event','Videos','Play','action','47',{'nonInteraction':0});
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_link_attrs = ''  # empty string
    data__test_custom_variables__html = """\
<!-- Google Analytics -->
<script type="text/javascript">
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
ga('create','UA-123123-1','auto');
ga('send','pageview',{"dimension9":"jonathan"});
</script>
<!-- End Google Analytics -->"""
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
    data__test_advanced__html = """\
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
ga('ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('ecommerce:send');
ga('send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('send','event','Videos','Play','action','47',{'nonInteraction':0});
ga('create','UA-123123-3','auto','trkr0',{"allowLinker":true});
ga('trkr0.send','pageview',{"dimension9":"jonathan"});
ga('trkr0.ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('trkr0.ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('trkr0.ecommerce:send');
ga('trkr0.send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('trkr0.send','event','Videos','Play','action','47',{'nonInteraction':0});
ga('create','UA-123123-2','auto','trkr1',{"allowLinker":true});
ga('trkr1.send','pageview',{"dimension9":"jonathan"});
ga('trkr1.ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('trkr1.ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('trkr1.ecommerce:send');
ga('trkr1.send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('trkr1.send','event','Videos','Play','action','47',{'nonInteraction':0});
</script>
<!-- End Google Analytics -->"""
    data__test_advanced__global__html = """\
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
ga('ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('ecommerce:send');
ga('send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('send','event','Videos','Play','action','47',{'nonInteraction':0});
ga('create','UA-123123-3','auto','trkr0',{"allowLinker":true});
ga('trkr0.set',{"dimension9":"jonathan"});
ga('trkr0.send','pageview');
ga('trkr0.ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('trkr0.ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('trkr0.ecommerce:send');
ga('trkr0.send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('trkr0.send','event','Videos','Play','action','47',{'nonInteraction':0});
ga('create','UA-123123-2','auto','trkr1',{"allowLinker":true});
ga('trkr1.set',{"dimension9":"jonathan"});
ga('trkr1.send','pageview');
ga('trkr1.ecommerce:addTransaction',{"affiliation":"analytics.js","tax":"10.00","id":"1234","shipping":"5.00","revenue":"115.00"})
ga('trkr1.ecommerce:addItem',{"sku":"DD44","category":"Green Medium","name":"T-Shirt","price":"100.00","id":"1234","quantity":"1"})
ga('trkr1.ecommerce:send');
ga('trkr1.send','event','Videos','Play','action','47',{'nonInteraction':1});
ga('trkr1.send','event','Videos','Play','action','47',{'nonInteraction':0});
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


class TestGtag(CoreTests, unittest.TestCase):
    """
    python -munittest g_analytics_writer.tests.writing.TestGtag.test_track_event

    python -munittest g_analytics_writer.tests.writing.TestGtag
    python -munittest g_analytics_writer.tests.writing.TestGtag.test_advanced
    python -munittest g_analytics_writer.tests.writing.TestGtag.test_crossdomain
    """
    mode = AnalyticsMode.GTAG
    data__transaction_dict_good = data__transaction_dict_Analytics
    data__transaction_dict_bad = data__transaction_dict_GA
    data__transaction_item_dict = data__transaction_item_dict
    data__custom_variables = data__custom_variables__ANALYTICS
    data__event_good_1 = data__event_1__GA
    data__event_good_2 = data__event_2__GA
    data__event_good_3 = data__event_3__ANALYTICS_hit
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
    data__test_comments__html_comments ="""\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
</script>
<!-- End Google Analytics -->"""
    data__test_comments__html_nocomments ="""\
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
</script>"""
    data__test_transaction_good__html ="""\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
gtag('event', 'purchase', {"items":[{"category":"Green Medium","price":"100.00","id":"1234","quantity":"1"}],"tax":"10.00","value":"115.00","affiliation":"analytics.js","shipping":"5.00","transaction_id":"1234"}
</script>
<!-- End Google Analytics -->"""
    data__test_transaction_bad__html ="""\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
gtag('event', 'purchase', {"affiliation":"ga.js","tax":"10.00","shipping":"5.00","transaction_id":"1234","items":[{"category":"Green Medium","price":"100.00","id":"1234","quantity":"1"}]}
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html =""""""
    data__test_crossdomain__html_multi =""""""
    data__test_track_event__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1');
gtag('event', 'Play', {"non_interaction":true,"event_label":"action","event_category":"Videos","value":"47"}
gtag('event', 'Play', {"non_interaction":false,"event_label":"action","event_category":"Videos","value":"47"}
</script>
<!-- End Google Analytics -->"""
    data__test_crossdomain__html_link_attrs = ''  # empty string
    data__test_custom_variables__html = """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-123123-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"}});
gtag('event','pageview',{"name":"jonathan"});
</script>
<!-- End Google Analytics -->"""
    data__test_custom_variables__global__html = data__test_custom_variables__html
    data__test_advanced__html = """"""
    data__test_advanced__global__html = data__test_advanced__html
    data__test_userid_prerender__html ="""\
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
