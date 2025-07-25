"""
Shopping cart functionality tests
"""
import pytest
from tests.pages.login_page import LoginPage
from tests.pages.inventory_page import InventoryPage


class TestShoppingCart:
    """Test shopping cart functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, browser, base_url):
        """Setup - login before each test"""
        self.browser = browser
        self.base_url = base_url
        self.login_page = LoginPage(browser)
        self.inventory_page = InventoryPage(browser)

        # Navigate and login
        browser.get(base_url)
        self.login_page.login("standard_user", "secret_sauce")

        # Verify we're logged in
        assert self.inventory_page.is_on_inventory_page()

    def test_add_single_item_to_cart(self):
        """Test adding a single item to cart"""
        # Get initial cart count
        initial_count = self.inventory_page.get_cart_count()

        # Add first item to cart
        self.inventory_page.add_item_to_cart(0)

        # Verify cart count increased
        new_count = self.inventory_page.get_cart_count()
        assert new_count == initial_count + 1

    def test_add_multiple_items_to_cart(self):
        """Test adding multiple items to cart"""
        # Add 3 items to cart
        for i in range(3):
            self.inventory_page.add_item_to_cart(i)

        # Verify cart count
        cart_count = self.inventory_page.get_cart_count()
        assert cart_count == 3

    def test_inventory_page_displays_products(self):
        """Test that inventory page shows products"""
        # Verify products are displayed
        product_count = self.inventory_page.get_product_count()
        assert product_count > 0, "No products displayed on inventory page"
        assert product_count == 6, f"Expected 6 products, found {product_count}"