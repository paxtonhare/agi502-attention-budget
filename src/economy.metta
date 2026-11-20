; Scalar specifications for Python's batched economy bookkeeping.
(= (rent-wage $sti $proof-entry)
   (+ (* 0.85 $sti) (* 3.0 $proof-entry)))
(= (co-use $weight $pair-used) (+ $weight $pair-used))
(= (spread $sti $weight $total-weight)
   (/ (* (* 0.10 $sti) $weight) $total-weight))
(= (recency $age) (/ 1.0 $age)) ; age supplied as power of two
(= (harness-score $overlap $used-decay $seen-decay)
   (+ $overlap (+ (* 0.5 $used-decay) (* 0.25 $seen-decay))))
(= (stimulus $sti $overlap) (+ $sti (* 0.25 $overlap)))
(= (rank-before $a $b $a-priority $b-priority)
   (if (== $a $b) (< $a-priority $b-priority) (> $a $b)))
