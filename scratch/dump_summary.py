import sqlite3

def dump():
    conn = sqlite3.connect('data/security.db')
    c = conn.cursor()
    c.execute("select query, divergence, judgment_divergence from counterfactual_audits")
    rows = c.fetchall()
    print(f"{'Query':<60} | {'Divergence':<10} | {'Judg Div':<8}")
    print("-" * 83)
    for row in rows:
        # truncate query to fit
        query = row[0][:57] + "..." if len(row[0]) > 57 else row[0]
        print(f"{query:<60} | {row[1]:<10.4f} | {row[2]:<8}")
    conn.close()

if __name__ == "__main__":
    dump()
