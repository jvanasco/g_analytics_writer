google_analytics_writer gives lightweight support for Google Analytics

It offers a AnalyticsWriter object, which offers a standard API to multiple Google Analytics tracking formats:

* ga.js (historical format)
* analytics.js (historical format)
* gtag.js (current)
	
It also offers helper packages for the pyramid framework, which can automate managing AnalyticsWriter objects

AnalyticsWriter objects simply contain various bits of data in an internal format, and then prints them out in the correct order via a helper functions for each format.

The goal of this project is to 


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
** Choice of using a single , queued, "push" style command - or repeated ga.js API calls
** _setAccount
* Multiple Domain Tracking
** _setDomainName
** _setAllowLinker
* Custom Variables
* _setCustomVar
* eCommerce
** _addTrans
** _addItem
** _trackTrans
* Event Tracking
* _trackEvent

# History

this pacakge replaces the following two packages,

    * gaq_hub - https://github.com/jvanasco/gaq_hub
    which replaced
		* pyramid_gaq - https://github.com/jvanasco/pyramid_gaq
		* pylons_gaq  - https://github.com/jvanasco/pylons_gaq | pylons support was ended in the 0.2.0 release


# QuickStart

## create a new GaqHub object and do stuff with it

    from gaq_hub import GaqHub

    gaq= GaqHub( 'GA_ACCOUNT_ID' )
    gaq.setCustomVar(1,'TemplateVersion','A',3)
    print gaq.as_html()

that's really about it


# QuickStart - Pyramid

the pyramid helpers simply manage a GaqHub object in the request.gaq namespace

	environment.ini

		gaq.account_id= UA-123412341234-1234


	this way you can have different reporting environments...

		dev.ini
			gaq.account = U-123449-2

		production.ini
			gaq.account = U-123449-1


	__init__.py:

		def main(global_config, **settings):
			...
			# custom gaq
			config.include("gaq_hub.pyramid_helpers")


## When you want to set a custom variable , or anything similar...

    request.gaq.setCustomVar(1, 'TemplateVersion', 'A', 3)


## To print this out..

In my mako templates, I just have this...

    <head>
    ...
    ${request.gaq.as_html()|n}
    ...
    </head>

Notice that you have to escape under Mako.   For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html
