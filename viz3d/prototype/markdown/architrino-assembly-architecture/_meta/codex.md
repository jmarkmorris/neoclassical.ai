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

That’s the rule.

No UI. No status command. No toggle.

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

Now remove it permanently.

Edit your shell config:

```bash
nano ~/.zshrc
```

Find and delete any line like:

```bash
export OPENAI_API_KEY=sk-...
```

Save, then reload:

```bash
source ~/.zshrc
```

Verify:

```bash
echo $OPENAI_API_KEY
```

Should print nothing.

---

### Step 2 — Clear old Codex credentials (optional but recommended)

This avoids stale auth confusion.

```bash
rm -f ~/.codex/auth.json
```

(or `auth.toml` if that exists)

---

### Step 3 — Log in via browser

Now authenticate to ChatGPT:

```bash
codex login
```

Browser opens → sign in → approve.

This binds Codex to your Plus/Pro account.

---

### Step 4 — Test

Run something simple:

```bash
codex "print hello world in python"
```

Then check your OpenAI API dashboard.

If no usage appears → you’re on Plus/Pro.

---

### Result

Now:

* No API key
* Using subscription
* 5.3 access works

---

# II. Switch FROM Plus/Pro → TO API Key

Goal: Force Codex to bill your API account.

### Step 1 — Set API key in shell

Temporary (session only):

```bash
export OPENAI_API_KEY="sk-xxxxxxxx"
```

Permanent:

```bash
nano ~/.zshrc
```

Add:

```bash
export OPENAI_API_KEY="sk-xxxxxxxx"
```

Reload:

```bash
source ~/.zshrc
```

Verify:

```bash
echo $OPENAI_API_KEY
```

Should show your key.

---

### Step 2 — (Optional) Remove browser login

Not strictly required, but cleaner.

```bash
rm -f ~/.codex/auth.json
```

Codex will ignore OAuth once key exists anyway.

---

### Step 3 — Test

Run:

```bash
codex "print hello world in python"
```

Check API dashboard → you’ll see usage.

---

### Result

Now:

* API key present
* Subscription ignored
* Usage billed per token

---

# III. The Only Rule You Need to Remember

> If `OPENAI_API_KEY` exists → API mode
> If it does NOT exist → Plus/Pro mode

That’s it.

Everything else is noise.

---

# IV. Recommended Workflow (Power User)

Since you actively use both, do this:

### Create two helper scripts

#### `use_api.sh`

```bash
export OPENAI_API_KEY="sk-xxxxxxxx"
echo "Codex now using API"
```

#### `use_plus.sh`

```bash
unset OPENAI_API_KEY
echo "Codex now using Plus/Pro"
```

Make executable:

```bash
chmod +x use_api.sh use_plus.sh
```

Then switch instantly:

```bash
./use_api.sh
./use_plus.sh
```

No editing files. No confusion.

---

# Bottom Line

There is no “setting.”

There is no “mode.”

There is only:

* Environment variable → API
* No variable → Plan

Once you internalize that, this stops being mysterious.

---

If you want, I can next help you set this up so different terminals automatically default to different modes.
