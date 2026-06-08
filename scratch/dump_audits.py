import sqlite3

def dump():
    conn = sqlite3.connect('data/security.db')
    c = conn.cursor()
    c.execute("select query, normal_response, counterfactual_response, divergence, judgment_divergence from counterfactual_audits")
    for row in c.fetchall():
        print("="*60)
        print(f"QUERY: {row[0]}")
        print(f"DIV: {row[3]:.4f} | JUDG_DIV: {row[4]}")
        print("-"*30)
        print(f"NORMAL RESPONSE:\n{row[1]}")
        print("-"*30)
        print(f"COUNTERFACTUAL RESPONSE:\n{row[2]}")
    conn.close()

if __name__ == "__main__":
    dump()
