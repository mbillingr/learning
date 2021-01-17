use mini_kanren::core::pair::Pair;
use mini_kanren::database::Database;
use mini_kanren::goals::list::{conso, for_each, membero, rembero};
use mini_kanren::prelude::*;
use mini_kanren::{conda, conj, db_facts, db_rel, fresh, list, run};
use std::collections::HashMap;
use std::sync::Arc;

// declare relations
db_rel! {
    ploto(a, b)
}

fn main() {
    let mut story_elements = HashMap::new();
    story_elements.insert(
        ("maybe-telegram-girl", "telegram-girl"),
        "A singing telegram girl arrives.",
    );
    story_elements.insert(
        ("maybe-motorist", "motorist"),
        "A stranded motorist comes asking for help.",
    );
    story_elements.insert(
        ("motorist", "policeman"),
        "Investigating an abandoned car, a policeman appears.",
    );
    story_elements.insert(
        ("motorist", "dead-motorist"),
        "The motorist is found dead in the lounge, killed by a wrench.",
    );
    story_elements.insert(
        ("telegram-girl", "dead-telegram-girl"),
        "The telegram girl is murdered in the hall with a revolver.",
    );
    story_elements.insert(
        ("policeman", "dead-policeman"),
        "The policeman is killed in the library with a lead pipe.",
    );
    story_elements.insert(
        ("dead-motorist", "guilty-mustard"),
        "Colonel Mustard killed the motorist, his old driver during the war.",
    );
    story_elements.insert(
        ("dead-motorist", "guilty-scarlet"),
        "Miss Scarlet killed the motorist to keep her secrets safe.",
    );
    story_elements.insert(
        ("dead-motorist", "guilty-peacock"),
        "Mrs. Peacock killed the motorist.",
    );
    story_elements.insert(
        ("dead-motorist", "guilty-peacock"),
        "Mrs. Peacock killed the motorist.",
    );
    story_elements.insert(
        ("dead-telegram-girl", "guilty-scarlet"),
        "Miss Scarlet killed the telegram girl so she wouldn't talk.",
    );
    story_elements.insert(
        ("dead-telegram-girl", "guilty-peacock"),
        "Mrs. Peacock killed the telegram girl.",
    );
    story_elements.insert(
        ("dead-telegram-girl", "guilty-wadsworth"),
        "Wadsworth shot the telegram girl.",
    );
    story_elements.insert(
        ("dead-policeman", "guilty-scarlet"),
        "Miss Scarlet tried to cover her tracks by murdering the policeman.",
    );
    story_elements.insert(
        ("dead-policeman", "guilty-peacock"),
        "Mrs. Peacock killed the policeman.",
    );
    story_elements.insert(
        ("mr-boddy", "dead-mr-boddy"),
        "Mr. Boddy's body is found in the hall beaten to death with a candlestick.",
    );
    story_elements.insert(
        ("dead-mr-body", "guilty-plum"),
        "Mr. Plum killed Mr. Boddy thinking he was the real blackmailer.",
    );
    story_elements.insert(
        ("dead-mr-body", "guilty-scarlet"),
        "Miss Scarlet killed Mr. Boddy to keep him quiet.",
    );
    story_elements.insert(
        ("dead-mr-body", "guilty-peacock"),
        "Mrs. Peacock killed Mr. Boddy.",
    );
    story_elements.insert(
        ("cook", "dead-cook"),
        "The cook is found stabbed in the kitchen.",
    );
    story_elements.insert(
        ("dead-cook", "guilty-scarlet"),
        "Miss Scarlet killed the cook to silence her.",
    );
    story_elements.insert(
        ("dead-cook", "guilty-peacock"),
        "Mrs. Peacock killed her cook, who used to work for her.",
    );
    story_elements.insert(
        ("yvette", "dead-yvette"),
        "Yvette, the maid, is found strangled with the rope in the billiard room.",
    );
    story_elements.insert(
        ("dead-yvette", "guilty-scarlet"),
        "Miss Scarlet killed her old employee, Yvette.",
    );
    story_elements.insert(
        ("dead-yvette", "guilty-peacock"),
        "Mrs. Peacock killed Yvette.",
    );
    story_elements.insert(
        ("dead-yvette", "guilty-white"),
        "Mrs. White killed Yvette, who had an affair with her husband.",
    );
    story_elements.insert(
        ("wadsworth", "dead-wadsworth"),
        "Wadsworth is found shot dead in the hall.",
    );
    story_elements.insert(
        ("dead-wadsworth", "guilty-green"),
        "Mr. Green, an undercover FBI agent, shot Wadsworth.",
    );
    story_elements.insert(
        ("dead-telegram-girl", "guilty-green"),
        "Mr. Green, an undercover FBI agent, shot the telegram girl by accident.",
    );

    // Construct an empty database
    // and add some facts about the world.
    let mut db = Database::new();
    for &(a, b) in story_elements.keys() {
        db_facts! {
            db {
                ploto(a, b);
            }
        }
    }

    // Share database
    let db = Arc::new(db);

    let start_state = list![
        "maybe-telegram-girl",
        "maybe-motorist",
        "wadsworth",
        "mr-boddy",
        "cook",
        "yvette"
    ];

    let res = run!(*, (s, a), actiono(&db, start_state.clone(), s, a));
    println!("{:?}", res);

    let res = run!(*, (s, a), actiono(&db, list!["motorist"], s, a));
    println!("{:?}", res);

    let res = run!(
        q,
        storyo(
            db.clone(),
            start_state,
            Arc::new(vec![
                //"dead-wadsworth".into(),
                //"policeman".into(),
                "guilty-green".into()
            ]),
            q
        )
    );
    for s in res {
        if story_valid(&s) && story_len(&s) > 1 {
            print_story(&s, &story_elements);
        }
    }
}

