# Developer: Bikash

import pytest
from playwright.sync_api import sync_playwright
import os
import allure
import functools
import yaml
import logging
import json
from datetime import datetime
from typing import Dict, Generator
import requests
from utills.excel_reader import ExcelReader

CONFIG_PATH = 'config/config.yaml'
SCREENSHOT_DIR = "report/screenshots"
ALLURE_REPORT_DIR = "report/allure"
EXCEL_PATH = "data/test_data.xlsx"


def load_yaml_config(config_path: str) -> Dict:
    """Load and validate configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        required_keys = ['environment', 'urls', 'credentials', 'timeouts', 'reporting']
        if not all(key in config for key in required_keys):
            raise ValueError(f"Config file missing required sections: {required_keys}")
        return config
    except Exception as e:
        pytest.fail(f"Failed to load config: {str(e)}")


@pytest.fixture(scope='session')
def config() -> Dict:
    """Provide configuration as a session-scoped fixture."""
    return load_yaml_config(CONFIG_PATH)


def pytest_configure(config):
    """Configure pytest environment and Allure reporting."""
    cfg = load_yaml_config(CONFIG_PATH)

    # Setup directories
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(ALLURE_REPORT_DIR, exist_ok=True)

    # Environment properties
    env_data = cfg['environment']
    env_props = [
        f"Browser={env_data['browser']}",
        f"Platform={env_data['platform']}",
        f"TestedBy={env_data['tested_by']}"
    ]
    with open(os.path.join(ALLURE_REPORT_DIR, "environment.properties"), "w") as f:
        f.write("\n".join(env_props))

    # Categories definition
    categories = [
        {"name": "Regression", "matchedStatuses": ["passed", "failed"]},
        {"name": "Known Issues", "matchedStatuses": ["broken"], "traceRegex": ".*known_issue.*"}
    ]
    with open(os.path.join(ALLURE_REPORT_DIR, "categories.json"), "w") as f:
        json.dump(categories, f, indent=2)

    # Executor info
    with open(os.path.join(ALLURE_REPORT_DIR, "executor.json"), "w") as f:
        json.dump(cfg['executor'], f, indent=2)


@pytest.fixture(scope="session")
def api_request(config):
    """Fixture for making API requests with Playwright context."""
    with sync_playwright() as playwright:
        context = playwright.request.new_context(
            base_url=config['urls']['api_base_url'],
            extra_http_headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        yield context
        context.dispose()


@pytest.fixture(scope="session")
def http_session(config):
    """Fixture for making API requests using requests library."""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield session
    session.close()


class AllureScreenshotHandler(logging.Handler):
    """Custom logging handler for screenshots in Allure."""
    def __init__(self, page):
        super().__init__()
        self.page = page

    def emit(self, record):
        try:
            msg = self.format(record)
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_name = f"{record.levelname}_{timestamp}"
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{screenshot_name}.png")

            if self.page:
                self.page.screenshot(path=screenshot_path)
                with allure.step(msg):
                    allure.attach.file(
                        screenshot_path,
                        name=screenshot_name,
                        attachment_type=allure.attachment_type.PNG
                    )
        except Exception as e:
            logging.error(f"Failed to capture screenshot for log: {e}")


@pytest.fixture(scope="session")
def browser(config) -> Generator:
    """Launch browser instance with configuration."""
    with sync_playwright() as playwright:
        browser_type = getattr(playwright, config['environment']['browser'])
        browser = browser_type.launch(headless=config['environment'].get('headless', False))
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def browser_context(config, browser) -> Generator:
    """Create browser context and block ads/tracking."""
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='en-US'
    )

    def block_ads(route, request):
        blocked_domains = ["ads", "doubleclick.net", "googlesyndication"]
        if any(bad in request.url for bad in blocked_domains):
            route.abort()
        else:
            route.continue_()

    context.route("**/*", block_ads)
    context.clear_cookies()
    context.clear_permissions()

    context.set_default_timeout(config['timeouts']['element_wait'])

    yield context
    context.close()


# @pytest.fixture(scope="session")
# def browser_context(config, browser) -> Generator:
#     """Create browser context with timeout settings."""
#     context = browser.new_context(
#         viewport={'width': 1920, 'height': 1080},
#         locale='en-US'
#     )
#     context.set_default_timeout(config['timeouts']['page_load'])
#     yield context
#     context.close()


@pytest.fixture(scope="function")
def page(browser_context) -> Generator:
    """Provide a fresh page for each test."""
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(autouse=True)
def setup_logging(page):
    """Configure logging with Allure integration."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = AllureScreenshotHandler(page)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not any(isinstance(h, AllureScreenshotHandler) for h in logger.handlers):
        logger.addHandler(handler)
    yield
    logger.handlers = [h for h in logger.handlers if not isinstance(h, AllureScreenshotHandler)]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshots on test failure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{item.name}_failure.png")
            try:
                page.screenshot(path=screenshot_path)
                allure.attach.file(
                    screenshot_path,
                    name=f"Failure - {item.name}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                logging.error(f"Failed to capture failure screenshot: {e}")


def pytest_generate_tests(metafunc):
    if "order_test_data" in metafunc.fixturenames:
        reader = ExcelReader(EXCEL_PATH)
        test_cases = reader.get_order_test_cases()
        metafunc.parametrize("order_test_data", test_cases, ids=[tc['Scenario'] for tc in test_cases])
