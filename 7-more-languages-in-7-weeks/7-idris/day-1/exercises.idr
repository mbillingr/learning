mutual
  data Even = Zero | Succ Odd
  data Odd = After Even


data Tree = Leaf | Node (a, Tree, Tree)


recrev : (List a, List a) -> List a
recrev (Nil, out) = out
recrev (h :: t, out) = recrev (t, h :: out)


reversed : List a -> List a
reversed x = recrev (x, Nil)
