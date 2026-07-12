// RULES-1 conformance driver (PROPOSED-ASM-1124): run sparq-reason's N3
// fixpoint (`reason_n3`) over each input document (facts + the compiled
// rules.n3 of WMRE-1 §3) and emit the closure as JSON lines:
//   {"file": "<path>", "triples": [["s","p","o"], ...]}   (sorted, IRIs only)
// The Python side (conformance.py) generates the documents and compares this
// closure term-for-term with the twin's Cl(S). Disclosure: this exercises the
// N3 fixpoint entry point, not the OwlRl materializer; the rules are the
// SAME compiled artifact both engines consume.
use sparq_core::dict::{Dict, TermParts};
use std::io::Write;

fn iri_of(d: &Dict, id: sparq_core::dict::Id) -> Option<String> {
    match d.term_parts(id) {
        TermParts::Iri { prefix, suffix } => Some(format!("{prefix}{suffix}")),
        _ => None,
    }
}

fn main() {
    let out = std::io::stdout();
    let mut out = out.lock();
    for path in std::env::args().skip(1) {
        let src = std::fs::read_to_string(&path)
            .unwrap_or_else(|e| panic!("ERR_READ {path}: {e}"));
        let mut dict = Dict::default();
        let ids = sparq_reason::reason_n3(&mut dict, &src)
            .unwrap_or_else(|e| panic!("ERR_REASON {path}: {e}"));
        let mut triples: Vec<[String; 3]> = ids
            .iter()
            .filter_map(|t| {
                Some([iri_of(&dict, t[0])?, iri_of(&dict, t[1])?,
                      iri_of(&dict, t[2])?])
            })
            .collect();
        triples.sort();
        triples.dedup();
        let rows: Vec<String> = triples
            .iter()
            .map(|t| format!("[{:?},{:?},{:?}]", t[0], t[1], t[2]))
            .collect();
        writeln!(out, "{{\"file\":{:?},\"triples\":[{}]}}", path,
                 rows.join(",")).unwrap();
    }
}
