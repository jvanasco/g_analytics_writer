from . import GaqHub
from pylons import c 

def gaq_setup( account_id , single_push=False ):
    c._gaq= GaqHub( account_id , single_push=single_push )
    return c.gaq

def gaq_setAccount(account_id):
    c._gaq.setAccount( account_id )

def gaq_setSinglePush(bool_value):
    c._gaq.setSinglePush( bool_value )

def gaq_trackEvent(track_dict):
    c._gaq.trackEvent(track_dict)
    
def gaq_setCustomVar(index,name,value,opt_scope=None):
    c._gaq.setCustomVar(index,name,value,opt_scope=opt_scope)

def gaq_setDomainName(domain_name):
    c._gaq.setDomainName(domain_name)

def gaq_setAllowLinker(bool_allow):
    c._gaq.setAllowLinker(bool_allow)

def gaq_addTrans(track_dict):
    c._gaq.addTrans(track_dict)
    
def gaq_addItem(track_dict):
    c._gaq.addItem(track_dict)

def gaq_trackTrans():
    c._gaq.trackTrans()
    
def gaq_as_html():
    c._gaq.as_html()
