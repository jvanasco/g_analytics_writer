from json import dumps as json_dumps
import types


# logging
import logging
log = logging.getLogger(__name__)


# ==============================================================================

'''
def escape_text(text=''):
    """helper function"""
    return str(text).replace("\'", "\\'")
'''


def cleanup_js_dict_to_quoted(a_dict):
    copied_dict = {}
    for k, v in a_dict.items():
        if v is None:
            v = 'undefined'  # set to undefined
        else:
            v = "'%s'" % v  # wrap in single quotes
        copied_dict[k] = v
    return copied_dict


def itemDict_to_transactionId(itemDict):
    _transaction_id = itemDict.get('transactionId', None) or itemDict.get('id', None)
    return _transaction_id


def custom_dumps(data):
    return json_dumps(data, separators=(',', ':'))


def generate_tracker_name(secondary_account):
    secondary_account_name = None
    tracker_prefix = ''
    if secondary_account is not False:
        secondary_account_name = "trkr%s" % secondary_account
        tracker_prefix = '%s.' % secondary_account_name
    return (secondary_account_name, tracker_prefix)


class AnalyticsMode(object):
    GA_JS = 1
    ANALYTICS = 2
    # GTAG = 4
    
    _default = ANALYTICS
    _valid_modes = (GA_JS,
                    ANALYTICS,
                    # GTAG,
                    )
    _supports_single_push = (GA_JS, )


# ==============================================================================


