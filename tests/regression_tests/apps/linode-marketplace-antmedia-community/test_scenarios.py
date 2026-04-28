from playwright.sync_api import expect
from regression_tests.pages.antmedia_community.dashboard_page import DashboardPage
from regression_tests.pages.antmedia_community.login_page import LoginPage


def test_antmedia_startup(context, base_url):
    # Verifies that the Ant Media Server started and login page loads successfully.
    login_page = LoginPage(context)
    login_page.navigate(base_url)
    expect(context, "Ant Media Server is not started").to_have_title("Management of Ant Media Server")
    expect(login_page.username_input, "The username input field did not render on the screen.").to_be_visible()


def test_antmedia_login(context, base_url, app_credentials):
    # Verifies that user can loging to And Media Server with provided credentials.
    username = app_credentials["Ant Media Server Username"]
    password = app_credentials["Ant Media Server Password"]
    login_page = LoginPage(context)
    login_page.navigate(base_url)
    login_page.login(username, password)
    dashboard_page = DashboardPage(context)
    expect(dashboard_page.active_live_streams_label, "Credentials are invalid or something went wrong").to_be_visible()


def test_antmedia_start_stream():
    pass
