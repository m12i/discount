from unittest import TestCase
import fakeredis

from model import Discount
from redis_storage import RedisStorage, DISCOUNT_KEY_PREFIX

mock_redis = fakeredis.FakeStrictRedis()

BRAND_ID = 'brand 1'
USER_ID = 'user 1'


class TestStorage(TestCase):

    def test_insert(self):
        storage = RedisStorage(mock_redis)
        print('Should store a discount successfully')
        a_discount = Discount(
            brand_id=BRAND_ID,
            discount_code='This is discount 0',
            total_count=1,
        )
        actual = storage.insert(a_discount)
        self.assertIsNotNone(actual)
        self.assertIsNotNone(actual.created_at)
        self.assertTrue(actual.id.startswith(DISCOUNT_KEY_PREFIX))

        print('Should retrieve the discount by ID')
        discount_id = actual.id
        actual2 = storage.get_discount_by_id(discount_id)
        self.assertEqual(discount_id, actual2.id)

        print('Should retrieve all discounts')
        discount_id = actual.id
        actual = storage.get_discounts()
        self.assertEqual(1, len(actual))
        self.assertEqual(discount_id, actual[0].id)

        print('Should grant a discount code to a user')
        actual = storage.grant(discount_id, USER_ID)
        self.assertEqual(discount_id, actual)

        print('Should NOT grant if a discount code runs out')
        actual = storage.grant(discount_id, USER_ID)
        self.assertEqual('', actual)

        print('Should NOT grant if a discount code is invalid')
        actual = storage.grant('an-invalid-discount-code', USER_ID)
        self.assertEqual('', actual)
