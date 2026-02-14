## 20260212 - new codex available

  - Codex is now powered by gpt-5.3-codex, our most capable agentic coding model yet. 
  - It's built for 
    - long-running, 
    - project-scale work, 
    - with mid-turn steering
    - frequent progress updates 
    - collaborate while it runs 
    - (and it's faster too).


## 20260214 - Trouble using 5.3 leads to api vs. plan usage instructions.

The situation is confusing because the Codex CLI does **not** expose a clean “mode switch”. Let’s strip this down to what actually works in practice.

There are **only two real selectors**:

1. Environment variable `OPENAI_API_KEY`
2. Whether you are logged in via browser (`codex login`)

And **environment variables win**.

If a key is present, Codex uses the API. Period.

If no key is present, Codex falls back to your ChatGPT Plus/Pro login.


---

# I. Switch FROM API Key → TO Plus/Pro Plan

Goal: Make Codex ignore the API key and use your ChatGPT subscription.

### Step 1 — Remove the API key from your shell

Check first:

```bash
echo $OPENAI_API_KEY
```

If you see anything → it’s active.

Disable it (current session):

```bash
unset OPENAI_API_KEY
```

---

### Step 2 — Save chat history and then Clear old Codex credentials

```bash
cp -r ~/.codex/sessions ~/codex_backup_sessions
```

This avoids stale auth confusion.

```bash
rm -f ~/.codex
```

---

### Step 3 — Log in via browser

Now authenticate to ChatGPT:

```bash
codex login
```

Browser opens → sign in → approve.

This binds Codex to your Plus/Pro account.

---

### Result

Now:

* No API key
* Using subscription
* 5.3 access works

---

