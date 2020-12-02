
fun eq_int(a: int, b: int) = (a = b)
fun less_than(a: int, b: int) = (a < b)

signature N =
sig
  type number
  exception Too_small
  val succ : number -> number
  val pred : number -> number
  val is_zero : number -> bool
end

signature N_C_R =
sig
  type number
  exception Too_small
  val conceal : int -> number
  val succ : number -> number
  val pred : number -> number
  val is_zero : number -> bool
  val reveal : number -> int
end

functor NumberAsInt() :> N_C_R =
struct
  type number = int
  exception Too_small
  fun conceal(n)
      = n
  fun succ(n)
      = n + 1
  fun pred(n)
      = if eq_int(n, 0)
          then raise Too_small
          else n - 1
  fun is_zero(n)
      = eq_int(n, 0)
  fun reveal(n)
      = n
end

functor NumberAsNum() :> N_C_R =
struct
  datatype num =
    Zero
  | One_more_than of num
  type number = num
  exception Too_small
  fun conceal(n)
      = if eq_int(n, 0)
          then Zero
          else One_more_than(conceal(n-1))
  fun succ(n)
      = One_more_than(n)
  fun pred(Zero)
      = raise Too_small
    | pred(One_more_than(n))
      = n
  fun is_zero(Zero)
      = true
    | is_zero(a_num)
      = false
  fun reveal(Zero)
      = 0
    | reveal(One_more_than(n))
      = 1 + reveal(n)
end

structure IntStruct = NumberAsInt();
structure NumStruct = NumberAsNum();

signature P =
  sig
    type number
    val plus: (number * number) -> number
  end

functor PON (structure a_N : N) 
  :> 
  P where type number = a_N.number
  =
struct
  type number = a_N.number
  fun plus(n, m)
    = if a_N.is_zero(n)
        then m
        else a_N.succ(plus(a_N.pred(n), m))
end

structure IntArith = 
  PON(structure a_N = IntStruct)

structure NumArith = 
  PON(structure a_N = NumStruct)



functor NumberAsInt2()
  :>
  N where type number = int
  =
  struct
    type number = int
    exception Too_small
    fun succ(n)
        = n + 1
    fun pred(n)
        = if eq_int(n, 0)
            then raise Too_small
            else n - 1
    fun is_zero(n)
        = eq_int(n, 0)
  end

structure IntStruct2 = NumberAsInt2();

structure IntArith2 = 
  PON(structure a_N = IntStruct2)


signature S = 
sig
  type number1
  type number2
  val similar : (number1 * number2) -> bool
end

functor Same(structure a_N : N
             structure b_N : N)
  :>
  S where type number1 = a_N.number
    where type number2 = b_N.number
  =
  struct
    type number1 = a_N.number
    type number2 = b_N.number
    fun sim(n, m)
        = if a_N.is_zero(n)
            then b_N.is_zero(m)
            else sim(a_N.pred(n), b_N.pred(m))
    fun similar(n, m)
        = ((sim(n, m)
            handle a_N.Too_small => false)
           handle b_N.Too_small => false)
  end

structure SimIntNum = 
  Same(structure a_N = IntStruct
       structure b_N = NumStruct)

structure SimNumInt = 
  Same(structure a_N = NumStruct
       structure b_N = IntStruct)


fun new_plus(x, y)
    = IntStruct.reveal(
        IntArith.plus(
          IntStruct.conceal(x),
          IntStruct.conceal(y)))


signature J =
sig
  val new_plus : (int * int) -> int
end

functor NP(structure a_N : N_C_R
           structure a_P : P
           sharing type a_N.number = a_P.number)
  :> J =
  struct
    fun new_plus(x, y)
        = a_N.reveal(
            a_P.plus(
              a_N.conceal(x),
              a_N.conceal(y)))
  end

structure NPStruct =
  NP(structure a_N = NumStruct
     structure a_P = NumArith)

structure NPStruct =
  NP(structure a_N = NumberAsNum()
     structure a_P = PON(structure a_N = a_N))


signature T = 
sig
  type number
  val times : (number * number) -> number
end


functor TON(structure a_N : N
            structure a_P : P
            sharing type a_N.number = a_P.number)
  :> 
  T where type number = a_N.number
  =
  struct
    type number = a_N.number
    fun times(n, m)
        = if a_N.is_zero(m)
            then m
            else a_P.plus(n, times(n, a_N.pred(m)))
  end
