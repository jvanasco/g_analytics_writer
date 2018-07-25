g_analytics_writer gives lightweight support for writing optimized Google Analytics

It offers a AnalyticsWriter object, which provides a standard API to authoring multiple Google Analytics tracking formats:

* ga.js (historical legacy)
* analytics.js (current/deprecated)
* gtag.js (current/future)

It also offers helper packages for the pyramid framework, which can automate managing AnalyticsWriter objects

The package is designed to work with MVC/MVT/MCT/etc systems:

* Python should populate all the tracking data, then render everything at once.
* Applications should invoke this library with 'what I want to do', and this library will figure out how best to do it.

This is not designed to iteratively generate a tagging, but instead to generate everything at once, as optimized as possible. 

This package strives to create as few calls to the google servers as possible.

AnalyticsWriter objects simply contain various bits of data in an internal format, and then prints them out in the correct order via a helper functions for each format.

The goal of this project is to simplify migration across versions. You tell this package what you want to track and how, it will figure out how to do that in Google Analytics!

If you're just using simple track pageviews, this package is likely overkill

but if you're using any of this functionality, then its for you:

- custom variables for performance analytics
- event tracking for backend interaction / operations
- ecommerce tracking
- rolling up multiple domains into 1 reporting suite

This package lets you set Goog code wherever needed, and renders everything in the 'correct' order.

Every command has extensive docstrings, which also include, credit, and link to the relevant sections of the official GoogleAnalytics API docs.

# Supported Concepts & Commands

* Core
* SetAccount and reporting into multiple domains
* Multiple Domain Tracking
* Custom Variables
* eCommerce
* Event Tracking
* Session Unification/userId (ga.js only)

# History

this pacakge replaces the following packages,

* gaq_hub
** https://github.com/jvanasco/gaq_hub
** gaq_hub supported ga.js
** tags in this repository UNDER 0.2 are the old gaq_hub codebase
** gaq_hub, replaced
*** pyramid_gaq - https://github.com/jvanasco/pyramid_gaq
*** pylons_gaq  - https://github.com/jvanasco/pylons_gaq | pylons support was ended in the 0.2.0 release


# QuickStart

## create a new AnalyticsWriter object and do stuff with it

    from g_analytics_writer import AnalyticsWriter

    writer = AnalyticsWriter('GA_ACCOUNT_ID')
    writer.setCustomVar(1, 'TemplateVersion', 'A', 3)
    print writer.render()

that's really about it


# QuickStart - Pyramid

the pyramid helpers simply manage a AnalyticsWriter object in the request.gaq namespace

	environment.ini

		g_analytics_writer.account_id= UA-123412341234-1234


	this way you can have different reporting environments...

		dev.ini
			g_analytics_writer.account_id_ = U-123449-2

		production.ini
			g_analytics_writer.account_id_ = U-123449-1


	__init__.py:

		def main(global_config, **settings):
			...
			# custom gaq
			config.include("g_analytics_writer.pyramid_integration")


## When you want to set a custom variable , or anything similar...

    request.analytics_writer.setCustomVar(1, 'TemplateVersion', 'A', 3)


## Rendering Optimized Variables

For `analytics.js` the recommended configuration option is:

	`global_custom_data=True`

This will issue a global `set` for all trackers before the `pageview`

	ga('create','UA-123123-1','auto');
	ga('set',{"dimension9":"jonathan"});
	ga('send','pageview');

For `gtag.js` the recommended configuration option is:

	`default`

This will issue a global `set` *BEFORE* issuing the config, which will automatically trigger pageviews

	gtag('set',{"name":"jonathan"});
	gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"}});

Toggling configurations can generate this:

	gtag('config','UA-123123-1',{"custom_map":{"dimension9":"name"},"send_page_view":false});
	gtag('set',{"name":"jonathan"});
	gtag('event','pageview');

## To print this out..

In my mako templates, I just have this...

    <head>
    ...
    ${request.g_analytics_writer.as_html()|n}
    ...
    </head>

Notice that you have to escape under Mako.   For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html
