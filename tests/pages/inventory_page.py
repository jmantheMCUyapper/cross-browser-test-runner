"""
Inventory Page Object for SauceDemo site
"""
from selenium.webdriver.common.by import By
from tests.pages.base_pages import BasePage


class InventoryPage(BasePage):
    """Page object for inventory/products page"""

    # Locators
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    PRODUCT_ITEMS = (By.CLASS_NAME, "inventory_item")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    PRODUCT_SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "button[id^='add-to-cart']")
    REMOVE_BUTTONS = (By.CSS_SELECTOR, "button[id^='remove']")
    BURGER_MENU = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def __init__(self, driver):
        super().__init__(driver)

    def is_on_inventory_page(self):
        """Check if we're on the inventory page"""
        return self.is_displayed(self.INVENTORY_CONTAINER)

    def get_product_count(self):
        """Get number of products displayed"""
        products = self.find_elements(self.PRODUCT_ITEMS)
        return len(products)

    def add_item_to_cart(self, index=0):
        """Add item to cart by index"""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        if index < len(buttons):
            buttons[index].click()

    def get_cart_count(self):
        """Get number of items in cart"""
        if self.is_displayed(self.CART_BADGE):
            return int(self.get_text(self.CART_BADGE))
        return 0

    def logout(self):
        """Logout from the application"""
        self.click(self.BURGER_MENU)
        self.click(self.LOGOUT_LINK)