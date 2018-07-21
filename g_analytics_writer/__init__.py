from json import dumps as json_dumps
import pdb


# logging
import logging
log = logging.getLogger(__name__)


__VERSION__ = '0.2.0a2'


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


def source_dict_to_args(source_dict, args_order, remove_undefined=None):
    item_args = []
    for _field in args_order:
        _value = source_dict.get(_field, None)
        if _value is None:
            _value = 'undefined' # yo it's undefined
        elif type(_value) in (int, float):
            _value = "%s" % _value  # turn it into a string
        elif type(_value) is bool:
            _value = ("%s" % _value).lower()  # turn it into a string
        else:
            _value = "'%s'" % _value  # pop it in a quote
        item_args.append(_value)
    if remove_undefined:
        _max_defined = None
        for _idx, _value in enumerate(item_args):
            if _value != 'undefined':
               _max_defined = _idx
        if _max_defined is not None:
            item_args = item_args[:_max_defined+1]
        else:
            # TODO: log/error
            item_args = []
    return item_args


def itemDict_to_transactionId(itemDict):
    #                 ga.js                                  analytics.js                # gtag.js
    _transaction_id = itemDict.get('transactionId', None) or itemDict.get('id', None) or itemDict.get('transaction_id', None)
    return _transaction_id


def custom_dumps(data):
    return json_dumps(data, separators=(',', ':'))


PREFIXLEN_dimension = len('dimension')
PREFIXLEN_metric = len('metric')

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
    # 3 is reserved for ANALYTICS that is not async
    GTAG = 4

    _default = ANALYTICS
    _valid_modes = (GA_JS,
                    ANALYTICS,
                    GTAG,
                    )
    _supports_single_push = (GA_JS, )
    _ANALYTICS_fieldobject = 'fo'  # used as a unique value in `transaction_mapping`


class InvalidTag(Exception):
    """
    Base exception for invalid tags.
    A global instance of `INVALID_TAG` will be created and used for comparisons
    """
    pass


INVALID_TAG = InvalidTag()


# ==============================================================================


