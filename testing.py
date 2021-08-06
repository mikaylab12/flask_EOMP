from app import app
import unittest


class Test(unittest.TestCase):
    # check if response for user registration is 404
    def test_user_registration(self):
        test = app.test_client(self)
        response = test.get('/user-registration/')
        status = response.status_code
        self.assertEqual(status, 404)

    # check if response for adding products is 404
    def test_add_products(self):
        test = app.test_client(self)
        response = test.get('/add-products/')
        status = response.status_code
        self.assertEqual(status, 404)

    # check if the response for showing the products is 200
    def test_show_products(self):
        test = app.test_client(self)
        response = test.get('/show-products/')
        status = response.status_code
        self.assertEqual(status, 200)

    # check if response for a single product is 404
    def test_single_productId(self):
        test = app.test_client(self)
        response = test.get('/view-products/5/')
        status = response.status_code
        self.assertEqual(status, 404)


if __name__ == '__main__':
    unittest.main()
