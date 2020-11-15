#!/usr/bin/env python3

import unittest

try:
    from app import app

except Exception as error:
    print(f"Something is missing {error}")


class ApiTest(unittest.TestCase):
    def test_inde(self):
        tester = app.test_client(self)
        response = tester.get('/')
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)


if __name__ == '__main__':
    unittest.main()
