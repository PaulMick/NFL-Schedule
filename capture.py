from playwright.sync_api import sync_playwright
import time
import cv2

class NFLScheduleCapturer:
    def __init__(self):
        pass

    def screenshot(self, week: int):
        # full-page screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"https://www.nfl.com/schedules/2025/REG{week}/")
            time.sleep(3)
            # page.click('button:has-text("Accept Cookies")')
            page.click('button:has-text("Reject Optional Cookies")')
            time.sleep(3)
            page.screenshot(path = f"input/week{week}full.png", full_page = True, scale = "css")
            browser.close()

        # divided screenshots (games and byes)
        sc = cv2.imread(f"input/week{week}full.png")
        games_sc = sc[470:1850, 0:1280]
        byes_sc = sc[2250:2900, 0:1280]
        cv2.imwrite(f"input/week{week}games.png", games_sc)
        cv2.imwrite(f"input/week{week}byes.png", byes_sc)
        print(f"Week {week} captured")