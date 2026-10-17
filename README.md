# ducky-reddit

A single-user command-line helper for my own Reddit account (u/UnluckyDuckyDuck).
It runs locally on my Mac, authenticates with Reddit's script OAuth flow as my own
account only, and is triggered by hand. It has no other users and is not installed
in any subreddit.

It does three things, and nothing else:

| Command | What it does | Endpoint |
|---|---|---|
| `post` | Submits a post I wrote myself (title, body, subreddit, flair) | `POST /api/submit` |
| `history` | Lists my own submissions so I can respect each subreddit's posting cadence | `GET /user/<me>/submitted` |
| `inbox` | Shows my unread comment replies and messages so I can answer people promptly | `GET /message/unread` |

It does **not** read or store data about other users, comment or vote automatically,
monitor keywords, crawl subreddits, or send anything I have not written and reviewed.
Expected volume is under 100 requests per day.

## Setup

```
cp .env.example .env   # fill in client id, secret, username, password
python3 ducky.py history
python3 ducky.py inbox
python3 ducky.py post macapps "Title" --text-file post.md --flair "Promo"
```
