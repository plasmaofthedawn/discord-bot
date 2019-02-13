help_txt = """set_time_zn <Ex: est or utc-5>
add_interval <start day> <start time> <end day>(if different) <end time>
upload_schedule <text file>
show_schedule
remove_interval <index, as displayed in "show_schedule">
clear_schedule          wipes entire schedule"""


upload_schedule_example = """Mon{
10pm - 11pm
}
Tues{
10:30 - 11:00
}
Wed{
10 - 12
}
Sun-Sat{
22-23
}

Note: You can put your schedule in either 24hour format, 12 hours format, or a mix of both. And if multiple days have the same interval, simply put a hyphen between the first and last days(Ex: Wed-Fri{...) In addition, you may use doube hypens(--) for a time that spans over to the next day. Btw, spaces are ignored"""

upload_schedule_help = """upload_schedule > Upload a text file with your schedule, to see an example call "!upload_scedule example\""""