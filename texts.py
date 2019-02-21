help_txt = """Scheduling Help

set_time_zn <Ex: est or utc-5>
add_interval <start day> <start time> <end day>(if different) <end time>
upload_schedule <text file>
show_schedule
remove_interval <index, as displayed in "show_schedule">
clear_schedule          wipes entire schedule
authors          returns a list authors"""


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

upload_schedule_help = """upload_schedule > Upload a text file with your schedule, to see an example call "!upload_schedule example\""""

upload_ballot_help = """Get an example of proper formating using 'upload_ballot example'

Notes: This system doesn't detect every character for proper formating, so you may not get any error, which is why the info regarding a ballot is printed back for confirmation. If you want to include double quotes in any of your ballot items, simply use the escape character(\\")"""

voting_help = """Voting Help

upload_ballot          See 'upload_ballot help' for instruction
close_ballot <ballot noun or ID>    closes a ballot
extend_time <ballot noun or ID> <Days:Hours:Minutes>    pushes back scheduled closing time
vote <ballot noun or ID> <choosen options, separated by commas>(if writing in, put vote within double quotes, Ex: "pie")
current_ballots          lists currently open ballots
my_ballots          lists all of your ballots, open and closed
closed_ballots          lists all closed ballots
get_ballot <ballot noun or ID> <optional, 0 or 1 for layout>    prints all information for a ballot
add_options <ballot noun or ID> [<option 1>, etc..]    adds option(s) to ballot
allow_write_in <ballot noun or ID>    enables writing in, for a ballot
authors          returns a list authors"""