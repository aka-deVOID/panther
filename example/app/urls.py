from app.apis import *

from panther.app import API
from panther.response import Response


@API()
async def test(*args, **kwargs):
    return Response(data={'detail': 'this is for test'})

urls = {
    'none-class/': ReturnNone,
    'none/': return_none,
    'dict/': return_dict,
    'list/': return_list,
    'tuple/': return_tuple,
    'res-dict/': return_response_dict,
    'res-none': return_response_none,
    'res-list/': return_response_list,
    'res-tuple/': return_response_tuple,
    'res-req-data/': res_request_data,
    'res-req-data-output/': res_request_data_with_output_model,
    'redis/': using_redis,
    'login/': login,
    'auth/': auth_true,
    'perm/': check_permission,
    'rate-limit/': rate_limit,
    'test/': test,
    'patch-user/': patch_user,
    'patch-user-class/': PatchUser,
    '': single_user,
}
