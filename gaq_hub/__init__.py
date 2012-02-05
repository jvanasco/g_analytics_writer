import types

class GaqHub(object):
    data_struct= None

    def __init__(self , account_id , single_push=False ):
        """Sets up self.data_struct dict which we use for storage.
        
            You'd probably have something like this in your base controller:
            
            class Handler(object):
                def __init__(self,request):
                    self.request = request
                    h.gaq_setup(self.request,'AccountId')
                    
            All of the other commands in the module accept an optional 'request' kwarg. 
            
            If no 'request' is submitted, it will call pyramid.threadlocal.get_current_request()
            
            This should allow you to easily and cleanly call this within templates, and not just handler methods.
    
        """
        self.data_struct= {
            '__singlePush' : single_push,
    
            '_setAccount' : account_id,
    
            '_setCustomVar' : [],
    
            '_setDomainName': False,
            '_setAllowLinker': False,
    
            '_addTrans' : [],
            '_addItem' : [],
            '_trackTrans' : False,
    
            '_trackEvent' :[],

        }
    
    
        

    def setAccount(self,account_id):
        """This should really never be called, best to setup during __init__, where it is required"""
        self.data_struct['_setAccount']= account_id



    def setSinglePush(self,bool_value):
        """GA supports a single 'push' event.  """
        self.data_struct['__singlePush']= bool_value
    
    
    
    def trackEvent(self,track_dict):
        """'Constructs and sends the event tracking call to the Google Analytics Tracking Code. Use this to track visitor behavior on your website that is not related to a web page visit, such as interaction with a Flash video movie control or any user event that does not trigger a page request. For more information on Event Tracking, see the Event Tracking Guide.
        
        You can use any of the following optional parameters: opt_label, opt_value or opt_noninteraction. If you want to provide a value only for the second or 3rd optional parameter, you need to pass in undefined for the preceding optional parameter.'
    
        -- from http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEventTracking.html#_gat.GA_EventTracker_._trackEvent
        """
        clean= []
        for i in ['category','actions','opt_label','opt_value','opt_noninteraction'] :
            if i in track_dict :
                clean.append( "'%s'" % track_dict[i] )
            else:
                clean.append( 'undefined' )
        self.data_struct['_trackEvent'].append( """['_trackEvent',%s]""" % ','.join(clean) )
        
        
    
    def setCustomVar(self,index,name,value,opt_scope=None):
        """_setCustomVar(index, name, value, opt_scope)
        'Sets a custom variable with the supplied name, value, and scope for the variable. There is a 64-byte character limit for the name and value combined.'
    
        -- from http://code.google.com/apis/analytics/docs/gaJS/gaJSApiBasicConfiguration.html#_gat.GA_Tracker_._setCustomVar
        """
        if opt_scope :
            self.data_struct['_setCustomVar'].append( "['_setCustomVar',%s,'%s','%s',%s]" % (index,name,value,opt_scope) )
        else:
            self.data_struct['_setCustomVar'].append( "['_setCustomVar',%s,'%s','%s']" % (index,name,value) )
    
    
    
    def setDomainName(self,domain_name):
        """_setDomainName(newDomainName)
    
        -- from http://code.google.com/apis/analytics/docs/gaJS/gaJSApiDomainDirectory.html#_gat.GA_Tracker_._setDomainName
        """
        self.data_struct['_setDomainName']= domain_name
    
    
    
    def setAllowLinker(self,bool_allow):
        """_setAllowLinker(bool)
        http://code.google.com/apis/analytics/docs/gaJS/gaJSApiDomainDirectory.html#_gat.GA_Tracker_._setAllowLinker
        """
        self.data_struct['_setAllowLinker']= bool_allow
    
    
    def addTrans(self,track_dict):
        """'Creates a transaction object with the given values. As with _addItem(), this method handles only transaction tracking and provides no additional ecommerce functionality. Therefore, if the transaction is a duplicate of an existing transaction for that session, the old transaction values are over-written with the new transaction values. Arguments for this method are matched by position, so be sure to supply all parameters, even if some of them have an empty value.'
    
        -- from http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEcommerce.html#_gat.GA_Tracker_._addTrans
        """
        for i in ['order_id','total'] : # fix required ; let javascript show errors if null
            if i not in track_dict:
                track_dict[i] = ''
        for i in ['opt_affiliation','opt_tax','opt_shipping','opt_city','opt_state','opt_country'] : # fix optionals for positioning
            if i not in track_dict:
                track_dict[i] = ''
        self.data_struct['_addTrans'].append( """['_addTrans',%(order_id)s,'%(opt_affiliation)s','%(total)s','%(opt_tax)s','%(opt_shipping)s','%(opt_city)s','%(opt_state)s','%(opt_country)s']""" % track_dict)
        
    
    
    def addItem(self,track_dict):
        """'Use this method to track items purchased by visitors to your ecommerce site. This method tracks individual items by their SKU. This means that the sku parameter is required. This method then associates the item to the parent transaction object via the orderId argument'
        
        --from http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEcommerce.html#_gat.GA_Tracker_._addItem
        """
        for i in ['order_id','sku','name','price','quantity'] : # fix required ; let javascript show errors if null
            if i not in track_dict:
                track_dict[i] = ''
        for i in ['category'] : # fix optionals for positioning
            if i not in track_dict:
                track_dict[i] = ''
        self.data_struct['_addItem'].append( """['_addItem',%(order_id)s,'%(sku)s','%(name)s','%(category)s','%(price)s','%(quantity)s']""" % track_dict)
    
    
    
    def trackTrans(self):
        """gaq_trackTrans(request=None)- You merely have to call this to enable it. I decided to require this, instead of automatically calling it if a transaction exists, because this must be explicitly called in the ga.js API and its safer to reinforce this behavior.
        
        'Sends both the transaction and item data to the Google Analytics server. This method should be called after _trackPageview(), and used in conjunction with the _addItem() and addTrans() methods. It should be called after items and transaction elements have been set up.'
        
        --from http://code.google.com/apis/analytics/docs/gaJS/gaJSApiEcommerce.html#_gat.GA_Tracker_._trackTrans
        """
        self.data_struct['_trackTrans']= True


        
    def as_html(self):
        """helper function. prints out GA code for you, in the right order.
    
        You'd probably call it like this in a Mako template: 
            <head>
                ${h.as_html()|n}
            </head>
        
        Notice that you have to escape under Mako.   For more information on mako escape options - http://www.makotemplates.org/docs/filtering.html
        """
        single_push = self.data_struct['__singlePush']
        single_pushes= []
    
        script= [\
                    '<script type="text/javascript">',
                    'var _gaq = _gaq || [];',
                ]
        
        # start the single push if we elected
        if single_push:
            script.append( """_gaq.push(""" )
    
        # according to GA docs, the order to submit via javascript is:
        ## _setAccount
        ## _setDomainName
        ## _setAllowLinker
        ##
        ## cross domain tracking reference
        ## http://code.google.com/apis/analytics/docs/tracking/gaTrackingSite.html
    
        # _setAccount
        if single_push:
            single_pushes.append( """['_setAccount', '%s']""" % self.data_struct['_setAccount'] )
        else: 
            script.append( """_gaq.push(['_setAccount', '%s']);""" % self.data_struct['_setAccount'] )
            
        # _setDomainName
        if self.data_struct['_setDomainName']:
            if single_push:
                single_pushes.append( """['_setDomainName', '%s']""" % self.data_struct['_setDomainName'] )
            else: 
                script.append( """_gaq.push(['_setDomainName', '%s']);""" % self.data_struct['_setDomainName'] )
    
        # _setAllowLinker
        if self.data_struct['_setAllowLinker']:
            if single_push:
                single_pushes.append( """['_setAllowLinker', %s]""" % ( "%s" % self.data_struct['_setAllowLinker'] ).lower() )
            else: 
                script.append( """_gaq.push(['_setAllowLinker', %s]);""" % ( "%s" % self.data_struct['_setAllowLinker'] ).lower() )
    
        # _setCustomVar is next 
        # this is done in an array, because there might be some other commands that could fit in here
        for category in ['_setCustomVar']:
            for i in self.data_struct[category]:
                if single_push:
                    single_pushes.append(i)
                else:
                    script.append("""_gaq.push(%s);""" % i )
    
        if single_push:
            single_pushes.append("""['_trackPageview']""" )
        else:
            script.append("""_gaq.push(['_trackPageview']);""" )
    
        # according to GA docs, the order to submit via javascript is:
        ## _trackPageview
        ## _addTrans
        ## _addItem
        ## _trackTrans
        for category in ['_addTrans','_addItem']:
            for i in self.data_struct[category]:
                if single_push:
                    single_pushes.append(i)
                else:
                    script.append("""_gaq.push(%s);""" % i )
    
        if self.data_struct['_trackTrans'] :
            if single_push:
                single_pushes.append("""['_trackTrans']""" )
            else:
                script.append("""_gaq.push(['_trackTrans']);""" )
        
        # events seem to be on their own.
        for category in [ '_trackEvent']:
            for i in self.data_struct[category]:
                if single_push:
                    single_pushes.append(i)
                else:
                    script.append("""_gaq.push(%s);""" % i )
    
        # close the single push if we elected
        if single_push:
            script.append( ",\n".join(single_pushes) )
            script.append( """);""" )
    
        script.append( """(function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })(); """)
        script.append("</script>")
    
        return "\n".join(script)
