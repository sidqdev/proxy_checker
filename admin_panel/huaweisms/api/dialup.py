from . import common


XML_TEMPLATE = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<request>"
    "<dataswitch>{enable}</dataswitch>"
    "</request>"
)


XML_TEMPLATE_MODE = '''
<?xml version="1.0" encoding="UTF-8"?>
<request>
<NetworkMode>0{NetworkMode}</NetworkMode>
<NetworkBand>{NetworkBand}</NetworkBand>
<LTEBand>{LTEBand}</LTEBand>
</request>
'''


def connect_mobile(ctx):
    # type: (common.ApiCtx) -> ...
    return switch_mobile_on(ctx)


def disconnect_mobile(ctx):
    # type: (common.ApiCtx) -> ...
    return switch_mobile_off(ctx)


def get_mobile_status(ctx):
    # type: (common.ApiCtx) -> ...
    url = "{}/dialup/mobile-dataswitch".format(ctx.api_base_url)
    result = common.get_from_url(url, ctx)
    if result and result.get("type") == "response":
        response = result["response"]
        if response and response.get("dataswitch") == "1":
            return "CONNECTED"
        if response and response.get("dataswitch") == "0":
            return "DISCONNECTED"
    return "UNKNOWN"


def switch_mobile_off(ctx):
    # type: (common.ApiCtx) -> ...
    data = XML_TEMPLATE.format(enable=0)
    headers = {
        "__RequestVerificationToken": ctx.token,
    }
    url = "{}/dialup/mobile-dataswitch".format(ctx.api_base_url)
    return common.post_to_url(url, data, ctx, additional_headers=headers)


def switch_mobile_on(ctx):
    # type: (common.ApiCtx) -> ...
    data = XML_TEMPLATE.format(enable=1)
    headers = {
        "__RequestVerificationToken": ctx.token,
    }
    url = "{}/dialup/mobile-dataswitch".format(ctx.api_base_url)
    return common.post_to_url(url, data, ctx, additional_headers=headers)


def switch_network_mode(ctx, mode):
    NetworkBand = ""
    LTEBand = ""
    headers = {
        "__RequestVerificationToken": ctx.token,
    }

    url = "{}/net/net-mode".format(ctx.api_base_url)
    resp = common.get_from_url(url, data, ctx, additional_headers=headers)
    NetworkBand = resp['response']['NetworkBand']
    LTEBand = resp['response']['LTEBand']
    
    url = "{}/net/net-mode".format(ctx.api_base_url)

    data = XML_TEMPLATE_MODE.format(NetworkMode=mode, NetworkBand=NetworkBand, LTEBand=LTEBand)
    return common.post_to_url(url, data, ctx, additional_headers=headers)