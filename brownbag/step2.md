# Step 2: Reading a Config File

The script we're building will need your Freshdesk credentials — API key, domain, email, and so on. Those are stored in `~\.freshdesk\api.key`.

In this step, you'll ask the AI to write code that reads that file and confirms it can find your credentials.

---

## Why a Config File?

Credentials don't belong in code. If your script has `api_key = "abc123"` written directly into it, that key ends up in your git history, your backups, anywhere the file travels. A separate config file outside the project folder keeps secrets where they belong — on your machine, not in the code.

You already created `~\.freshdesk\api.key` during setup. Now we put it to use.

---

## Your Instruction to the AI

```
Write a Python script called config.py in the project root.

It should:
- Open the file at C:\Users\<your-username>\.freshdesk\api.key
- Read each line and parse it as a key: value pair
- Store the values in a dictionary
- Print each key and its value to confirm they loaded correctly

Use Python's built-in file handling — no external libraries for this step.
```

Replace `<your-username>` with your actual Windows username before sending.

---

## Review the Output

The AI will write the script and probably run it. Look at what it prints. You should see something like:

```
api_key: ****loaded****
domain: your-domain
email: you@company.com
...
```

(The AI may mask the api_key value for security — that's good behavior.)

---

## Things to Check

- Did it find the file? If not, the path is probably wrong. Tell the AI: `The file path is wrong — my username is [x]. Fix it.`
- Did all nine fields load? If any are missing, check your `api.key` file to make sure they're filled in.
- Did it crash? Paste the error to the AI and ask it to fix it.

---

## Making It Better

Once it's working, try this follow-up instruction:

```
If any required field is missing or empty, print a clear error message telling the user which field is missing. 
Don't crash — just warn and exit cleanly.
```

This is a good habit: always ask the AI to handle the case where something is wrong. Real tools need to fail gracefully.

---

## What You Just Did

You asked the AI to write a utility that your main script will depend on. You reviewed it, tested it, and improved it — all without writing a line of code.

That config loader will be reused in the next step.

Move on to [Step 3: Connecting to Freshdesk](step3.md).