fn actiono(
    db: &Arc<Database>,
    state: Value,
    new_state: impl Into<Value>,
    action: impl Into<Value>,
) -> impl Goal<Substitution<'static>> {
    fresh! {(inp, out, temp),
        membero(inp, state.clone()),
        ploto(db, inp, out),
        rembero(inp, state, temp),
        conso(out, temp, new_state.into()),
        eq((inp, out), action.into()),
    }
}

fn storyo(
    db: Arc<Database>,
    start_state: impl Into<Value>,
    end_elems: Arc<Vec<Value>>,
    actions: impl Into<Value>,
) -> impl Goal<Substitution<'static>> {
    let start_state = start_state.into();
    let actions = actions.into();
    let action = Var::new("action");
    let new_state = Var::new("new-state");
    let new_actions = Var::new("new-actions");
    conj! {
        actiono(&db, start_state, new_state, action),
        conso(action, new_actions, actions),
        conda! {
            everyg({
                let new_state = new_state.clone();
                move |x| membero(x.clone(), new_state)}, end_elems.iter()
            ),
            eq(new_actions, ());

            move |s| storyo(db.clone(), new_state, end_elems.clone(), new_actions).apply(s);
        }
    }
}

fn print_story(actions: &Value, story_elements: &HashMap<(&str, &str), &str>) {
    println!("PLOT SUMMARY:");

    for_each(&actions, |action| {
        let p = action.downcast_ref::<Pair>().unwrap().clone();
        let a = *p.first.downcast_ref::<&str>().unwrap();
        let b = *p.second.downcast_ref::<&str>().unwrap();
        println!("{}", story_elements[&(a, b)])
    });

    println!();
}

fn story_len(actions: &Value) -> usize {
    let mut n = 0;

    for_each(&actions, |_| {
        n += 1;
    });

    n
}

fn story_valid(mut actions: &Value) -> bool {
    while let Some(p) = actions.downcast_ref::<Pair>() {
        actions = &p.second;
    }

    actions.downcast_ref::<()>().is_some()
}
