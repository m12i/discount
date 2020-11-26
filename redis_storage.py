from typing import Iterator, List
from datetime import datetime

import redis

from model import Discount
from utils import generate_new_uuid
import os

DISCOUNT_KEY_PREFIX = 'dsc-'


class RedisStorage(object):

    def __init__(self, redis_server):
        self._redis = redis_server

    def insert(self, discount: Discount) -> Discount:
        """Stores the given discount and returns it with a unique ID assigned.

        :param discount: The discount to be stored
        :return: The stored discount
        """
        discount.id = f'{DISCOUNT_KEY_PREFIX}{generate_new_uuid()}'
        utcnow = datetime.utcnow()
        discount.created_at = f'{utcnow.isoformat()}Z'

        brand_id = discount.brand_id
        pipeline = self._redis.pipeline()
        pipeline.set(discount.id, Discount.to_json_str(discount))
        pipeline.zadd(brand_key(brand_id), {discount.id: utcnow.timestamp()})
        pipeline.set(discount_counter_key(discount.id), discount.total_count)
        pipeline.execute()
        return discount

    def grant(self, discount_id: str, user_id: str) -> str:
        """Grant the given discount to the user.

        :param discount_id: The id of the discount to be granted
        :param user_id: The id of the user to whom the discount is granted
        :return: the discount id
        """
        # TODO(mahmood): user pipeline here to ensure it runs in 1 transaction
        key = discount_counter_key(discount_id)
        if not self._redis.exists(key):
            return ''
        remaining_counts = self._redis.decr(key)
        if remaining_counts < 0:
            # Running out of discount
            return ''
        self._redis.zadd(user_key(user_id), {discount_id: 1})
        # TODO(mahmood): refactor this to return a grant object instead.
        return discount_id

    def get_discount_by_id(self, discount_id: str) -> Discount:
        """Returns a discount by id.

        :param discount_id:  The ID of the discount to be returned.
        :return:   The discount
        """
        return Discount.from_json_str(self._redis.get(discount_id))

    def get_discounts(self) -> List[str]:
        """Returns all discounts.

        :return:   The list of discounts
        """
        discounts_keys = [x for x in
                          self._redis.scan_iter(f'{DISCOUNT_KEY_PREFIX}*')]
        if not discounts_keys:
            return []
        return [Discount.from_json_str(discount) for discount in
                self._redis.mget(discounts_keys)]


def init_redis_storage() -> RedisStorage:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    print(f'Connecting to redis by host name: {redis_host}')
    return RedisStorage(redis.StrictRedis(
        host=redis_host, port=6379))


def brand_key(brand_id: str) -> str:
    """Returns the key used for keeping a brand's discount ids in redis"""
    return f'brand-{brand_id}-discounts'


def user_key(user_id: str) -> str:
    """Returns the key used for keeping user's discount ids in redis"""
    return f'user-{user_id}-discounts'


def discount_counter_key(discount_id: str) -> str:
    """Returns the key used for keeping a discount's count in redis"""
    return f'counter-{discount_id}'
