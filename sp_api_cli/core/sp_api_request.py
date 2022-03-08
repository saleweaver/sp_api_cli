from datetime import datetime

from sp_api.base import Client, Marketplaces


def request(marketplace, account, **kwargs):
    body = kwargs
    print(marketplace, account)
    body.update({'LastUpdatedAfter': datetime.utcnow().isoformat()})
    r = Client(Marketplaces[marketplace], account=account)._request(
        body.pop('path'),
        data=None if body['method'].upper() in ('GET',) else body,
        params=None if body['method'].upper() not in ('GET',) else body,
        add_marketplace=True
    )

    return r

