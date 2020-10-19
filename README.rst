g_analytics_writer
==================

Build Status: ![Python package](https://github.com/jvanasco/g_analytics_writer/workflows/Python%20package/badge.svg)


`g_analytics_writer` gives lightweight support for writing optimized "Google Analytics" tracking code for those times when you need to use The Great Satan, even though you would prefer not to.

Python2.7 and Python3.5+ are supported

It offers a `AnalyticsWriter` object, which provides a standard API to authoring multiple "Google Analytics" tracking formats:

* `ga.js` (historical legacy)
* `analytics.js` (current/deprecated)
* `gtag.js` (current/future)
* `amp` (accelerated mobile pages plugin)

It also offers helper packages for the `Pyramid` framework, which can automate managing `AnalyticsWriter` objects

The package is designed to work with MVC/MVT/MCT/etc systems:

* Python should populate all the tracking data, then render everything at once.
* Applications should invoke this library with 'what I want to do', and this library will figure out how best to do it.

This is not designed to iteratively generate a tagging, but instead to generate everything at once, as optimized as possible. 

This package strives to create as few calls to the google servers as possible.

`AnalyticsWriter` objects simply contain various bits of data in an internal format, and then prints them out in the correct order via a helper functions for each format.

The goal of this project is to simplify migration across versions. You tell this package what you want to track and how, it will figure out how to do that in "Google Analytics"!

If you're just using simple track pageviews, this package is likely overkill

but if you're using any of this functionality, then its for you:

* custom variables for performance analytics
* event tracking for backend interaction / operations
* ecommerce tracking
* rolling up multiple domains into 1 reporting suite

This package lets you set Google code wherever needed, and renders everything in the 'correct' order.

Every command has extensive docstrings, which also include, credit, and link to the relevant sections of the official GoogleAnalytics API docs.

Supported Concepts & Commands
=============================

* Core
* SetAccount and reporting into multiple domains
* Multiple Domain Tracking
* Custom Variables
* eCommerce
* Event Tracking
* Session Unification/userId (`analytics.js` only)
* AMP client_id integration


what's the difference between all these tracking versions?
==========================================================

There are a few big differences:

custom variables
----------------

1. The legacy `ga.js` did not require pre-configuring the admin(online) dashboard with custom dimensions. everything was configured on the tag, from the 'name' to the 'scope'.  sending data to their servers was in the form of: `_gaq.push(['_setCustomVar',1,'pagetype','account']);`.
2. The `analytics.js` version requires the dashboard to be pre-configured with custom dimensions. Note the form of  `ga('send','pageview',{"dimension1":"account"})` does not include the `pagetype` label, only the value `account`.
3. The `gat.js` version requires the dashboard to be pre-configured with custom dimensions and also requires a `custom_map`. Note the form of  `gtag('set',{"section":"account","pagetype":"home","is_known_user":"1"}); gtag('config','UA-12345678987654321-12',{"custom_map":{"dimension1":"section","dimension2":"pagetype","dimension5":"is_known_user"}});` sets the `pagetype` label,however that is not transmitted to their server - it is only used locally for translation.
4. AMP uses the `gat.js` concepts

order of execution and automatic pageviews
------------------------------------------

1. `ga.js` requires a manual `_trackPageview`, so it is easy to populate the pageview with custom variables.
2. `analytics.js` requires a manual `'send','pageview'`, so it is easy to populate the pageview with custom variables.
3. `gtag.js` automates `'send','pageview'`. in order to populate the pageview with custom variables, we must either pre-populate the tracker with global variables OR disable the initial pageview and send a `pageview` "event" to their servers.


and more
--------

transactions and events are all slightly different across versions


History
=======

this package replaces the following packages,

* `gaq_hub`
    * https://github.com/jvanasco/gaq_hub
    * `gaq_hub` supported `ga.js`
    * tags in this repository UNDER 0.2 are the old `gaq_hub` codebase
    * `gaq_hub`, replaced
        * pyramid_gaq - https://github.com/jvanasco/pyramid_gaq
        * pylons_gaq  - https://github.com/jvanasco/pylons_gaq | pylons support was ended in the 0.2.0 release


AVAILABLE MODES
===============

The available modes are:

.. code-block:: python

    AnalyticsMode.GA_JS = "legacy `ga.js`"
    AnalyticsMode.ANALYTICS = "current/deprecated `analytics.js`"
    AnalyticsMode.GTAG = "current/future `gtag.js`"
    AnalyticsMode.AMP = "AMP plugin support, is a variant of `gtag.js`"

The default is currently `AnalyticsMode.ANALYTICS`, which has the smallest amount of network traffic.

`AnalyticsMode.GTAG` has slightly larger network traffic, because the `gtag.js` file actually loads and interacts with the `analytics.js` file.


QuickStart - General
====================

Create a new AnalyticsWriter object and do stuff with it:

.. code-block:: python

    from g_analytics_writer import AnalyticsWriter

    writer = AnalyticsWriter('GA_ACCOUNT_ID')
    writer.setCustomVar(1, 'TemplateVersion', 'A', 3)
    print writer.render()

that's really about it


QuickStart - Pyramid
====================

The `Pyramid` helpers simply manage a `AnalyticsWriter` object in the request.gaq namespace

environment.ini - required

.. code-block:: python

	g_analytics_writer.account_id = UA-123412341234-1234

environment.ini - optional
    
.. code-block:: python

	g_analytics_writer.mode = <INT references AnalyticsMode>
	g_analytics_writer.use_comments = <BOOLEAN>
	g_analytics_writer.single_push = <BOOLEAN only for ga.js>
	g_analytics_writer.force_ssl = <BOOLEAN>
	g_analytics_writer.global_custom_data = <BOOLEAN>
	g_analytics_writer.gtag_dimensions_strategy = <BOOLEAN>
	g_analytics_writer.amp_clientid_integration = <BOOLEAN>

This way you can have different reporting environments.

For example, `dev.ini` may define a secondary account

.. code-block:: python

	g_analytics_writer.account_id_ = U-123449-2

wile `production.ini` defines your primary account

.. code-block:: python

	g_analytics_writer.account_id_ = U-123449-1


You simply include the package in your `__init__.py`

.. code-block:: python

	def main(global_config, **settings):
		...
		# custom gaq
		config.include("g_analytics_writer.pyramid_integration")


When you want to set a custom variable , or anything similar...
---------------------------------------------------------------

.. code-block:: python

    request.analytics_writer.setCustomVar(1, 'TemplateVersion', 'A', 3)


Rendering Optimized Variables
-----------------------------

For `analytics.js` the recommended configuration option is:

.. code-block:: python

    `global_custom_data=True`

This will issue a global `set` for all trackers before the `pageview`

.. code-block:: javascript

    ga('create','UA-123123-1','auto');
    ga('set',{"dimension9":"jonathan"});
    ga('send','pageview');

For `gtag.js` the recommended configuration option is:

.. code-block:: python

    `global_custom_data=True`

This will issue a global `set` *BEFORE* issuing the config, which will automatically trigger pageviews

.. code-block:: javascript

    gtag('set',{"name":"jonathan"});
    gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"}});

Toggling configurations can generate this:

.. code-block:: javascript

    gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"},"send_page_view":false});
    gtag('set',{"name":"jonathan"});
    gtag('event','pageview');

To print this out...
--------------------

In my mako templates, I just have this...

.. code-block:: html

    <head>
    ...
    ${request.g_analytics_writer.render()|n}
    ...
    </head>

Notice that you have to escape under Mako.   For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html


Licensing
---------

This package is made available via the MIT License -- http://www.opensource.org/licenses/mit-license

Content in the docstrings marked "Google Documentation" is copyright by Google and appears under their Creative Commons Attribution 3.0 License
