0.3.1
	2019.04.26
	* undid some aggressive 2to3 translations

0.3.0
	2019.04.25
	* official Python3 support. it worked before, but was not officially supported.
	* renamed `custom_json_dumps` to `json_dumps`
	* added `json_dumps_callable` to `AnalyticsWriter.__init__`
	* removed monkeypatching of json dumper in test, specify into writer
	* migrating charset to the front of the payload, per RFC

0.2.1
	2018.10.08
	* initial (limited) support for AMP format
	* added some classes as attibutes of `AnalyticsWriter`

0.2.0

	2018.07.26
	* initial release

0.2.0a
	* initial commit
	* renamed `g_analytics_writer`, was `gaq_hub`
	* the package now handles an internal format for tracking the data, and writes
	  in one of multiple google analytics formats
	* now supports
	 * ga.js
	 * analytics.js (new!)
	 * gtag.js (new!)
	* dropped pylons support
