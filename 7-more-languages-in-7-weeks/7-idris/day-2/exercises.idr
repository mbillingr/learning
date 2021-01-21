
data Vec : (n:Nat) -> (elem:Type) -> Type where
  Nil : Vec Z elem
  (::) : (a:elem) -> (x: Vec n elem) -> Vec (S n) elem

Matrix : Nat -> Nat -> Type -> Type
Matrix n m a = Vec n (Vec m a)

--transpose : Matrix n m a -> Matrix m n a
--transpose (Vec Z (Vec Z a)) = the (Vec Z (Vec Z a)) Nil




recrev : Vec n a -> Vec m a -> Vec (n+m) a
recrev Nil acc = acc
recrev (h :: t) acc = recrev t (h :: acc)


--reversed : Vec n a -> Vec n a
--reversed x = recrev (x, Nil)

--flip : Matrix n m a -> Matrix n m a
--flip x = reverse x
