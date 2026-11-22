set throttle off
set ::n 0
proc shot {} { screenshot -raw [format %s/f%03d.png $::env(OUT) $::n]; incr ::n; if {$::n >= 60} exit; after frame shot }
after time 20 { set throttle on; after frame shot }
