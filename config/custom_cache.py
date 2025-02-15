from datetime import datetime
from enum import Enum
from functools import wraps

from django.core.cache import cache
from loguru import logger
from rest_framework.response import Response


class CacheKey(Enum):
    CLUB_LIST = ("club_list", False)
    CLUB_DETAIL = ("club_detail", True)

    def __init__(self, prefix, need_pk):
        self.prefix = prefix
        self.need_pk = need_pk


def cache_response(key_prefix: CacheKey, timeout=60 * 15):
    """
    DRF 뷰 메소드를 위한 캐시 데코레이터

    Args:
        timeout: 캐시 만료 시간 (초)
        key_prefix: 캐시 키 접두사
    """

    def decorator(func):
        @wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            now = datetime.now()
            # GET 요청만 캐시
            if request.method != "GET":
                return func(view_instance, request, *args, **kwargs)

            # 동적 캐시 키 생성
            user_id = request.user.id if request.user.is_authenticated else "anonymous"

            # URL 파라미터(pk 등)가 있으면 캐시 키에 추가
            params = "_".join(f"{k}_{v}" for k, v in kwargs.items())

            if params:
                cache_key = f"{key_prefix.prefix}:{params}"
            else:
                cache_key = f"{key_prefix.prefix}"
            cache_key = f"{cache_key}:{user_id}"

            # 캐시된 데이터 확인
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.info(
                    f"Retrieved data from cache for key: {cache_key} in {datetime.now() - now} seconds"
                )
                return Response(cached_data)

            # 실제 뷰 함수 실행
            response = func(view_instance, request, *args, **kwargs)

            # 응답 데이터 캐싱
            cache_timeout = timeout
            cache.set(cache_key, response.data, cache_timeout)

            logger.info(
                f"Cached data for key: {cache_key} in {datetime.now() - now} seconds"
            )
            return response

        return wrapper

    return decorator


def delete_cache(key_prefix):
    cache.delete_pattern(f"{key_prefix}:*")


def delete_cache_response(key_prefix: CacheKey):
    """
    DRF 뷰 메소드 실행 후 캐시를 삭제하는 데코레이터

    Args:
        key_prefix: 삭제할 캐시 키 접두사
    """

    def decorator(func):
        @wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            # 실제 뷰 함수 실행
            response = func(view_instance, request, *args, **kwargs)

            # URL 파라미터(pk 등)가 있으면 캐시 키에 추가
            params = "_".join(f"{k}_{v}" for k, v in kwargs.items())

            if key_prefix.need_pk:
                cache_key = f"{key_prefix.prefix}:{params}"
            else:
                cache_key = f"{key_prefix.prefix}"

            # 캐시 삭제
            cache.delete_pattern(f"{cache_key}*")
            logger.info(f"Deleted cache for pattern: {cache_key}*")

            return response

        return wrapper

    return decorator
