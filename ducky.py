#!/usr/bin/env python3
"""ducky-reddit: a single-user helper for my own Reddit account.

Commands:
  history            list my own recent submissions (date, subreddit, title)
  inbox              list my unread replies and messages
  post SUB TITLE     submit a self post I wrote; body from --text-file, optional --flair

Credentials come from .env (script-type OAuth app, own account only).
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://oauth.reddit.com"

def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    env.update({k: v for k, v in os.environ.items() if k.startswith("REDDIT_")})
    return env

class Client:
    def __init__(self, env):
        self.user = env["REDDIT_USERNAME"]
        self.ua = f"macos:ducky-reddit:1.0 (by /u/{self.user})"
        auth = f"{env['REDDIT_CLIENT_ID']}:{env['REDDIT_CLIENT_SECRET']}".encode()
        import base64
        body = urllib.parse.urlencode({"grant_type": "password", "username": self.user,
                                       "password": env["REDDIT_PASSWORD"]}).encode()
        req = urllib.request.Request("https://www.reddit.com/api/v1/access_token", data=body,
                                     headers={"User-Agent": self.ua,
                                              "Authorization": "Basic " + base64.b64encode(auth).decode()})
        with urllib.request.urlopen(req) as r:
            self.token = json.load(r)["access_token"]

    def call(self, method, path, data=None):
        body = urllib.parse.urlencode(data).encode() if data else None
        req = urllib.request.Request(API + path, data=body, method=method,
                                     headers={"User-Agent": self.ua, "Authorization": f"bearer {self.token}"})
        with urllib.request.urlopen(req) as r:
            remaining = r.headers.get("x-ratelimit-remaining")
            if remaining and float(remaining) < 5:
                time.sleep(float(r.headers.get("x-ratelimit-reset", 60)))
            return json.load(r)

def cmd_history(c, args):
    data = c.call("GET", f"/user/{c.user}/submitted?limit={args.limit}&raw_json=1")
    for child in data["data"]["children"]:
        p = child["data"]
        day = datetime.fromtimestamp(p["created_utc"], timezone.utc).date()
        print(f"{day}  r/{p['subreddit']:<20} {p['title'][:80]}")

def cmd_inbox(c, args):
    data = c.call("GET", "/message/unread?limit=50&raw_json=1")
    items = data["data"]["children"]
    if not items:
        print("No unread messages."); return
    for child in items:
        m = child["data"]
        kind = "reply" if m.get("was_comment") else "message"
        print(f"[{kind}] u/{m.get('author')} in r/{m.get('subreddit') or '-'}: {m.get('body','')[:200]}")
        if m.get("context"): print(f"   https://www.reddit.com{m['context']}")

def cmd_post(c, args):
    text = open(args.text_file).read() if args.text_file else ""
    payload = {"sr": args.subreddit, "kind": "self", "title": args.title, "text": text,
               "api_type": "json", "sendreplies": "true"}
    if args.flair:
        flairs = c.call("GET", f"/r/{args.subreddit}/api/link_flair_v2")
        match = [f for f in flairs if f["text"].lower() == args.flair.lower()]
        if not match:
            sys.exit(f"No flair named {args.flair!r}. Available: {[f['text'] for f in flairs]}")
        payload["flair_id"] = match[0]["id"]
    print(f"About to post to r/{args.subreddit}: {args.title}")
    if input("Type yes to submit: ").strip().lower() != "yes":
        sys.exit("Cancelled.")
    res = c.call("POST", "/api/submit", payload)
    errors = res.get("json", {}).get("errors")
    if errors: sys.exit(f"Reddit returned errors: {errors}")
    print("Posted:", res["json"]["data"]["url"])

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("history"); h.add_argument("--limit", type=int, default=100); h.set_defaults(fn=cmd_history)
    i = sub.add_parser("inbox"); i.set_defaults(fn=cmd_inbox)
    p = sub.add_parser("post"); p.add_argument("subreddit"); p.add_argument("title")
    p.add_argument("--text-file"); p.add_argument("--flair"); p.set_defaults(fn=cmd_post)
    args = ap.parse_args()
    env = load_env()
    missing = [k for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD") if not env.get(k)]
    if missing: sys.exit(f"Missing in .env: {', '.join(missing)}")
    args.fn(Client(env), args)

if __name__ == "__main__":
    main()
