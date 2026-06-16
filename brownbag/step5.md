# Step 5: Putting It All Together

You have three working scripts. Now ask the AI to combine them into one clean, runnable tool.

---

## Your Instruction to the AI

```
Combine config.py, verify_connection.py, and create_ticket.py into a single script called freshdesk.py.

It should:
- Load credentials from ~\.freshdesk\api.key on startup
- Verify the connection to Freshdesk before doing anything else
- If the connection fails, exit with a clear error message
- If the connection succeeds, prompt the user for a subject and description
- Create the ticket
- Print the result

Keep the code clean and add a comment above each section explaining what it does.
```

---

## Run the Final Script

Ask the AI to run `freshdesk.py`. Walk through the full flow:

1. Credentials load from your config file
2. Connection is verified
3. You enter a subject and description
4. Ticket is created
5. ID and confirmation are printed

If everything works end to end — you're done.

---

## Ask for a README

The tool works. Now document it.

```
Write a README for this project that explains:
- What the script does
- How to set up the ~\.freshdesk\api.key config file
- How to install dependencies
- How to run freshdesk.py

Keep it short. Assume the reader is an IT professional, not a developer.
```

Review what the AI writes. Edit it by talking to the AI — not by typing into the file yourself.

---

## Commit the Work

Ask the AI to commit everything to git:

```
Commit all the current files to git with the message:
"feat: working Freshdesk ticket creation script"
```

If you have a GitHub fork set up, ask it to push as well.

---

## Reflect

Look at what you built:

- A config loader that reads credentials from a secure location
- A connection verifier that fails gracefully
- A ticket creation tool with proper error handling
- Clean code with comments
- A README
- A git commit

You didn't write any of it. You directed someone who did.

---

## What's Next

This is a starting point, not a finished product. Some directions you could take it:

- Ask the AI to add a `--list` flag that shows your open tickets
- Ask it to accept input from a form instead of the command line
- Ask it to log every ticket creation to a file
- Ask it to run on a schedule and send you a daily summary

All of those are one conversation away.

---

[← Back to the Brown Bag Index](../brownbag.md)
