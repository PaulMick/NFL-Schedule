from reader import Reader
from schedule import Schedule
from capture import NFLScheduleCapturer

# instantiate utilities
reader = Reader()
schedule = Schedule()
capturer = NFLScheduleCapturer()

# capture and ocr each week
for week in range(1, 19, 1):
    capturer.screenshot(week)
    data = reader.read_screenshot(week, printouts = True)
    schedule.add_week(data)

# write data
schedule.write_data("output/2025Schedule.json")