set throttle off
after time 25 { set throttle on; after time 2 { screenshot -raw $::env(SHOT)-fh.png; exit } }
