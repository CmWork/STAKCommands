"""Virtual Deployment Service STAK library"""


def check(param, param_name, msg):
    """returns string"""
    if type(param) == 'string':
        if len(param) == 0:
            msg = msg + ' ' + param_name
    return msg

def make_credentials(Provider, ProviderServer, ProviderUser,
                     ProviderPassword, ProviderTenant):
    """returns dict"""
    credentials = {}
    credentials['provider'] = Provider
    credentials['provider_server'] = ProviderServer
    credentials['provider_user'] = ProviderUser
    credentials['provider_password'] = ProviderPassword
    credentials['provider_tenant'] = ProviderTenant
    return credentials

