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

new_ballot_help = """new_ballot "<prompt>" ["<option1>", ect..] write_in=<bool> (0 or 1) roles=["<role1>", ect..](roles to limit vote to, roles are listed as text, not meantions) svpc=<bool>(see votes pre-close) title=<title>(optional, title of ballot)

Example: new_ballot "What is the best cake?" ["Cookie Cake", "Cake"] write_in=0 roles=["everyone"] svpc=1 title="Best Cake" 

Prompt has to go first, then options, but everything else can be in whatever order"""

voting_help = """Voting Help

new_ballot          See 'new_ballot help' for instruction
close_ballot <ballot name or ID>    closes a ballot
extend_time <ballot name or ID> <Days:Hours:Minutes>    pushes back scheduled closing time
vote <ballot name or ID> <option #>(if writing in, put vote within double quotes, Ex: "pie")
current_ballots          lists currently open ballots
my_ballots          lists all of your ballots, open and closed
closed_ballots          lists all closed ballots
ballot_options <ballot name or ID>    prints a list of all options for a ballot
get_ballot <ballot name or ID>    prints all information for a ballot
add_options <ballot name or ID> [<option 1>, etc..]    adds option(s) to ballot
add_roles <ballot name or ID> [<role 1>, etc..]    adds role(s) to those allowed to vote
allow_write_in <ballot name or ID>    enables writing in, for a ballot
authors          returns a list authors"""