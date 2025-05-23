import easyocr
import cv2
import numpy as np
import random

# to calculate scale factor
ORIG_RECT_HEIGHT = 84

class Reader:
    def __init__(self):
        self.reader = easyocr.Reader(["en"])

    # ocr sub-section of image
    def read_pos(self, img, x, y, w, h, cap_first: bool = False):
        x = round(x)
        y = round(y)
        w = round(w)
        h = round(h)
        sub_img = img[y:y + h, x:x + w]
        # cv2.imshow("sub img", sub_img)
        # cv2.waitKey(0)
        text = self.reader.readtext(sub_img, detail = 0)

        # common text corrections
        try:
            text.remove("How to Watch")
            text.remove("Ticketmaster")
            text.remove("Hotels")
        except: pass
        for i in range(len(text)):
            text[i] = text[i].replace(".", ":")
            text[i] = text[i].replace("-", ":")
            text[i] = text[i].replace("::", ":")
            if cap_first:
                text[i] = text[i].capitalize()
        return text
    
    # ocr sub-section of image
    def read_rect(self, img, r: list[float], cap_first: bool = False):
        r[0] = round(r[0])
        r[1] = round(r[1])
        r[2] = round(r[2])
        r[3] = round(r[3])
        sub_img = img[r[1]:r[1] + r[3], r[0]:r[0] + r[2]]
        text = self.reader.readtext(sub_img, detail = 0)

        # common text corrections
        try:
            text.remove("How to Watch")
            text.remove("Ticketmaster")
            text.remove("Hotels")
        except: pass
        for i in range(len(text)):
            text[i] = text[i].replace(".", ":")
            text[i] = text[i].replace("-", ":")
            text[i] = text[i].replace("::", ":")
            if cap_first:
                text[i] = text[i].capitalize()
        return text
    
    # ocr game rectangle
    def read_game(self, img, r: list[float], scale_factor: float):
        game = {
            "tbd": bool,
            "date": "",
            "time": "",
            "channel": "",
            "home": "",
            "away": ""
        }

        # time and channel
        left_text = self.read_pos(img, r[0], r[1], 200 * scale_factor, 80 * scale_factor)

        # away team
        game["away"] = self.read_pos(img, r[0] + 400 * scale_factor, r[1], 200 * scale_factor, 80 * scale_factor, cap_first = True)[0]
        
        # home team
        game["home"] = self.read_pos(img, r[0] + 850 * scale_factor, r[1], 200 * scale_factor, 80 * scale_factor, cap_first = True)[0]

        # account for TBD games
        if left_text[0] == "TBD":
            game["tbd"] = True
        else:
            game["tbd"] = False
            game["time"] = left_text[0]
            game["channel"] = left_text[1]

        return game

    # ocr entire week's data, call this
    def read_screenshot(self, week: int, printouts: bool = False):
        games_sc = cv2.imread(f"input/week{week}games.png")
        byes_sc = cv2.imread(f"input/week{week}byes.png")

        games_rgb = cv2.cvtColor(games_sc, cv2.COLOR_BGR2RGB)
        byes_rgb = cv2.cvtColor(byes_sc, cv2.COLOR_BGR2RGB)

        # color range for bounding the white rectangles
        games_lower_color = np.array([239, 239, 239])
        games_upper_color = np.array([256, 256, 256])
        byes_lower_color = np.array([245, 245, 245])
        byes_upper_color = np.array([256, 256, 256])

        games_mask = cv2.inRange(games_rgb, games_lower_color, games_upper_color)
        byes_mask = cv2.inRange(byes_rgb, byes_lower_color, byes_upper_color)

        games_contours, _ = cv2.findContours(games_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        byes_contours, _ = cv2.findContours(byes_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find white rectangles
        game_rects = []
        for cnt in games_contours:
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4 and cv2.contourArea(cnt) > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                if y > 75:
                    game_rects.append([x, y, w, h])
        bye_rects = []
        for cnt in byes_contours:
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4 and cv2.contourArea(cnt) > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                bye_rects.append([x, y, w, h])

        # scaling factor of screenshot
        scale_factor = game_rects[0][3] / ORIG_RECT_HEIGHT
        # print(f"scale factor: {round(scale_factor, 3)}")

        # group game rectangles by day
        grouped_game_rects = []
        group = []
        prev_y = -1000
        game_rects.sort(key = lambda r: r[1])
        for r in game_rects:
            if abs(r[1] - prev_y) > 180 * scale_factor:
                if len(group) > 0:
                    grouped_game_rects.append(group)
                group = []
            group.append(r)
            prev_y = r[1]
        grouped_game_rects.append(group)

        week_data = {
            "week": week,
            "games": [],
            "tbd_games": [],
            "byes": []
        }

        # display game rectangle bounding boxes, optional
        # for g in grouped_game_rects:
        #     color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        #     for i in range(len(g)):
        #         if i == 0:
        #             cv2.rectangle(games_sc, (g[i][0] - round(10 * scale_factor), g[i][1] - round(75 * scale_factor)), (g[i][0] + round(390 * scale_factor), g[i][1] - round(25 * scale_factor)), color, 2)
        #         cv2.rectangle(games_sc, (g[i][0], g[i][1]), (g[i][0] + g[i][2], g[i][1] + g[i][3]), color, 2)
        #         cv2.rectangle(games_sc, (g[i][0], g[i][1]), (g[i][0] + round(200 * scale_factor), g[i][1] + round(80 * scale_factor)), color, 2)
        #         cv2.rectangle(games_sc, (g[i][0] + round(400 * scale_factor), g[i][1]), (g[i][0] + round(600 * scale_factor), g[i][1] + round(80 * scale_factor)), color, 2)
        #         cv2.rectangle(games_sc, (g[i][0] + round(850 * scale_factor), g[i][1]), (g[i][0] + round(1050 * scale_factor), g[i][1] + round(80 * scale_factor)), color, 2)
                    
        # cv2.imshow("Detected Rectangles", games_sc)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # ocr games by day
        for group in grouped_game_rects:
            date = self.read_pos(games_sc, group[0][0] - 10 * scale_factor, group[0][1] - 75 * scale_factor, 400 * scale_factor, 50 * scale_factor)[0]
            date = date.replace("STH", "5TH")
            for game_rect in group:
                game = self.read_game(games_sc, game_rect, scale_factor)
                game["date"] = date
                if date == "GAMES NOT YET SCHEDULED":
                    week_data["tbd_games"].append(game)
                else:
                    week_data["games"].append(game)

        # reference position for reading byes
        byes_landmark = [round((bye_rects[0][0] + bye_rects[1][0] + bye_rects[2][0]) / 3), round((bye_rects[0][1] + bye_rects[1][1] + bye_rects[2][1]) / 3)]

        # display byes bounding box, optional
        # for b in bye_rects:
        #     cv2.rectangle(byes_sc, (b[0], b[1]), (b[0] + b[2], b[1] + b[3]), (255, 0, 0), 2)
        # cv2.rectangle(byes_sc, (round(byes_landmark[0] - 620 * scale_factor), round(byes_landmark[1] + 490 * scale_factor)), (round(byes_landmark[0] + 870 * scale_factor), round(byes_landmark[1] + 565 * scale_factor)), (0, 255, 0), 2)
        # cv2.imshow("byes", byes_sc)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # ocr byes
        byes = self.read_pos(byes_sc, byes_landmark[0] - 620 * scale_factor, byes_landmark[1] + 490 * scale_factor, 1500 * scale_factor, 75 * scale_factor, cap_first = True)

        # no byes this week
        if byes[0].count("No") > 0 or byes[0].count("no") > 0:
            byes = []

        for bye in byes:
            week_data["byes"].append({
                "team": bye
            })

        # status printout
        if printouts:
            print(f'Week {week_data["week"]} Data:')
            for game in week_data["games"]:
                print(f'{game["date"]} at {game["time"]}: {game["away"]} at {game["home"]} on {game["channel"]}')
            for tbd_game in week_data["tbd_games"]:
                print(f'TBD: {tbd_game["away"]} at {tbd_game["home"]}')
            for bye in week_data["byes"]:
                print(f'BYE: {bye["team"]}')

        return week_data
            