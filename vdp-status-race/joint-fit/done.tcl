set throttle off
proc check {} {
	if {[string first $::env(DONE) [get_screen]] >= 0} { after time 2 exit; return }
	if {[string first " in " [get_screen]] >= 0 && [string first "rror" [get_screen]] >= 0} { screenshot -raw $::env(SHOT)-error.png; exit }
	after time 5 check
}
after time 10 check
after time 20000 { screenshot -raw $::env(SHOT)-timeout.png; exit }
