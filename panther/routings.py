import re
from copy import deepcopy
from runpy import run_path
from typing import Callable
from collections import Counter
from typing import MutableMapping
from collections.abc import Mapping
from functools import reduce, partial

from panther.configs import config


def check_and_load_urls(urls: str | None) -> dict | None:
    from panther.logger import logger

    if urls is None:
        return logger.critical("configs.py Does Not Have 'URLs'")

    try:
        full_urls_path = config['base_dir'] / urls
        urls_dict = run_path(str(full_urls_path))['urls']
    except FileNotFoundError:
        return logger.critical("Couldn't Open 'URLs' Address.")
    except KeyError:
        return logger.critical("'URLs' Address Does Not Have 'urls'")
    if not isinstance(urls_dict, dict):
        return logger.critical("'urls' Of URLs Is Not dict.")
    return urls_dict


def flatten_urls(urls: dict) -> dict:
    return {k: v for k, v in _flattening_urls(urls)}


def _flattening_urls(data: dict | Callable, url: str = ''):
    # Add `/` add the end of url
    if not url.endswith('/'):
        url = f'{url}/'

    if isinstance(data, dict):
        for k, v in data.items():
            yield from _flattening_urls(v, f'{url}{k}')
    else:
        # Remove `/` prefix of url
        url = url.removeprefix('/')

        # Collect it, if it doesn't have problem
        if _is_url_endpoint_valid(url=url, endpoint=data):
            yield url, data


def _is_url_endpoint_valid(url: str, endpoint: Callable) -> bool:
    from panther.logger import logger

    if endpoint is ...:
        logger.error(f"URL Can't Point To Ellipsis. ('{url}' -> ...)")
    elif endpoint is None:
        logger.error(f"URL Can't Point To None. ('{url}' -> None)")
    elif url and not re.match(r'^[a-zA-Z<>0-9_/-]+$', url):
        logger.error(f"URL Is Not Valid. --> '{url}'")
    else:
        return True
    return False


def finalize_urls(urls: dict) -> dict:
    """convert flat dict to nested"""
    urls_list = list()
    for url, endpoint in urls.items():
        path = dict()
        if url == '':
            # This condition only happen when
            #   user defines the root url == '' instead of '/'
            url = '/'

        for single_path in list(filter(lambda x: x != '', url.split('/')[:-1][::-1])) or ['']:
            if single_path != '' and not path:
                path = {single_path: {'': endpoint}}
            else:
                path = {single_path: path or endpoint}
        urls_list.append(path)
    return _merge(*urls_list) if urls_list else {}


def _merge(destination: MutableMapping, *sources) -> MutableMapping:
    return _simplify_urls(reduce(partial(_deepmerge), sources, destination))


def _simplify_urls(urls):
    simplified_urls = dict()

    for key, value in urls.items():
        if isinstance(value, dict):
            simplified_value = _simplify_urls(value)
            if isinstance(simplified_value, dict) and len(simplified_value) == 1 and '' in simplified_value:
                simplified_urls[key] = simplified_value['']
            else:
                simplified_urls[key] = simplified_value
        else:
            simplified_urls[key] = value

    return simplified_urls


def _deepmerge(dst, src):
    """Credit to Travis Clarke --> https://github.com/clarketm/mergedeep"""
    for key in src:
        if key in dst:
            if _is_recursive_merge(dst[key], src[key]):
                _deepmerge(dst[key], src[key])
            else:
                dst[key] = deepcopy(src[key])
        else:
            dst[key] = deepcopy(src[key])
    return dst


def _is_recursive_merge(a, b):
    both_mapping = isinstance(a, Mapping) and isinstance(b, Mapping)
    both_counter = isinstance(a, Counter) and isinstance(b, Counter)
    return both_mapping and not both_counter


def find_endpoint(path: str) -> tuple[Callable | None, str]:
    urls = config['urls']

    if (location := path.find('?')) != -1:
        path = path[:location]
    path = path.removesuffix('/').removeprefix('/')  # 'user/list'
    paths = path.split('/')  # ['user', 'list']
    paths_len = len(paths)

    found_path = ''
    for i, split_path in enumerate(paths):
        last_path = bool((i + 1) == paths_len)
        found = urls.get(split_path)

        # `found` is callable
        if last_path and callable(found):
            found_path += f'{split_path}/'
            return found, found_path

        # `found` is dict
        if isinstance(found, dict):
            found_path += f'{split_path}/'
            if last_path and callable(endpoint := found.get('')):
                return endpoint, found_path

            urls = found
            continue

        # `found` is None
        _continue = False
        for key, value in urls.items():
            if key.startswith('<'):
                if last_path:
                    if callable(value):
                        found_path += f'{key}/'
                        return value, found_path

                    elif isinstance(value, dict) and '' in value:
                        found_path += f'{key}/'
                        return value[''], found_path

                    else:
                        return None, ''

                urls = value
                found_path += f'{key}/'
                _continue = True
                break

        if _continue:
            continue

    return None, ''


def collect_path_variables(request_path: str, found_path: str) -> dict:
    found_path = found_path.removesuffix('/').removeprefix('/')
    request_path = request_path.removesuffix('/').removeprefix('/')
    path_variables = dict()
    for f_path, r_path in zip(found_path.split('/'), request_path.split('/')):
        if f_path.startswith('<'):
            path_variables[f_path[1:-1]] = r_path
    return path_variables
