import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "assets", "data")
OUT = os.path.join(BASE, "supabase", "seed_data.sql")


def esc(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def pg_array(items):
    return "ARRAY[" + ",".join(esc(i) for i in items) + "]::text[]"


def bool_lit(b):
    return "true" if b else "false"


def num_or_null(v):
    return "NULL" if v is None else str(v)


def main():
    with open(os.path.join(DATA, "posts.json"), encoding="utf-8") as f:
        posts = json.load(f)
    with open(os.path.join(DATA, "rankings.json"), encoding="utf-8") as f:
        rankings = json.load(f)
    with open(os.path.join(DATA, "ticker.json"), encoding="utf-8") as f:
        ticker = json.load(f)

    lines = ["-- 자동 생성된 시드 데이터 (generate_seed.py)", ""]

    lines.append("truncate table posts, rankings, ticker_items restart identity;")
    lines.append("")

    lines.append("insert into posts (id, category, category_label, tag, title, excerpt, content, icon, video, duration, views, comments, date, popular, rank) values")
    row_sqls = []
    for p in posts:
        row_sqls.append(
            "(" + ", ".join([
                esc(p["id"]),
                esc(p["category"]),
                esc(p["categoryLabel"]),
                esc(p["tag"]),
                esc(p["title"]),
                esc(p["excerpt"]),
                pg_array(p["content"]),
                esc(p["icon"]),
                bool_lit(p["video"]),
                esc(p["duration"]),
                str(p["views"]),
                str(p["comments"]),
                esc(p["date"]),
                bool_lit(p["popular"]),
                num_or_null(p["rank"]),
            ]) + ")"
        )
    lines.append(",\n".join(row_sqls) + ";")
    lines.append("")

    lines.append("insert into rankings (rank, name, subs, delta, category) values")
    row_sqls = []
    for r in rankings:
        row_sqls.append(
            "(" + ", ".join([
                str(r["rank"]),
                esc(r["name"]),
                esc(r["subs"]),
                str(r["delta"]),
                esc(r["category"]),
            ]) + ")"
        )
    lines.append(",\n".join(row_sqls) + ";")
    lines.append("")

    lines.append("insert into ticker_items (label, text, sort_order) values")
    row_sqls = []
    for i, t in enumerate(ticker):
        row_sqls.append(
            "(" + ", ".join([esc(t["label"]), esc(t["text"]), str(i)]) + ")"
        )
    lines.append(",\n".join(row_sqls) + ";")
    lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("wrote", OUT)


if __name__ == "__main__":
    main()
