import json


class Discount(object):
    """A class to store a discount."""

    def __init__(self, brand_id: str, discount_code: str, total_count: int):
        self.discount_code = discount_code
        self.total_count = total_count
        self.brand_id = brand_id
        self.id = None
        self.created_at = None

    def __repr__(self):
        return f'({self.id}, {self.brand_id}, {self.discount_code}'

    @classmethod
    def to_json_str(cls, discount):
        return json.dumps(discount, default=lambda o: o.__dict__)

    @classmethod
    def from_json_str(cls, data: str):
        msg_dict = json.loads(data)
        out = Discount('', '', 0)
        out.__dict__.update(msg_dict)
        return out
