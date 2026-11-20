; A proof lists selectable entry IDs in forward order. Only the current
; focus is stored as obs/edge atoms in the reasoner's space.
(= (chain2 $goal $subject)
   (match &self (, (obs $f $p $subject) (edge $r $p $goal)) ($f $r)))
(= (chain3 $goal $subject)
   (match &self (, (obs $f $p $subject) (edge $r $p $q) (edge $s $q $goal)) ($f $r $s)))
