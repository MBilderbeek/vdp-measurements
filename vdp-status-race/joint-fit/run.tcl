set throttle off
proc check {} {
  if {![catch {set s [get_screen]}] && [string match "*All done*" $s]} { exit }
  after time 5 check
}
after time 10 check
after time 40000 exit
