from . import GaqHub
from pyramid.threadlocal import get_current_request


def includeme(config):
    """the pyramid includeme command
    including this will automatically setup the GaqHub object for every request
    """
    config.add_request_method(
        'gaq_hub.pyramid_helpers.new_GaqHub',
        'gaq',
        reify=True,
    )


def new_GaqHub(request):
    """simply creates a new hub"""
    account_id = request.registry.settings['gaq.account_id']
    return GaqHub(account_id, single_push=False)


# ==============================================================================
#   WARNING
#
#   Everything below is pretty much deprecated.  use the includeme instead and request methods
#
# ==============================================================================


def gaq_setup(account_id, single_push=False, request=None):
    request = request or get_current_request()
    request._gaq = GaqHub(account_id, single_push=single_push)
    return request._gaq


def gaq_setAccount(account_id, request=None):
    request = request or get_current_request()
    request._gaq.setAccount(account_id)


def gaq_setSinglePush(bool_value, request=None):
    request = request or get_current_request()
    request._gaq.setSinglePush(bool_value)


def gaq_trackEvent(track_dict, request=None):
    request = request or get_current_request()
    request._gaq.trackEvent(track_dict)


def gaq_setCustomVar(index, name, value, opt_scope=None, request=None):
    request = request or get_current_request()
    request._gaq.setCustomVar(index, name, value, opt_scope=opt_scope)


def gaq_setDomainName(domain_name, request=None):
    request = request or get_current_request()
    request._gaq.setDomainName(domain_name)


def gaq_setAllowLinker(bool_allow, request=None):
    request = request or get_current_request()
    request._gaq.setAllowLinker(bool_allow)


def gaq_addTrans(track_dict, request=None):
    request = request or get_current_request()
    request._gaq.addTrans(track_dict)


def gaq_addItem(track_dict, request=None):
    request = request or get_current_request()
    request._gaq.addItem(track_dict)


def gaq_trackTrans(request=None):
    request = request or get_current_request()
    request._gaq.trackTrans()


def gaq_as_html(request=None):
    request = request or get_current_request()
    return request._gaq.as_html()