class AnalyticsWriter(object):
    data_struct = None
    _mode = None
    _modes_support_alternate = None
    single_push = None
    global_custom_data = None
    use_comments = True
    force_ssl = None

    def __init__(
        self,
        account_id,
        mode=AnalyticsMode._default,
        use_comments=True,
        single_push=False,
        force_ssl=None,
        modes_support_alternate=None,
        global_custom_data=None,
    ):
        """
        Sets up self.data_struct dict which we use for storage.

        You'd probably have something like this in your pyramid app:
        
            config.include('g_analytics_writer.pyramid_integration')
        
        That will mount a custom configured ``AnalyticsWriter`` object on the
        Pyramid ``request`` as `request.g_analytics_writer`
        

        Args-
            :account_id
                STRING
                The Google Analytics account id.
                example: UA-123123123-1
        KwArgs-
            :mode
                INT
                default: `AnalyticsMode._default` == analytics.js
                The INT from the ``AnalyticsMode`` class specifiying the
                output type.
                This can not be changed after instantiation, because it is used
                by some helper functions.
            :modes_support_alternate
                INT or LIST/TUPLE of INTs
                default: None
                if alternate modes are supported, the package will try to upgrade
                incompatible data to the newer formats. Disabling this can
                optimize Python operations per request.                
            :use_comments
                BOOLEAN
                default: True
                If ``True``, this package will generate the leading/trailing
                HTML comments that surround the HTML block. Disabling this can
                optimize HTML size.
            :single_push
                BOOLEAN
                default: False
                If ``True``, this package will output the entirety of a `ga.js`
                command in a single 'push'. Enabling this can
                optimize HTML size and Javascript execution.
            :force_ssl
                BOOLEAN
                default: None
                If ``True``, this package will instruct google_analytics to
                force a html connection on http connections.
            :global_custom_data
                BOOLEAN
                default: None
                If ``True``, will register the custom metrics/data for all page hits.
                This is only supported on `analytics.js`; `gtag.js` does not seem to have an option
        """
        if mode not in AnalyticsMode._valid_modes:
            raise ValueError("invalid mode")
        self._mode = mode
        if modes_support_alternate:
            # convert string/int to iterables
            if type(modes_support_alternate) not in (list, tuple):
                modes_support_alternate = (modes_support_alternate, )
            self._modes_support_alternate = modes_support_alternate
        self.use_comments = use_comments
        self.single_push = single_push
        self.global_custom_data = global_custom_data  # this is public!

        # ga.js allows a force of ssl
        # https://developers.google.com/analytics/devguides/collection/gajs/#ssl
        self.force_ssl = force_ssl

        self.data_struct = {
            '*account_id': account_id,
            '*additional_accounts': set({}),
            '*tracked_events': [],
            '*custom_dimensions': {},
            '*custom_metrics': {},
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

    def track_event(self, track_dict):
        """
        The tracking dict should be in this format:
            {'*category': the category
             '*action': the action
            }
        Notice the leading asterisk `*` on certain keys. An asterisk is the
        prefix for identifying `g_analytics_writer` native commands. These keys
        will be mapped onto relevant Google Analytics fields upon rendering.

        Keys without an prefixed asterisk will be interpreted as extra data to
        be submitted by fieldobjects or other methods.

        =========================================================================
        Chart of translated items
        *** note: items in this chart with a leading `{` are fieldObject keys ***
        *** note: other items are args ***
        =========================================================================
        native           | ga.js              | analytics.js    | gtag.js
        -----------------+--------------------+-----------------+-----------------
        *action          | action             | {eventAction    | action/"event name"
        *category        | category           | {eventCategory  | {event_category
        *label           | opt_label          | {eventLabel     | {event_label
        *value           | opt_value          | {eventValue     | {value
        *non_interaction | opt_noninteraction | {nonInteraction | non_interaction
        -----------------+--------------------+-----------------+-----------------
        `non_interaction` must be a boolean.
        other values will be rendered as-is.
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Platform Version Notes:
        
        gtag.js:
            * `category` is OPTIONAL
            * each default `action` has a default `category`
            * each default `action` *might* have a default `label`
            * custom events (`action``) have a default `category` of 'engagement' and a default `label` of 'not set'.

        ========================================================================

        Upstream Documentation

        gtag.js
            https://developers.google.com/analytics/devguides/collection/gtagjs/events#send_events
            
            # example
            gtag('event', <action>, {
              'event_category': <category>,
              'event_label': <label>,
              'value': <value>
            });

            # fields reference
            `<action>` is the string that will appear as the event action in Google Analytics Event reports.
            `<category>` is the string that will appear as the event category.
            `<label>` is the string that will appear as the event label.
            `<value>` is a non-negative integer that will appear as the event value.            
        
            only `action` is required

            * user timings have shifted:
                https://developers.google.com/analytics/devguides/collection/gtagjs/migration
                analytics.js    | gtag.js
                ----------------+--------
                timingValue     | value
                timingVar       | name

        analytics.js
            https://developers.google.com/analytics/devguides/collection/analyticsjs/events#implementation

            # example
            ga('send', 'event', [eventCategory], [eventAction], [eventLabel], [eventValue], [fieldsObject]);

            # fields reference
            https://developers.google.com/analytics/devguides/collection/analyticsjs/field-reference

            `eventCategory`  - required
            `eventAction`    - required
            `eventLabel`     - optional
            `eventValue`     - optional
            `nonInteraction` - optional
            
        ga.js
            https://developers.google.com/analytics/devguides/collection/gajs/eventTrackerGuide#setting-up-event-tracking

            # example
            _trackEvent(category, action, opt_label, opt_value, opt_noninteraction)
            
            # fields reference
            `category`            String  The general event category (e.g. "Videos").
            `action`              String  The action for the event (e.g. "Play").
            `opt_label`           String  An optional descriptor for the event.
            `opt_value`           Int     An optional value associated with the event. You can see your event values in the Overview, Categories, and Actions reports, where they are listed by event or aggregated across events, depending upon your report view.
            `opt_noninteraction`  Boolean Default value is false. By default, the event hit sent by _trackEvent() will impact a visitor's bounce rate. By setting this parameter to true, this event hit will not be used in bounce rate calculations.

        =====
        Conversion:
            analytics.js field  |   gtag.js parameter
            --------------------+-----------------------
            eventAction         |   event_action
            eventCategory       |   event_category
            eventLabel          |   event_label
            eventValue          |   value
        analytics js
            ga('send', 'event', {
              'eventCategory': 'Category',
              'eventAction': 'Action'
            });

           gtag('event', <action>, {
                'event_category': <category>,
                'event_label': <label>,
                'value': <value>
                 });
            gtag('event', 'video_auto_play_start', {
              'event_label': 'My promotional video',
              'event_category': 'video_auto_play',
              'non_interaction': true
            });

        """
        self.data_struct['*tracked_events'].append(track_dict)

    def set_custom_variable(self, index, name, value, opt_scope=None):
        self.set_custom_dimension(index, name, value, opt_scope=opt_scope)

    def set_custom_dimension(self, index, name, value, opt_scope=None):
        """
        IMPORTANT!!!

        Note the following distinction:
        * VALUE is required, NAME is not
        * Name can be passed in as "None" on `analytics.js` installs
        HOWEVER it is recommended that you pass in the Name
        
        INDEX/SLOT
            ga.js index is an int
            analytics & gtag, index is usually a "prefix" of "dimension" with 'int' appended
            if you pass in `dimension9`, it will be stripped to `9` then rendered as needed

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

            name+scope combos are configured on the admin as "dimensions"

            they are then set into the tracker instance as the dimention

                ga('set','dimension1','Paid');

            or they are sent in as pagedata
                ga('send','pageview',{"dimension1":"Paid"});
        """
        if type(index) is not int:
            if index.startswith('dimension'):
                index = index[PREFIXLEN_dimension:]
            
        self.data_struct['*custom_dimensions'][index] = (name,
                                                         value,
                                                         opt_scope,
                                                         )


    def set_custom_metric(self, index, name, value):
        """
        this is not tracked in ga.js
        this is supported in analytics and gtag
        """
        if type(index) is not int:
            if index.startswith('metric'):
                index = index[PREFIXLEN_metric:]
        self.data_struct['*custom_metrics'][index] = (name,
                                                      value,
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
            YOU MUST ENABLED THIS ON THE ADMIN DASHBOARD
        gtag.js - supported
            YOU MUST ENABLED THIS ON THE ADMIN DASHBOARD
        """
        self.data_struct['*user_id'] = user_id

    def setrender_user_id(self, user_id):
        """
        used if the user_id wasn't set during setup

        analytics.js - supported
            YOU MUST ENABLED THIS ON THE ADMIN DASHBOARD
        gtag.js - supported
            YOU MUST ENABLED THIS ON THE ADMIN DASHBOARD

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
        elif self._mode == AnalyticsMode.GTAG:
            # https://developers.google.com/analytics/devguides/collection/gtagjs/cookies-user-id
            payload = []
            account_id = self.data_struct['*account_id']
            payload.append("""gtag('config', '%s', {'user_id': '%s'});""" % (account_id, user_id))
            for alt_account_id in self.data_struct['*additional_accounts']:
                payload.append("""gtag('config', '%s', {'user_id': '%s'});""" % (alt_account_id, user_id))
            return '\n'.join(payload)
        return ''

    def add_transaction(self, track_dict):
        """
        IMPORTANT:
            gtag.js requires ecommerce to be configured in the dashboard's view settings


        CORE DIFFERENCES

        =========================================================================
        Chart of translated terms
        =========================================================================
        native           | ga.js              | analytics.js    | gtag.js
        -----------------+--------------------+-----------------+-----------------
        *id              | transactionId      | id              | transaction_id
        *affiliation     | . affiliation      | . affiliation   | . affiliation
        *total           | total              |                 | 
        *revenue         |                    | . revenue       | . value           
        *tax             | . tax              | . tax           | . tax
        *shipping        | . shipping         | . shipping      | . shipping
        *city            | . city             |                 | 
        *state           | . state            |                 | 
        *country         | . country          |                 | 
        *coupon          |                    | .! coupon       | . coupon
        *list_name       |                    | .! list         | . list_name
        *checkout_step   |                    | .! step         | . checkout_step
        *checkout_option |                    | .! option       | . checkout_option
        -----------------+--------------------+-----------------+-----------------
        items with a prefix `.` are optional 
        items with a prefix `!` require the enhanced ecommerce plugin
        # important info
            *total = excludes tax/shipping
            *revenue = includes tax/shipping
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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
                     | https://developers.google.com/analytics/devguides/collection/analyticsjs/field-reference

                id  text    Yes The transaction ID. (e.g. 1234)
                affiliation text    No  The store or affiliation from which this transaction occurred (e.g. Acme Clothing).
                revenue currency    No  Specifies the total revenue or grand total associated with the transaction (e.g. 11.99). This value may include shipping, tax costs, or other adjustments to total revenue that you want to include as part of your revenue calculations.
                shipping    currency    No  Specifies the total shipping cost of the transaction. (e.g. 5)
                tax currency    No  Specifies the total tax of the transaction. (e.g. 1.29)

                ga('ecommerce:addTransaction', {
                  'id': '1234',                     // Transaction ID. Required.
                  'affiliation': 'Acme Clothing',   // Affiliation or store name.
                  'revenue': '11.99',               // Grand Total.
                  'shipping': '5',                  // Shipping.
                  'tax': '1.29'                     // Tax.
                });

        gtag.js | https://developers.google.com/gtagjs/reference/event
                | https://developers.google.com/analytics/devguides/collection/analyticsjs/ecommerce

            Conversion

                Enhanced ecommerce action data
                analytics.js field  |   gtag.js parameter
                --------------------+-----------------------
                id                  |   transaction_id
                affiliation         |   affiliation
                revenue             |   value
                tax                 |   tax
                shipping            |   shipping
                coupon              |   coupon
                list                |   list_name
                step                |   checkout_step
                option              |   checkout_option
                --------------------+-----------------------

                Product and promotion actions
                --------------------------------+---------------------------------------
                analytics.js field	            |   gtag.js event
                add	                            |   add_to_cart
                checkout (first step)	        |   begin_checkout
                checkout (any subsequent step)	|   checkout_progress
                checkout_option	                |   set_checkout_option
                click		                    |   select_content (without promotions)
                detail	                	    |   view_item
                promo_click	                	|   select_content (with promotions)
                purchase		                |   purchase
                refund		                    |   refund
                remove		                    |   remove_from_cart
                --------------------------------+---------------------------------------

            event: purchase
            https://developers.google.com/gtagjs/reference/event
                purchase    transaction_id, value, currency, tax, shipping, items, coupon
            kwargs: items
                https://developers.google.com/gtagjs/reference/parameter#event_parameters
                    items   array
                    An array of items (typically a list of products). Used for ecommerce events.
                    items[].brand   string  'Google'    Brand of the item
                    items[].category    string  'Apparel/T-Shirts'  Item category
                    items[].creative_name   string  'spring_banner_2'   Name of a creative used
                    items[].creative_slot   string  'banner_slot_1' Name of the creative slot
                    items[].id  string  'P12345'    Unique ID/SKU for the item
                    items[].location_id string  'Mountain View' Location of the item
                    items[].name    string  'Android Warhol T-Shirt'    Item name
                    items[].price   currency    '29.2'  Purchase price of the item
                    items[].quantity    integer 2   Item quantity
            kwargs: currency
                https://developers.google.com/gtagjs/reference/parameter#event_parameters
                currency    string  'USD'   Purchase currency in 3-letter ISO_4217 format
            kwargs: tax
                https://developers.google.com/gtagjs/reference/parameter#event_parameters
                tax currency    '2.43'  Tax amount for transaction
            kwargs: shipping
                https://developers.google.com/gtagjs/reference/parameter#event_parameters
                shipping    currency    '5.99'  Shipping cost for transaction
            kwargs: value
                https://developers.google.com/gtagjs/reference/parameter#event_parameters
                value   number  22  Value (i.e. revenue) associated with the event
            kwargs: coupon
                https://developers.google.com/gtagjs/reference/parameter#event_parameters
                coupon  string  'spring_fun'    Coupon code for a purchasable item
        """
        # stash this into a dict
        _transaction_id = track_dict.get('*id', '')
        if not _transaction_id:
            raise ValueError("missing `*id`")
        if _transaction_id != str(_transaction_id):
            _transaction_id = str(_transaction_id)
            track_dict['*id'] = _transaction_id
        self.data_struct['*transaction'][_transaction_id] = track_dict

    def add_transaction_item(self, item_dict):
        """
        IMPORTANT:
            gtag.js requires ecommerce to be configured in the dashboard's view settings


        =========================================================================
        Chart of translated terms
        =========================================================================
        native           | ga.js              | analytics.js    | gtag.js
        -----------------+--------------------+-----------------+-----------------
        *id              | . transactionId    | id              | transaction_id
        *sku             | sku                | 
        *name            | name               | 
        *category        | . category         | 
        *price           | price              | 
        *quantity        | quantity           | 
        -----------------+--------------------+-----------------+-----------------
        items with a prefix `.` are optional 
        items with a prefix `!` require the enhanced ecommerce plugin
        # important info
            ga.js doesn't require transactionId, but this package does
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


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
        _transaction_id = item_dict.get('*transaction_id', '')
        if not _transaction_id:
            raise ValueError("missing `*transaction_id`")
        if _transaction_id != str(_transaction_id):
            _transaction_id = str(_transaction_id)
            item_dict['*transaction_id'] = _transaction_id
        if _transaction_id not in self.data_struct['*transaction_items']:
            self.data_struct['*transaction_items'][_transaction_id] = []
        self.data_struct['*transaction_items'][_transaction_id].append(item_dict)

    def _render__ga_js__inner(
        self,
        script,
        nested_script,
        account_id,
        secondary_account=False,
    ):
        """
        this handles the inner render for ga.js

        args/kwargs:
            script = array of script lines
            nested_script = Array of single-push data
            account_id = current account_id, might be nested
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
        _single_push = self.single_push
        if secondary_account is False:
            if self.force_ssl is True:
                # ga.js allows a force of ssl
                # https://developers.google.com/analytics/devguides/collection/gajs/#ssl
                if _single_push:
                    nested_script.append(u"""['_gat._forceSSL']""")
                else:
                    script.append(u"""_gaq.push(['_gat._forceSSL']);""")

        (secondary_account_name,
         tracker_prefix
         ) = generate_tracker_name(secondary_account)

        # _setAccount
        if _single_push:
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
            if _single_push:
                nested_script.append(u"""['%s_setDomainName','%s']""" % (tracker_prefix, self.data_struct['*crossdomain_tracking']['domain']))
                nested_script.append(u"""['%s_setAllowLinker',true]""" % (tracker_prefix))
            else:
                script.append(u"""_gaq.push(['%s_setDomainName','%s']);""" % (tracker_prefix, self.data_struct['*crossdomain_tracking']['domain']))
                script.append(u"""_gaq.push(['%s_setAllowLinker',true]);""" % tracker_prefix)

        # _setCustomVar is next
        for index in sorted(self.data_struct['*custom_dimensions'].keys()):
            # for ga.js:
            # index == str(integer)
            # _payload == (name, value, opt_scope)
            _payload = self.data_struct['*custom_dimensions'][index]
            if not _payload:
                continue
            _payload = (tracker_prefix, index, _payload[0], _payload[1], _payload[2], )
            if _payload[4]:
                formatted = u"""['%s_setCustomVar',%s,'%s','%s',%s]""" % _payload
            else:
                formatted = u"""['%s_setCustomVar',%s,'%s','%s']""" % _payload[:4]
            if _single_push:
                nested_script.append(formatted)
            else:
                script.append(u"""%s_gaq.push(%s);""" % (tracker_prefix, formatted))

        if _single_push:
            nested_script.append(u"""['%s_trackPageview']""" % tracker_prefix)
        else:
            script.append(u"""_gaq.push(['%s_trackPageview']);""" % tracker_prefix)

        # according to GA docs, the order to submit via javascript is:
        # # _trackPageview
        # # _addTrans
        # # _addItem
        # # _trackTrans
        if self.data_struct['*transaction']:
            # _addTrans(transactionId, affiliation, total, tax, shipping, city, state, country)
            # _addItem(transactionId, sku, name, category, price, quantity)
            _txn_fields_order = ('*id', '*affiliation', '*total', '*tax', '*shipping', '*city', '*state', '*country', )
            _txn_fields_required = ('*id', '*total', )
            _txn_fields_optional = ('*affiliation', '*tax', '*shipping', '*city', '*state', '*country', )
            _item_fields_order = ('*transaction_id', '*sku', '*name', '*category', '*price', '*quantity', )
            _item_fields_required = ('*transaction_id', '*sku', '*name', '*price', '*quantity', )
            _item_fields_optional = ('*category', )

            _valid_transactions = False
            for transaction_id in self.data_struct['*transaction'].keys():
                _transaction_dict = self.data_struct['*transaction'][transaction_id]
                try:
                    for _field in _txn_fields_required:
                        _value = _transaction_dict.get(_field, None)
                        if _value is None:
                            raise InvalidTag()
                except Exception:
                    _formatted = '/* invalid transaction */'
                    if _single_push:
                        nested_script.append(_formatted)
                    else:
                        script.append(u"""_gaq.push(%s);""" % _formatted)
                    continue
                _transaction_args = source_dict_to_args(_transaction_dict, _txn_fields_order, remove_undefined=True)
                _formatted = """['%(tracker_prefix)s_addTrans',%(joined_args)s]""" % {'tracker_prefix': tracker_prefix,
                                                                                     'joined_args': ','.join(_transaction_args)
                                                                                     }
                if _single_push:
                    nested_script.append(_formatted)
                else:
                    script.append(u"""_gaq.push(%s);""" % _formatted)

                _valid_transactions = True

                if transaction_id in self.data_struct['*transaction_items']:
                    for _item_dict in self.data_struct['*transaction_items'][transaction_id]:
                        try:
                            for _field in _item_fields_required:
                                _value = _item_dict.get(_field, None)
                                if _value is None:
                                    raise InvalidTag()
                        except Exception:
                            _formatted = '/* invalid transaction item */'
                            if _single_push:
                                nested_script.append(_formatted)
                            else:
                                script.append(u"""_gaq.push(%s);""" % _formatted)
                            continue

                        _item_args = source_dict_to_args(_item_dict, _item_fields_order, remove_undefined=True)
                        _formatted = """['%(tracker_prefix)s_addItem',%(joined_args)s]""" % {'tracker_prefix': tracker_prefix,
                                                                                             'joined_args': ','.join(_item_args)
                                                                                             }
                        if _single_push:
                            nested_script.append(_formatted)
                        else:
                            script.append(u"""_gaq.push(%s);""" % _formatted)

            if _valid_transactions:
                # send the _trackTransaction
                # https://developers.google.com/analytics/devguides/collection/gajs/methods/gaJSApiEcommerce?csw=1#_gat.GA_Tracker_._addTrans
                # Sends both the transaction and item data to the Google Analytics server. This method should be called after _trackPageview(), and used in conjunction with the _addItem() and addTrans() methods. It should be called after items and transaction elements have been set up.
                if _single_push:
                    nested_script.append(u"""['%s_trackTrans']""" % tracker_prefix)
                else:
                    script.append(u"""_gaq.push(['%s_trackTrans']);""" % tracker_prefix)

        else:
            if self.data_struct['*transaction_items']:
                log.error('no transaction registered, but transaction_items added')

        # EVENTS
        # example: _trackEvent(category, action, opt_label, opt_value, opt_noninteraction)
        # the `_trackEvent` api expects the args in this order. render 'undefined' if we don't have it.
        _events = []
        _event_fields_required = ('*category', '*action', )
        _event_fields_optional = ('*label', '*value', '*non_interaction', )
        for _event_dict in self.data_struct['*tracked_events']:
            _event_args = []
            _event_args_optional = []
            # events are expected to be a series of args
            try:
                for _field in _event_fields_required:
                    _value = _event_dict.get(_field)
                    if not _value:
                        raise InvalidTag()
                    _value = "'%s'" % _value  # pop it in a quote
                    _event_args.append(_value)
            except:
                _events.append(INVALID_TAG)
                continue
            # figure out the optional args, if any...
            for _field in _event_fields_optional:
                # set the value to a default of `None`
                # don't set it to `undefined` yet.
                # we need the `None` for tests...
                _value = _event_dict.get(_field, None)
                _event_args_optional.append(_value)
            if _event_args_optional:
                if all(e is None for e in _event_args_optional):
                    # reset this
                    _event_args_optional = []
                else:    
                    # upgrade `None` to `"undefined"`, other items are strings
                    for _idx, _value in enumerate(_event_args_optional):
                        if _value is None:
                            _value = 'undefined' # yo it's undefined
                        elif type(_value) in (int, float):
                            _value = "%s" % _value  # turn it into a string
                        elif type(_value) is bool:
                            _value = ("%s" % _value).lower()  # turn it into a string
                        else:
                            _value = "'%s'" % _value  # pop it in a quote
                        _event_args_optional[_idx] = _value
                    # remove every 'undefined' from the tail of the list
                    _max_defined = None
                    for _idx, _value in enumerate(_event_args_optional):
                        if _value != 'undefined':
                           _max_defined = _idx
                    if _max_defined is not None:
                        _event_args_optional = _event_args_optional[:_max_defined+1]
                    else:    
                        _event_args_optional = []
            _event_args_all = _event_args + _event_args_optional
            _events.append("""['%s_trackEvent',%s]""" % (tracker_prefix, ','.join(_event_args_all)))
        if _events:
            for _event in _events:
                if _single_push:
                    if _event is INVALID_TAG:
                        nested_script.append("/* _trackEvent: incompatible event */")
                    else:
                        nested_script.append(_event)
                else:
                    if _event is INVALID_TAG:
                        script.append("/* _trackEvent: incompatible event */")
                    else:
                        script.append(u"""_gaq.push(%s);""" % _event)
        # end events

        # done
        return script, nested_script

    def _render__ga_js(self):
        script = []
        nested_script = []
        if self.use_comments:
            script.append(u"""<!-- Google Analytics -->""")
        script.append(u"""<script type="text/javascript">""")
        script.append(u"""var _gaq = _gaq || [];""")
        
        _single_push = self.single_push

        # start the single push if we elected
        if _single_push:
            script.append(u"""_gaq.push(""")

        (script,
         nested_script,
         ) = self._render__ga_js__inner(script,
                                        nested_script,
                                        self.data_struct['*account_id'],
                                        secondary_account=False,
                                        )
        for (idx, account_id) in enumerate(self.data_struct['*additional_accounts']):
            (script,
             nested_script,
             ) = self._render__ga_js__inner(script,
                                            nested_script,
                                            account_id,
                                            secondary_account=idx,
                                            )

        # close the single push if we elected
        if _single_push:
            script.append(u""",\n""".join(nested_script))
            script.append(u""");""")

        script.append(u"""\
(function() {
var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
ga.src = ('https:' == document.location.protocol ? 'https://ssl': 'http://www') + '.google-analytics.com/ga.js';
var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();""")
        script.append(u"""</script>""")
        if self.use_comments:
            script.append('<!-- End Google Analytics -->')
        return u"""\n""".join(script)

    def _render__analytics__inner(
        self,
        script,
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

        pagehit_data = {}
        custom_data = {}

        # custom variables?
        for index in sorted(self.data_struct['*custom_dimensions'].keys()):
            # for ga.js:
            # index == str(integer)
            # payload == (name, value, opt_scope)
            # however... we only need send the VALUE, because name+opt_scope are handled on the admin dashboard
            _payload = self.data_struct['*custom_dimensions'][index]
            if not _payload:
                continue
            # remember, we stripped `dimension` out
            custom_data["dimension%s" % index] = _payload[1]  # value
        for index in sorted(self.data_struct['*custom_metrics'].keys()):
            # for ga.js:
            # index == str(integer)
            # payload == (name, value, opt_scope)
            # however... we only need send the VALUE, because name+opt_scope are handled on the admin dashboard
            _payload = self.data_struct['*custom_metrics'][index]
            if not _payload:
                continue
            # remember, we stripped `metric` out
            custom_data["metric%s" % index] = _payload[1]  # value
        
        if self.global_custom_data:
            # update the entire tracker
            script.append(u"""ga('%sset',%s);""" % (tracker_prefix, custom_dumps(custom_data)))
        else:
            # update our pagedata items
            # pagehit_data.update(custom_data)
            pagehit_data = custom_data

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
                for i in ['affiliation', 'revenue', 'shipping', 'tax', 'currency', ]:  # fix optionals before positioning
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
                        for i in ['sku', 'category', 'price', 'quantity', 'currency', ]:
                            if i in item_dict:
                                v = item_dict[i]
                                cleaned_dict[i] = str(v) if v is not None else None
                        _formatted = u"""ga('%secommerce:addItem',%s)""" % (tracker_prefix, custom_dumps(cleaned_dict))
                        script.append(_formatted)
            script.append(u"""ga('%secommerce:send');""" % tracker_prefix)

        else:
            if self.data_struct['*transaction_items']:
                log.error('no transaction registered, but transaction_items added')

        # EVENTS
        # example: ga('send', 'event', [eventCategory], [eventAction], [eventLabel], [eventValue], [fieldsObject]);
        _events = []
        _event_fields_required = ('*category', '*action', )
        _event_fields_optional = ('*label', '*value', )
        _event_fields_optional_fieldobject = (('*non_interaction', 'nonInteraction'), )
        for _event_dict in self.data_struct['*tracked_events']:
            _event_args = []
            _event_args_optional = []
            _event_fieldobject = {}
            # events are expected to be a series of args
            try:
                for _field in _event_fields_required:
                    _value = _event_dict.get(_field)
                    if not _value:
                        raise InvalidTag()
                    _value = "'%s'" % _value  # pop it in a quote
                    _event_args.append(_value)
            except:
                _events.append(INVALID_TAG)
                continue
            # figure out the optional args, if any...
            for _field in _event_fields_optional:
                # set the value to a default of `None`
                # don't set it to `undefined` yet.
                # we need the `None` for tests...
                _value = _event_dict.get(_field, None)
                _event_args_optional.append(_value)
            if _event_args_optional:
                if not any(_event_args_optional):
                    # reset this
                    _event_args_optional = []
                else:    
                    # upgrade `None` to `"undefined"`, other items are strings
                    for _idx, _value in enumerate(_event_args_optional):
                        if _value is None:
                            _value = 'undefined' # yo it's undefined
                        else:
                            if type(_value) in (int, float):
                                _value = "%s" % _value  # turn it into a string
                            elif type(_value) is bool:
                                _value = ("%s" % _value).lower()  # turn it into a string
                            else:
                                _value = "'%s'" % _value  # pop it in a quote
                        _event_args_optional[_idx] = _value
                    # remove every 'undefined' from the tail of the list
                    _max_defined = None
                    for _idx, value in enumerate(_event_args_optional):
                        if _value != 'undefined':
                           _max_defined = _idx
                    if _max_defined is not None:
                        _event_args_optional = _event_args_optional[:_max_defined+1]
                    else:    
                        _event_args_optional = []
            # figure out the fieldobject args if any.
            for (_field_src, _field_dest) in _event_fields_optional_fieldobject:
                # set the value to a default of `None`
                # don't set it to `undefined` yet.
                # we need the `None` for tests...
                _value = _event_dict.get(_field_src, None)
                if _value is not None:
                    _event_fieldobject[_field_dest] = _value

            _event_args_all = _event_args + _event_args_optional
            if _event_fieldobject:
                _event_args_all.append(custom_dumps(_event_fieldobject))
            _events.append(u"""ga('%ssend','event',%s);""" % (tracker_prefix, ','.join(_event_args_all)))

        if _events:
            for _event in _events:
                if _event is INVALID_TAG:
                    script.append("/* ga('%ssend': incompatible event */" % tracker_prefix)
                else:
                    script.append(_event)

        return script

    def _render__analytics(self, async=None):
        script = []
        if self.use_comments:
            script.append(u"""<!-- Google Analytics -->""")
        script.append(u"""<script type="text/javascript">""")
        script.append(u"""\
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');""")

        account_id = self.data_struct['*account_id']
        script = self._render__analytics__inner(script,
                                                account_id,
                                                secondary_account=False,
                                                )

        for (idx, account_id) in enumerate(self.data_struct['*additional_accounts']):
            script = self._render__analytics__inner(script,
                                                    account_id,
                                                    secondary_account=idx,
                                                    )

        script.append(u"""</script>""")
        if self.use_comments:
            script.append('<!-- End Google Analytics -->')
        return u"""\n""".join(script)

    def _render__gtag(self):
        """
        migration guide: https://developers.google.com/analytics/devguides/collection/gtagjs/migration
        """
        script = []
        account_id = self.data_struct['*account_id']
        if self.use_comments:
            # script.append(u"""<!-- Google Analytics -->""")
            script.append(u"""<!-- Global site tag (gtag.js) - Google Analytics -->""")
        script.append(u"""\
<script async src="https://www.googletagmanager.com/gtag/js?id=%(account_id)s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
""" % {'account_id': account_id})

        # initial config args
        create_args = {}
        if self.data_struct['*user_id']:
            create_args['user_id'] = self.data_struct['*user_id']
        jsons_custom_values = None
        if self.data_struct['*custom_dimensions']:
            # this will be: 'dimension%s' = name
            custom_map = {}
            # this will be: name = value
            custom_values = {}
            for index in sorted(self.data_struct['*custom_dimensions'].keys()):
                _payload = self.data_struct['*custom_dimensions'][index]
                custom_map['dimension%s' % index] = _payload[0]
                custom_values[_payload[0]] = _payload[1]
            create_args['custom_map'] = custom_map
            jsons_custom_values = custom_dumps(custom_values)
        
        # set the main account_id config
        if not create_args:
            script.append("""gtag('config','%s');""" % account_id)
            for (idx, alt_account_id) in enumerate(self.data_struct['*additional_accounts']):
                script.append("""gtag('config','%s');""" % alt_account_id)  # ,{'groups':'core'}
        else:
            jsons_create_args = custom_dumps(create_args)
            script.append("""gtag('config','%s',%s);""" % (account_id, jsons_create_args))
            for (idx, alt_account_id) in enumerate(self.data_struct['*additional_accounts']):
                script.append("""gtag('config','%s',%s);""" % (alt_account_id, jsons_create_args))  # ,{'groups':'core'}

        # if we have custom_variables, they're done via a config update + event
        if jsons_custom_values:
            # this works for to all?
            script.append("""gtag('event','pageview',%s);""" % jsons_custom_values)

        # ecommerce
        if self.data_struct['*transaction']:
            for transaction_id in self.data_struct['*transaction'].keys():
                # _addTrans(transactionId, affiliation, total, tax, shipping, city, state, country)
                transaction_dict = self.data_struct['*transaction'][transaction_id]
                # required field
                cleaned_dict__transaction = {'transaction_id': str(transaction_id), }

                # unchanged fields:
                fields_unchanged = ['affiliation', 'shipping', 'tax', 'coupon', 'currency', ]
                for i in fields_unchanged:  # fix optionals before positioning
                    if i in transaction_dict:
                        v = transaction_dict[i]
                        cleaned_dict__transaction[i] = str(v) if v is not None else None

                # fields can be remapped
                # eg analytics.js is "revenue"|  gtag.js is "value"
                fields_remappable = remappable_action_fields('*transaction', transaction_dict, AnalyticsMode.GTAG)
                for (_dkey, _skey) in fields_remappable:
                    if _skey in transaction_dict:
                        v = transaction_dict[_skey]
                        cleaned_dict__transaction[_dkey] = str(v) if v is not None else None

                # now we do items
                items = []
                if transaction_id in self.data_struct['*transaction_items']:
                    for item_dict in self.data_struct['*transaction_items'][transaction_id]:
                        cleaned_dict__item = {}
                        fields_unchanged = ['category', 'price', 'quantity', ]
                        fields_new = ['brand', 'creative_name', 'creative_slot', 'location_id', ]
                        _fields = fields_unchanged + fields_new

                        for i in _fields:  # fix optionals before positioning
                            if i in item_dict:
                                v = item_dict[i]
                                cleaned_dict__item[i] = str(v) if v is not None else None

                        fields_remappable = remappable_action_fields('*transaction_items', item_dict, AnalyticsMode.GTAG)
                        for (_dkey, _skey) in fields_remappable:
                            if _skey in item_dict:
                                v = item_dict[_skey]
                                cleaned_dict__item[_dkey] = str(v) if v is not None else None
                        items.append(cleaned_dict__item)
                cleaned_dict__transaction['items'] = items

                _formatted = u"""gtag('event', 'purchase', %s""" % custom_dumps(cleaned_dict__transaction)
                script.append(_formatted)

        # track_pageview is automatic and part of the config

        # events
        # ga('send', 'event', 'category', 'action', 'opt_label', opt_value, {'nonInteraction': 1});
        _events = []
        _event_fields_optional_fieldobject = (('*category', 'event_category'),
                                              ('*label', 'event_label'),
                                              ('*value', 'value'),
                                              ('*non_interaction', 'non_interaction'),  # TODO: is this legit?
                                              )
        for _event_dict in self.data_struct['*tracked_events']:
            # all events require an action
            _event_action = _event_dict.get('*action')
            try:
                if not _event_action:
                    raise InvalidTag()
            except:
                _events.append(INVALID_TAG)
                continue
                    
            _event_fieldobject = {}
            # figure out the fieldobject args if any.
            for (_field_src, _field_dest) in _event_fields_optional_fieldobject:
                # set the value to a default of `None`
                # don't set it to `undefined` yet.
                # we need the `None` for tests...
                _value = _event_dict.get(_field_src, None)
                if _value is not None:
                    _event_fieldobject[_field_dest] = _value

            if _event_fieldobject:
                _formatted = u"""gtag('event','%s',%s""" % (_event_action, custom_dumps(_event_fieldobject))
                _events.append(_formatted)
            else:
                _formatted = u"""gtag('event','%s');""" % _event_action
                _events.append(_formatted)

        if _events:
            for _event in _events:
                if _event is INVALID_TAG:
                    script.append("/* gtag('event': incompatible event */")
                else:
                    script.append(_event)
            

        script.append(u"""</script>""")
        if self.use_comments:
            script.append('<!-- End Google Analytics -->')
        return u"""\n""".join(script)

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
        elif mode == AnalyticsMode.GTAG:
            return self._render__gtag()

        return '<!-- unsupported AnalyticsMode -->'


# ==============================================================================


__all__ = ('AnalyticsWriter',
           'AnalyticsMode',
           )
