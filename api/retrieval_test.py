"""30-question retrieval test for /search.

Run from the api/ folder:  python retrieval_test.py

It calls the same functions /search uses (no server needed).
hit@1 = the right file is the top result. hit@4 = the right file is in the top 4.
Questions with expected = None are out of scope: we only look at the top similarity.
"""
import time

from main import embed_query, search_chunks

TOP_K = 4

# (question, [acceptable files], note)
TESTS = [
    # Academic Affairs
    ("What is the minimum attendance I need?", ["academic_policies.md"]),
    ("What GPA puts me on academic probation?", ["academic_policies.md"]),
    ("When is the course enrollment period?", ["course_enrollment.md"]),
    ("How many credit hours can I take in a semester?", ["course_enrollment.md"]),
    ("When are the midterm exams?", ["exams.md"]),
    ("How fast must I report a problem that happened during an exam?", ["exams.md"]),
    # Finance
    ("When is the first fee installment due?", ["fee_deadlines.md"]),
    ("How much is the late fee?", ["fee_deadlines.md"]),
    ("How long does a card payment take to show up?", ["fee_payment.md"]),
    ("My payment failed, what should I do?", ["fee_payment.md"]),
    ("Do I get a refund if I withdraw early?", ["refunds.md"]),
    ("How long does a refund take after approval?", ["refunds.md"]),
    # IT Support
    ("How long is the password reset link valid?", ["password_reset.md"]),
    ("How do I reset my forgotten password?", ["password_reset.md"]),
    ("Which browsers does the portal support?", ["portal_login.md"]),
    ("When is the portal down for maintenance?", ["portal_login.md"]),
    ("What is the maximum file size I can upload?", ["technical_support.md"]),
    ("Which file types can I upload?", ["technical_support.md"]),
    # Student Services
    ("How much does an enrollment certificate cost?", ["certificates.md"]),
    ("How long does a transcript take?", ["certificates.md"]),
    ("How do I update my phone number?", ["student_records.md"]),
    ("How do I correct a spelling mistake in my name?", ["student_records.md"]),
    ("How quickly will someone reply to my request?", ["general_support.md"]),
    ("Can the copilot approve an exception for me?", ["general_support.md"]),
    # Cross-topic (either file is acceptable)
    ("I paid my fee twice, what now?", ["fee_payment.md", "refunds.md"]),
    ("The portal crashed during my exam", ["technical_support.md", "exams.md"]),
    ("Who handles grade appeals?", ["academic_policies.md", "general_support.md"]),
    ("I need a document that proves my fees are paid", ["certificates.md"]),
    # Out of scope (no good answer exists in the knowledge base)
    ("What is on the cafeteria menu today?", None),
    ("Can I get a hostel room?", None),
]


def main() -> None:
    hit1 = hit4 = scored = 0
    in_scope_top: list[float] = []
    out_scope_top: list[float] = []

    for i, (question, expected) in enumerate(TESTS, 1):
        rows = search_chunks(embed_query(question), TOP_K, None)
        files = [r["source_file"].split("/")[-1] for r in rows]
        top_sim = rows[0]["similarity"] if rows else 0.0

        if expected is None:
            out_scope_top.append(top_sim)
            print(f"{i:>2}. OUT-OF-SCOPE top={files[0]} sim={top_sim:.2f} | {question}")
        else:
            scored += 1
            ok1 = files[0] in expected
            ok4 = any(f in expected for f in files)
            hit1 += ok1
            hit4 += ok4
            in_scope_top.append(top_sim)
            tag = "PASS" if ok1 else ("TOP4" if ok4 else "FAIL")
            print(f"{i:>2}. {tag} top={files[0]} sim={top_sim:.2f} | {question}")
        time.sleep(0.3)

    print()
    print(f"hit@1: {hit1}/{scored}")
    print(f"hit@4: {hit4}/{scored}")
    if in_scope_top:
        print(f"in-scope top similarity: min {min(in_scope_top):.2f}, "
              f"avg {sum(in_scope_top) / len(in_scope_top):.2f}")
    if out_scope_top:
        print(f"out-of-scope top similarity: max {max(out_scope_top):.2f}")


if __name__ == "__main__":
    main()