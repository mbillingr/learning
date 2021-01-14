use mini_kanren::goals::list::{membero, conso};
use mini_kanren::{conde, eq, list, run, Goal, db_facts, db_rel, defrel, Value, Substitution, fresh, Stream};
use mini_kanren::database::Database;
use std::sync::Arc;

fn main() {
    println!("DAY 1\n=====\n");
    dbg!(run!(*, q, eq(q, 1)));
    dbg!(run!(*, q, eq(q.clone(), 1), eq(q, 2)));
    dbg!(run!(*, q, membero(q, list![1, 2, 3])));
    dbg!(run!(3, q, membero(list![1, 2, 3], q)));
    dbg!(run!(3, q, membero(3, list![1, 2, q, 4])));

    dbg!(run!(*, q, conde! {
        eq(q, 1);
        eq(q, 2), eq(q, 3);
        eq(q, "abc");
    }));

    dbg!(run!(*, q, conso("a", list!["b", "c"], q)));
    dbg!(run!(*, (h, t), conso(h, t, list!["a", "b", "c"])));

    exercise1();
    exercise6();
}

fn exercise1() {
    println!("\nExercise 1\n----------");
    println!("{:?}", run!(*, q,
        membero(q, list![1, 2, 3, "foo"]),
        membero(q, list![3, 4, 5, "foo"]),
    ));
}

fn exercise6() {
    println!("\nExercise 6\n----------");

    db_rel! {
        childo(parent, child);
        spouseo(a, b);
    }

    let mut db = Database::new();
    db_facts! {
        db {
            spouseo("Abraham", "Mona");
            spouseo("Clancy", "Jackie");
            spouseo("Homer", "Marge");

            childo("Abraham", "Herb");
            childo("Abraham", "Homer");
            childo("Mona", "Homer");

            childo("Clancy", "Marge");
            childo("Clancy", "Patty");
            childo("Clancy", "Selma");
            childo("Jackie", "Marge");
            childo("Jackie", "Patty");
            childo("Jackie", "Selma");

            childo("Selma", "Ling");

            childo("Homer", "Bart");
            childo("Homer", "Lisa");
            childo("Homer", "Maggie");
            childo("Marge", "Bart");
            childo("Marge", "Lisa");
            childo("Marge", "Maggie");
        }
    };

    fn ancestoro(db: &Arc<Database>, ancestor: impl Into<Value>, descendant: impl Into<Value>) -> impl Goal<Substitution<'static>> {
        let ancestor = ancestor.into();
        let descendant = descendant.into();
        conde! {
            childo(db, ancestor.clone(), descendant.clone());
            fresh!{ (parent),
                childo(db, ancestor, parent),
                childo(db, parent, descendant),
            };
        }
    }

    fn siblingo(db: &Arc<Database>, a: impl Into<Value>, b: impl Into<Value>) -> impl Goal<Substitution<'static>> {
        let a = a.into();
        let b = b.into();
        fresh!{ (parent),
            childo(db, parent, a.clone()),
            childo(db, parent, b.clone()),
            not_eqc(a.clone(), b.clone()),
        }
    }

    /// unequality constraint
    fn not_eqc(a: impl Into<Value>, b: impl Into<Value>) -> impl Goal<Substitution<'static>> {
        let a = a.into();
        let b = b.into();
        move |s: Substitution<'static>| match s.clone().unify(&a, &b) {
            Some(_) => Stream::empty(),
            None => Stream::singleton(s),
        }
    }

    let db = Arc::new(db);

    let person = "Bart";
    println!("Ancestors of {}: {:?}", person, run!(*, q, ancestoro(&db, q, person)));

    println!("Siblings of {}: {:?}", person, run!(*, q, siblingo(&db, person, q)));
}
