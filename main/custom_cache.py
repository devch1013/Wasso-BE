from datetime import datetime
from functools import wraps

from django.core.cache import cache
from loguru import logger
from rest_framework.response import Response


class CacheKey:
    CLUB_LIST = "club_list"
    CLUB_DETAIL = "club_detail"


def cache_response(timeout=60, key_prefix="view"):
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
            cache_key = f"{key_prefix}:{user_id}"
            if params:
                cache_key = f"{cache_key}:{params}"

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
