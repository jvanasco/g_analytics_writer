0.2
* initial commit
* renamed `g_analytics_writer`, was `gaq_hub`
* the package now handles an internal format for tracking the data, and writes
  in one of multiple google analytics formats
* now supports
 * ga.js
 * analytics.js (new!)
 * gtag.js (new!)
* dropped pylons support
