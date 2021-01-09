use mini_kanren::*;

fn main() {
    dbg!(run!(*, q { eq(q, 1); }));
    dbg!(run!(*, q { eq(q.clone(), 1); eq(q, 2); }));
}
