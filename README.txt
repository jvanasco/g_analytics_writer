gaq_hub gives lightweight support for Google Analytics

it offers a GaqHub object, which can be modifed in many fun and exicting ways

it also offers helper packages for popular python frameworks, pylons and pyramid, which can automate managing GaqHub objects

GaqHub objects simply contain various bits of data, and then print them out in the correct order via a helper function.

For Pylons:
    creates and manages an _gaq namespace under pylons.c
    
For Pyramid:
    creates and manages an _gaq namespace under a request instance.  if no request instance is passed via a kward, get_current_request() is called

if you're just using `_trackPageview` from gaq, this package is likely overkill 

but if you're using any of this functionality, then its for you:
- custom variables for performance analytics 
- event tracking for backend interaction / operations 
- ecommerce tracking 
- rolling up multiple domains into 1 reporting suite

This package lets you set GA code wherever needed, and renders everything in the 'correct' order.

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
    pylons_gaq  - https://github.com/jvanasco/pylons_gaq
    pyramid_gaq - https://github.com/jvanasco/pyramid_gaq


# QuickStart 

## create a new GaqHub object and do stuff with it

    from gaq_hub import GaqHub
    
    gaq= GaqHub( 'GA_ACCOUNT_ID' )
    gaq.setCustomVar(1,'TemplateVersion','A',3)
    print gaq.as_html()

that's really about it


# QuickStart - Pyramid

the pyramid helpers simply manage a GaqHub object in the request._gaq namespace , and uses a call to get_current_request if no kwarg for 'request' is provided :

    def gaq_setup( account_id , single_push=False , request=None ):
        if request is None:
           request= get_current_request()
        request._gaq= GaqHub( account_id , single_push=single_push )

## import this into your helpers

Dropping it into your helpers namespace makes it easier to use in templates like mako.

lib/helpers.py

    from gaq_hub.pyramid_helpers import *
    
## configure your BaseController to call gaq_setup on __init__

This example is from my "pylons style hander".

There are only two vars to submit:

1. Your Google Analytics Account ID
2. Whether or not your want to use the "Single Push" method, or a bunch of separate events.

handlers/base.py

    class Handler(object):
        def __init__(self, request):
        self.request = request
        h.gaq_setup('GA_ACCOUNT_ID',single_push=False, request=self.request )


if you want to get all fancy...
        h.gaq_setup( request.registry.settings['gaq.account'] , request=self.request )

this way you can have different reporting environments...

    dev.ini
        gaq.account = U-123449-2
    
    production.ini
        gaq.account = U-123449-1



        


## When you want to set a custom variable , or anything similar...

    h.gaq_setCustomVar(1,'TemplateVersion','A',3)

    
## To print this out..

In my mako templates, I just have this...

    <head>
    ...
    ${h.gaq_print()|n}
    ...
    </head>

Notice that you have to escape under Mako.   For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html


# QuickStart Pylons

## import this into your helpers

Dropping it into your helpers namespace makes it easier to use in templates like mako.

lib/helpers.py

    from gaq_hub.pylons_helpers import *
    

## configure your BaseController to call gaq_setup on __init__

This example is from my "pylons style hander".

There are only two vars to submit:

1. Your Google Analytics Account ID
2. Whether or not your want to use the "Single Push" method, or a bunch of separate events.

handlers/base.py

    class Handler(object):
        def __init__(self, request):
        self.request = request
        h.gaq_setup(request,'GA_ACCOUNT_ID',single_push=False)


## When you want to set a custom variable , or anything similar...

    h.gaq_setCustomVar(1,'TemplateVersion','A',3)

    
## To print this out..

In my mako templates, I just have this...

    <head>
    ...
    ${h.gaq_print()|n}
    ...
    </head>

Notice that you have to escape under Mako.   For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html