class AnalyticsWriter(object):
    data_struct = None
    _mode = None

    def __init__(
        self,
        account_id,
        mode=AnalyticsMode._default,
        use_comments=True,
        single_push=False,
        force_ssl=None,
    ):
        """
        Sets up self.data_struct dict which we use for storage.

        You'd probably have something like this in your base controller:

        class Handler(object):
            def __init__(self, request):
                self.request = request
                h.gaq_setup('AccountId')


        """
        if mode not in AnalyticsMode._valid_modes:
            raise ValueError("invalid mode")
        self._mode = mode
        self._use_comments = use_comments
        
        # ga.js allows a force of ssl
        # https://developers.google.com/analytics/devguides/collection/gajs/#ssl
        self._force_ssl = force_ssl

        self.data_struct = {
            '*single_push': single_push,
            '*account_id': account_id,
            '*additional_accounts': set({}),
            '*tracked_events': [],
            '*custom_variables': {},
            '*transaction': {},  # dict of k/v by transactionId
            '*transaction_items': {},  # dict of k:LIST by transactionId
            '*crossdomain_tracking': None,
            '*user_id': None,
        }

    def set_account(self, account_id):
        """This should really never be called, best to setup during __init__, where it is required"""
        self.data_struct['*account_id'] = account_id

    def set_account_additional__add(self, account_id):
        """add an additional account id to send the data to.  please note - this is only tested to work with the async method.
        """
        self.data_struct['*additional_accounts'].add(account_id)

    def set_account_additional__del(self, account_id):
        try:
            self.data_struct['*additional_accounts'].remove(account_id)
        except KeyError:
            pass

    def set_single_push(self, bool_value):
        """
        `ga.js` supports a single 'push' event, which can consolidate the API calls
        """
        self.data_struct['*single_push'] = bool_value

    def track_event(self, track_dict):
        """
        ga.js
            _trackEvent(category, action, opt_label, opt_value, opt_noninteraction)
                String   category The general event category (e.g. "Videos"). 
                String   action The action for the event (e.g. "Play"). 
                String   opt_label An optional descriptor for the event.
                Int      opt_value An optional value associated with the event. You can see your event values in the Overview, Categories, and Actions reports, where they are listed by event or aggregated across events, depending upon your report view.
                Boolean  opt_noninteraction Default value is false. By default, the event hit sent by _trackEvent() will impact a visitor's bounce rate. By setting this parameter to true, this event hit will not be used in bounce rate calculations.

        analytics.js
                ga('send','event','category','action','opt_label', opt_value, {'nonInteraction': 1});
        """
        self.data_struct['*tracked_events'].append(track_dict)

    def set_custom_variable(self, index, value, name=None, opt_scope=None):
        """
        IMPORTANT.

        Note the following design decision:
            VALUE is required
            NAME is not, and comes after VALUE

        There are slight differences in how this is handled:

        ga.js

            this is configured ad-hoc
            
            there are up to 6 slots

            _gaq.push(['_setCustomVar', slot, name, value, scope)
            
            explained:

                _gaq.push(['_setCustomVar',
                  1,                           // Slot
                  'Customer Type',             // Name
                  'Paid',                      // Value
                  1                            // Scope (1 = User scope)
                ]);
        
        analytics.js

            https://developers.google.com/analytics/devguides/collection/analyticsjs/custom-dims-mets
            
            there are up to 20 dimeneions
        
            names are configured on the admin as "dimensions"
            
            ga('set','dimension1','Paid');
        """
        self.data_struct['*custom_variables'][index] = (value,
                                                        name if name else '',
                                                        opt_scope,
                                                        )

    def set_crossdomain_tracking(self, domain_name, all_domains=None):
        """
        ga.js
            just set in the domain name to link to
        """
        if self.data_struct['*crossdomain_tracking'] is None:
            self.data_struct['*crossdomain_tracking'] = {}
        self.data_struct['*crossdomain_tracking'] = {'domain': domain_name, }
        if all_domains:
            if type(all_domains) not in (list, tuple):
                all_domains = [all_domains, ]
            self.data_struct['*crossdomain_tracking']['all_domains'] = all_domains

    def render_crossdomain_link_attrs(self, link):
        """
        ga.js
            renders onclick
        analytics.js
            ANALYTICS loads a plugin which automates setting up the onclick events via javascript
        """
        if self._mode == AnalyticsMode.GA_JS:
            # should this compare to the domain?
            return '''onclick="_gaq.push(['_link','%s']); return false;"''' % link
        return ''
    
    def set_user_id(self, user_id):
        """
        ga.js - may not be supported
        analytics.js - supported
        """
        self.data_struct['*user_id'] = user_id

    def setrender_user_id(self, user_id):
        """
        used if the user_id wasn't set during setup
        google analytics
            // At a later time, once the `userId` value is known,
            // sets the value on the tracker.
            // Setting the userId doesn't send data to Google Analytics.
            // You must also use a pageview or event to send the data.
        """
        self.data_struct['*user_id'] = user_id
        if self._mode == AnalyticsMode.ANALYTICS:
            payload = []
            payload.append("""ga('set','userId','%s');""" % user_id)
            payload.append("""ga('send','event','authentication','user-id available');""")
            for (secondary_account, account_id) in enumerate(self.data_struct['*additional_accounts']):
                (secondary_account_name,
                 tracker_prefix
                 ) = generate_tracker_name(secondary_account)
                payload.append("""ga('%sset','userId','%s');""" % (tracker_prefix, user_id))
                payload.append("""ga('%ssend','event','authentication','user-id available');""" % tracker_prefix)
            return '\n'.join(payload)
        return ''

    def add_transaction(self, track_dict):
        """
        CORE DIFFERENCES
        
        
        ga.js                         | analytics.js
        ------------------------------+------------
        transactionId                 | id
        total [excludes tax/shipping] | -
        -                             | revenue [includes tax/shipping]
        city                          |
        state                         |
        country                       |
        
        -----
        
        
        ga.js   | https://developers.google.com/analytics/devguides/collection/gajs/methods/gaJSApiEcommerce?csw=1#_gat.GA_Tracker_._addTrans
            _addTrans(transactionId, affiliation, total, tax, shipping, city, state, country)
                String   transactionId Required. Internal unique transaction ID number for this transaction.
                String   affiliation Optional. Partner or store affiliation (undefined if absent).
                String   total Required. Total dollar amount of the transaction. Does not include tax and shipping and should only be considered the "grand total" if you explicity include shipping and tax.
                String   tax Optional. Tax amount of the transaction.
                String   shipping Optional. Shipping charge for the transaction.
                String   city Optional. City to associate with transaction.
                String   state Optional. State to associate with transaction.
                String   country Optional. Country to associate with transaction.
        
        analytics.js | https://developers.google.com/analytics/devguides/collection/upgrade/reference/gajs-analyticsjs
                     | https://developers.google.com/analytics/devguides/collection/analyticsjs/ecommerce
        
                id	text	Yes	The transaction ID. (e.g. 1234)
                affiliation	text	No	The store or affiliation from which this transaction occurred (e.g. Acme Clothing).
                revenue	currency	No	Specifies the total revenue or grand total associated with the transaction (e.g. 11.99). This value may include shipping, tax costs, or other adjustments to total revenue that you want to include as part of your revenue calculations.
                shipping	currency	No	Specifies the total shipping cost of the transaction. (e.g. 5)
                tax	currency	No	Specifies the total tax of the transaction. (e.g. 1.29)

                ga('ecommerce:addTransaction', {
                  'id': '1234',                     // Transaction ID. Required.
                  'affiliation': 'Acme Clothing',   // Affiliation or store name.
                  'revenue': '11.99',               // Grand Total.
                  'shipping': '5',                  // Shipping.
                  'tax': '1.29'                     // Tax.
                });

        """
        # stash this into a dict
        _transaction_id = itemDict_to_transactionId(track_dict)  # transactionId is ga.js; id is analytics.js
        self.data_struct['*transaction'][_transaction_id] = track_dict

    def add_transaction_item(self, track_dict):
        """
        ga.js   | https://developers.google.com/analytics/devguides/collection/gajs/methods/gaJSApiEcommerce#_gat.GA_Tracker_._addItem
            _addItem(transactionId, sku, name, category, price, quantity)
                String   transactionId Optional Order ID of the transaction to associate with item.
                String   sku Required. Item's SKU code.
                String   name Required. Product name. Required to see data in the product detail report.
                String   category Optional. Product category.
                String   price Required. Product price.
                String   quantity Required. Purchase quantity.

        analytics.js | https://developers.google.com/analytics/devguides/collection/upgrade/reference/gajs-analyticsjs
                     | https://developers.google.com/analytics/devguides/collection/analyticsjs/ecommerce

            ga('ecommerce:addItem', {
              'id': '1234',                     // Transaction ID. Required.
              'name': 'Fluffy Pink Bunnies',    // Product name. Required.
              'sku': 'DD23444',                 // SKU/code.
              'category': 'Party Toys',         // Category or variation.
              'price': '11.99',                 // Unit price.
              'quantity': '1'                   // Quantity.
            });
        """
        _transaction_id = itemDict_to_transactionId(track_dict)  # transactionId is ga.js; id is analytics.js
        if _transaction_id not in self.data_struct['*transaction_items']:
            self.data_struct['*transaction_items'][_transaction_id] = []
        self.data_struct['*transaction_items'][_transaction_id].append(track_dict)

    def _render__ga_js__inner(
        self,
        script,
        nested_script,
        account_id,
        single_push,
        secondary_account=False,
    ):
        """
        this handles the inner render for ga.js

        args/kwargs:        
            script = array of script lines
            nested_script = Array of single-push data
            account_id = current account_id, might be nested
            single_push = Boolean. True if this is a single-push element
            secondary_account = False or idx(0+).
        returns:
            tuple (script, nested_script)

        according to GA docs, the order to submit via javascript is:
        * _setAccount
        * _setDomainName
        * _setAllowLinker
        * _trackPageview

        Reference Documentation:
        
        cross domain tracking reference
        -------------------------------
        * http://code.google.com/apis/analytics/docs/tracking/gaTrackingSite.html

        Event Tracking - trackEvent
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEventTracking.html#_gat.GA_EventTracker_._trackEvent

            Constructs and sends the event tracking call to the Google Analytics Tracking Code. Use this to track visitor behavior on your website that is not related to a web page visit, such as interaction with a Flash video movie control or any user event that does not trigger a page request. For more information on Event Tracking, see the Event Tracking Guide.

            You can use any of the following optional parameters: opt_label, opt_value or opt_noninteraction. If you want to provide a value only for the second or 3rd optional parameter, you need to pass in undefined for the preceding optional parameter.

        Custom Variables - setCustomVar
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiBasicConfiguration.html#_gat.GA_Tracker_._setCustomVar

            _setCustomVar(index, name, value, opt_scope)
            Sets a custom variable with the supplied name, value, and scope for the variable. There is a 64-byte character limit for the name and value combined.

        Set Domain Name
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiDomainDirectory.html#_gat.GA_Tracker_._setDomainName

            _setDomainName(newDomainName)

        * via https://developers.google.com/analytics/devguides/collection/gajs/gaTrackingSite#yourDomainName
        
            _setDomainName('yourDomainName')

            What it does.
            This method sets the domain field of the cookie to the string provided in the parameter. With this method, you can control the domain name used by the cookie. You will ONLY have to set up linking between top-level domains because sub-domains will share the same cookies with their parents.

            When to use it.
            Use this when you want to treat top- and sub-domains as one entity and track in the same view (profile). Also use this when you want to track across multiple top-level domains AND their sub-domains. In this case, you will need to using linking between the top-level domains, but not between the top-level domains and their sub-domains.

            When not to use it.
            If you are tracking a single domain, you do not need to explicitly set the domain name.

        Set Allow Linker
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiDomainDirectory.html#_gat.GA_Tracker_._setAllowLinker  

            _setAllowLinker(bool)
        
        Add Transaction:
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEcommerce.html#_gat.GA_Tracker_._addTrans

            Creates a transaction object with the given values. As with _addItem(), this method handles only transaction tracking and provides no additional ecommerce functionality. Therefore, if the transaction is a duplicate of an existing transaction for that session, the old transaction values are over-written with the new transaction values. Arguments for this method are matched by position, so be sure to supply all parameters, even if some of them have an empty value.'

        Add Item:
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEcommerce.html#_gat.GA_Tracker_._addItem        

            Use this method to track items purchased by visitors to your ecommerce site. This method tracks individual items by their SKU. This means that the sku parameter is required. This method then associates the item to the parent transaction object via the orderId argument

        * Track Transaction
        -------------------------------
        * via http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEcommerce.html#_gat.GA_Tracker_._trackTrans

           Sends both the transaction and item data to the Google Analytics server. This method should be called after _trackPageview(), and used in conjunction with the _addItem() and addTrans() methods. It should be called after items and transaction elements have been set up.
        """
        if secondary_account is False:
            if self._force_ssl is True:
                # ga.js allows a force of ssl
                # https://developers.google.com/analytics/devguides/collection/gajs/#ssl
                if single_push:
                    nested_script.append(u"""['_gat._forceSSL']""")
                else:
                    script.append(u"""_gaq.push(['_gat._forceSSL']);""")

        (secondary_account_name,
         tracker_prefix
         ) = generate_tracker_name(secondary_account)
        
        # _setAccount
        if single_push:
            nested_script.append(u"""['%s_setAccount','%s']""" % (tracker_prefix, account_id))
        else:
            script.append(u"""_gaq.push(['%s_setAccount','%s']);""" % (tracker_prefix, account_id))

        # crossdomain_tracking
        """
        ga.js
            Online Store Domain: www.example-petstore.com
                Setup:
                    var pageTracker = _gat._getTracker('UA-12345-1');
                    pageTracker._setDomainName('example-petstore.com');
                    pageTracker._setAllowLinker(true);
                    pageTracker._trackPageview();
                Offsite Links:
                    <a href="http://www.my-example-blogsite.com/intro.html"
                       onclick="pageTracker._link('http://www.my-example-blogsite.com/intro.html'); return false;">

            Online Store Subdomain: dogs.example-petstore.com
                Setup:
                    var pageTracker = _gat._getTracker('UA-12345-1');
                    pageTracker._setDomainName('example-petstore.com');
                    pageTracker._setAllowLinker(true);
                    pageTracker._trackPageview();
                Offsite Links:
                    <a href="http://www.my-example-blogsite.com/intro.html"
                       onclick="pageTracker._link('http://www.my-example-blogsite.com/intro.html'); return false;">

            Blog Domain: www.my-example-blogsite.com
                Setup:
                    var pageTracker = _gat._getTracker('UA-12345-1');
                    pageTracker._setDomainName('my-example-blogsite.com');
                    pageTracker._setAllowLinker(true);
                    pageTracker._trackPageview();
                Offsite Links:
                    <a href="http://dogs.example-petstore.com/intro.html"
                       onclick="pageTracker._link('http://dogs.example-petstore.com/intro.html'); return false;">

        async
            Online Store Domain: www.example-petstore.com
                Setup:
                    var _gaq = _gaq || [];
                    _gaq.push(['_setAccount', 'UA-12345-1']);
                    _gaq.push(['_setDomainName', 'example-petstore.com']);
                    _gaq.push(['_setAllowLinker', true]);
                    _gaq.push(['_trackPageview']);        
                Offsite Links:
                    <a href="http://www.my-example-blogsite.com/intro"
                       onclick="_gaq.push(['_link', 'http://www.my-example-blogsite.com/intro.html']); return false;">
            Online Store Subdomain: dogs.example-petstore.com
                Setup:
                    var _gaq = _gaq || [];
                    _gaq.push(['_setAccount', 'UA-12345-1']);
                    _gaq.push(['_setDomainName', 'example-petstore.com']);
                    _gaq.push(['_setAllowLinker', true]);
                    _gaq.push(['_trackPageview']);
                Offsite Links:
                    <a href="http://www.my-example-blogsite.com/intro.html"
                       onclick="_gaq.push(['_link', 'http://www.my-example-blogsite.com/intro.html']); return false;">
            Blog Domain: www.my-example-blogsite.com
                Setup:
                    var _gaq = _gaq || [];
                    _gaq.push(['_setAccount', 'UA-12345-1']);
                    _gaq.push(['_setDomainName', 'my-example-blogsite.com']);
                    _gaq.push(['_setAllowLinker', true]);
                    _gaq.push(['_trackPageview']);
                Offsite Links:
                    <a href="http://dogs.example-petstore.com/intro.html"
                       onclick="_gaq.push(['_link', 'http://dogs.example-petstore.com/intro.html']); return false;">
        """
        if self.data_struct['*crossdomain_tracking']:
            if single_push:
                nested_script.append(u"""['%s_setDomainName','%s']""" % (tracker_prefix, self.data_struct['*crossdomain_tracking']['domain']))
                nested_script.append(u"""['%s_setAllowLinker',true]""" % (tracker_prefix))
            else:
                script.append(u"""_gaq.push(['%s_setDomainName','%s']);""" % (tracker_prefix, self.data_struct['*crossdomain_tracking']['domain']))
                script.append(u"""_gaq.push(['%s_setAllowLinker',true]);""" % tracker_prefix)

        # _setCustomVar is next
        for index in sorted(self.data_struct['*custom_variables'].keys()):
            # for ga.js:
            # index == str(integer)
            # _payload == (value, name, opt_scope)
            # however... we want to send (name, value, opt_scope)
            _payload = self.data_struct['*custom_variables'][index]
            if not _payload: continue
            _payload = (tracker_prefix, index, _payload[1], _payload[0], _payload[2], )
            if _payload[4]:
                formatted = u"""['%s_setCustomVar',%s,'%s','%s',%s]""" % _payload
            else:
                formatted = u"""['%s_setCustomVar',%s,'%s','%s']""" % _payload[:4]
            if single_push:
                nested_script.append(formatted)
            else:
                script.append(u"""%s_gaq.push(%s);""" % (tracker_prefix, formatted))

        if single_push:
            nested_script.append(u"""['%s_trackPageview']""" % tracker_prefix)
        else:
            script.append(u"""_gaq.push(['%s_trackPageview']);""" % tracker_prefix)

        # according to GA docs, the order to submit via javascript is:
        # # _trackPageview
        # # _addTrans
        # # _addItem
        # # _trackTrans
        if self.data_struct['*transaction']:
            for transaction_id in self.data_struct['*transaction'].keys():
                # _addTrans(transactionId, affiliation, total, tax, shipping, city, state, country)
                transaction_dict = self.data_struct['*transaction'][transaction_id]
                # these two fields are REQUIRED
                for i in ['transactionId', 'total']:  # fix required ; let javascript show errors if null
                    if i not in transaction_dict:
                        log.error('transaction field is missing: %s', i)
                        transaction_dict[i] = None
                for i in ['affiliation', 'tax', 'shipping', 'city', 'state', 'country']:  # fix optionals before positioning
                    if i not in transaction_dict:
                        transaction_dict[i] = None
                cleaned_dict = cleanup_js_dict_to_quoted(transaction_dict)
                cleaned_dict['_tracker_prefix'] = tracker_prefix
                _formatted = """['%(_tracker_prefix)s_addTrans',%(transactionId)s,%(affiliation)s,%(total)s,%(tax)s,%(shipping)s,%(city)s,%(state)s,%(country)s]""" % cleaned_dict
                if single_push:
                    nested_script.append(_formatted)
                else:
                    script.append(u"""_gaq.push(%s);""" % _formatted)

                if transaction_id in self.data_struct['*transaction_items']:
                    for item_dict in self.data_struct['*transaction_items'][transaction_id]:
                        # _addItem(transactionId, sku, name, category, price, quantity)
                        cleaned_dict = {'transactionId': transaction_id}
                        _transaction_id = itemDict_to_transactionId(item_dict)  # transactionId is ga.js; id is analytics.js
                        # this is impossible due to how we store it
                        # if transaction_id != _transaction_id:
                        #    log.error("transaction id does not match")
                        for i in ['sku', 'name', 'category', 'price', 'quantity', ]:  # fix required ; let javascript show errors if null
                            if i in item_dict:
                                cleaned_dict[i] = item_dict[i]
                            else:
                                cleaned_dict[i] = None
                        cleaned_dict = cleanup_js_dict_to_quoted(cleaned_dict)
                        cleaned_dict['_tracker_prefix'] = tracker_prefix
                        _formatted = """['%(_tracker_prefix)s_addItem',%(transactionId)s,%(sku)s,%(name)s,%(category)s,%(price)s,%(quantity)s]""" % cleaned_dict
                        if single_push:
                            nested_script.append(_formatted)
                        else:
                            script.append(u"""_gaq.push(%s);""" % _formatted)

            # send the _trackTransaction
            # https://developers.google.com/analytics/devguides/collection/gajs/methods/gaJSApiEcommerce?csw=1#_gat.GA_Tracker_._addTrans
            # Sends both the transaction and item data to the Google Analytics server. This method should be called after _trackPageview(), and used in conjunction with the _addItem() and addTrans() methods. It should be called after items and transaction elements have been set up.
            if single_push:
                nested_script.append(u"""['%s_trackTrans']""" % tracker_prefix)
            else:
                script.append(u"""_gaq.push(['%s_trackTrans']);""" % tracker_prefix)

        else:
            if self.data_struct['*transaction_items']:
                log.error('no transaction registered, but transaction_items added')

        # events are handled in a peculiar way
        _events = []
        for _event_dict in self.data_struct['*tracked_events']:
            _event_args = []
            # the `_trackEvent` api expects the args in this order. render 'undefined'
            for field in ['category', 'action', 'opt_label', 'opt_value', 'opt_noninteraction', ]:
                if field in _event_dict:
                    _value = _event_dict[field]
                    if field in ('opt_noninteraction', ):
                        _value = str(bool(_value)).lower()
                    else:
                        _value = "'%s'" % _value
                else:
                    _value = "undefined"
                _event_args.append(_value)
            _events.append("""['%s_trackEvent',%s]""" % (tracker_prefix, ','.join(_event_args)))
        if _events:
            for _event in _events:
                if single_push:
                    nested_script.append(_event)
                else:
                    script.append(u"""_gaq.push(%s);""" % _event)
        # end events

        # done
        return script, nested_script

    def _render__ga_js(self):
        script = []
        nested_script = []
        if self._use_comments:
            script.append(u"""<!-- Google Analytics -->""")
        script.append(u"""<script type="text/javascript">""")
        script.append(u"""var _gaq = _gaq || [];""")

        single_push = self.data_struct['*single_push']

        # start the single push if we elected
        if single_push:
            script.append(u"""_gaq.push(""")

        (script,
         nested_script,
         ) = self._render__ga_js__inner(script,
                                        nested_script,
                                        self.data_struct['*account_id'],
                                        single_push,
                                        secondary_account=False,
                                        )
        for (idx, account_id) in enumerate(self.data_struct['*additional_accounts']):
            (script,
             nested_script,
             ) = self._render__ga_js__inner(script,
                                            nested_script,
                                            account_id,
                                            single_push,
                                            secondary_account=idx,
                                            )

        # close the single push if we elected
        if single_push:
            script.append(u""",\n""".join(nested_script))
            script.append(u""");""")

        script.append(u"""\
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();""")
        script.append(u"""</script>""")
        if self._use_comments:
            script.append('<!-- End Google Analytics -->')
        return u"""\n""".join(script)


    def _render__analytics__inner(
        self,
        script,
        nested_script,
        account_id,
        secondary_account=False,
    ):
        # precompute first
        create_args = {}
        if self.data_struct['*crossdomain_tracking']:
            create_args['allowLinker'] = True
        if self.data_struct['*user_id']:
            create_args['userId'] = self.data_struct['*user_id']
        
        (secondary_account_name,
         tracker_prefix
         ) = generate_tracker_name(secondary_account)
        
        # account_id first
        # create([trackingId], [cookieDomain], [name], [fieldsObject]);
        if not create_args:
            if secondary_account_name:
                script.append(u"""ga('create','%s','auto','%s');""" % (account_id, secondary_account_name))
            else:
                script.append(u"""ga('create','%s','auto');""" % account_id)
        else:
            create_args = custom_dumps(create_args)
            if secondary_account_name:
                script.append(u"""ga('create','%s','auto','%s',%s);""" % (account_id, secondary_account_name, create_args))
            else:
                script.append(u"""ga('create','%s','auto',%s);""" % (account_id, create_args))

        if secondary_account is False:
            # crossdomain
            if self.data_struct['*crossdomain_tracking']:
                script.append(u"""ga('require','linker');""")
                destination_domain = self.data_struct['*crossdomain_tracking']['domain']
                _all_domains = self.data_struct['*crossdomain_tracking'].get('all_domains')
                if _all_domains:
                    destination_domain = set([destination_domain, ])
                    destination_domain.update(_all_domains)
                    destination_domain = sorted(destination_domain)
                    destination_domain = ','.join(["'%s'" % domain for domain in destination_domain])
                else:
                    destination_domain = "'%s'" % destination_domain
                script.append(u"""ga('linker:autoLink',[%s]);""" % destination_domain)
            # ecommerce
            if self.data_struct['*transaction']:
                script.append(u"""ga('require','ecommerce');""")

        # custom variables?
        pagehit_data = {}
        for index in sorted(self.data_struct['*custom_variables'].keys()):
            # for ga.js:
            # index == str(integer)
            # payload == (value, name, opt_scope)
            # however... we only send the VALUE, because name+opt_scope are handled on the admin dashboard
            _payload = self.data_struct['*custom_variables'][index]
            if not _payload: continue
            pagehit_data[index] = _payload[0]  # value

        # pageview
        # ga('send', 'pageview');
        if pagehit_data:
            formatted_line = u"""ga('%ssend','pageview',%s);""" % (tracker_prefix, custom_dumps(pagehit_data))
            script.append(formatted_line)
        else:
            script.append(u"""ga('%ssend','pageview');""" % tracker_prefix)

        # according to GA docs, the order to submit via javascript is:
        # # ga('send', 'pageview');
        # # ga('require', 'ecommerce');   // Load the ecommerce plug-in.
        # # ecommerce:addTransaction
        # # ecommerce:addItem
        # # ga('ecommerce:send');
        if self.data_struct['*transaction']:

            for transaction_id in self.data_struct['*transaction'].keys():
                # _addTrans(transactionId, affiliation, total, tax, shipping, city, state, country)
                transaction_dict = self.data_struct['*transaction'][transaction_id]
                # required field
                cleaned_dict = {'id': str(transaction_id), }
                for i in ['affiliation', 'revenue', 'shipping', 'tax', ]:  # fix optionals before positioning
                    if i in transaction_dict:
                        v = transaction_dict[i]
                        cleaned_dict[i] = str(v) if v is not None else None
                _formatted = u"""ga('%secommerce:addTransaction',%s)""" % (tracker_prefix, custom_dumps(cleaned_dict))
                script.append(_formatted)

                if transaction_id in self.data_struct['*transaction_items']:
                    for item_dict in self.data_struct['*transaction_items'][transaction_id]:
                        # _addItem(transactionId, sku, name, category, price, quantity)
                        cleaned_dict = {'id': str(transaction_id), }
                        for i in ['name', ]:  # fix required ; let javascript show errors if null
                            cleaned_dict[i] = item_dict.get(i, None)
                        for i in ['sku', 'category', 'price', 'quantity']:
                            if i in item_dict:
                                v = item_dict[i]
                                cleaned_dict[i] = str(v) if v is not None else None
                        _formatted = u"""ga('%secommerce:addItem',%s)""" % (tracker_prefix, custom_dumps(cleaned_dict))
                        script.append(_formatted)
            script.append(u"""ga('%secommerce:send');""" % tracker_prefix)

        else:
            if self.data_struct['*transaction_items']:
                log.error('no transaction registered, but transaction_items added')
                
                
        # events
        # ga('send', 'event', 'category', 'action', 'opt_label', opt_value, {'nonInteraction': 1});
        _events = []
        for _event_dict in self.data_struct['*tracked_events']:
            _event_args = []
            # the `_trackEvent` api expects the args in this order. render 'undefined'
            for field in ['category', 'action', 'opt_label', 'opt_value', ]:
                if field in _event_dict:
                    _value = _event_dict[field]
                    if _value is not None:
                        _value = "'%s'" % _value
                else:
                    _value = u"undefined"
                _event_args.append(_value)
            if 'opt_noninteraction' in _event_dict:
                _value = int(bool(_event_dict.get('opt_noninteraction')))
                fieldsObject = u"{'nonInteraction':%s}" % _value
                _event_args.append(fieldsObject)
            _events.append(u"""ga('%ssend','event',%s);""" % (tracker_prefix, ','.join(_event_args)))
        if _events:
            script.extend(_events)

        return (script, nested_script)

    def _render__analytics(self, async=None):
        script = []
        nested_script = []
        if self._use_comments:
            script.append(u"""<!-- Google Analytics -->""")
        script.append(u"""<script type="text/javascript">""")
        script.append(u"""\
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');""")

        account_id = self.data_struct['*account_id']
        (script, 
         nested_script
         ) = self._render__analytics__inner(script,
                                            nested_script,
                                            account_id,
                                            secondary_account=False,
                                            )

        for (idx, account_id) in enumerate(self.data_struct['*additional_accounts']):
            (script,
             nested_script,
             ) = self._render__analytics__inner(script,
                                           nested_script,
                                           account_id,
                                           secondary_account=idx,
                                           )



        script.append(u"""</script>""")
        if self._use_comments:
            script.append('<!-- End Google Analytics -->')
        return u"""\n""".join(script)

    def _render_gtag_head(self):
        """
        it is now recommended to use the gtag javascript, placed in the HEAD
            * https://support.google.com/analytics/answer/1008080?hl=en&ref_topic=1008079
        """
        return TEMPLATE_gtag_head % {'account_id': self.data_struct['*account_id'] }

    def _render__gtag(self):
        """\
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=%(account_id)s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config','%(account_id)s');
</script>
"""
    def render(self, mode=None):
        """
        helper function. prints out GA code for you, in the right order.

        You'd probably call it like this in a Mako template:
            <head>
                ${h.render()|n}
            </head>

        Notice that you have to escape under Mako.
        For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html
        """
        if (mode is not None) and (mode not in AnalyticsMode._valid_modes):
            raise ValueError("invalid mode")
        mode = mode if mode is not None else self._mode


        if mode == AnalyticsMode.GA_JS:
            return self._render__ga_js()
        elif mode == AnalyticsMode.ANALYTICS:
            return self._render__analytics(async=True)

        return '<!-- unsupported AnalyticsMode -->'


# ==============================================================================


__all__ = ('AnalyticsWriter',
           'AnalyticsMode',
           )
