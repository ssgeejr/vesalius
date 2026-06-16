# Step 1: Your First Conversation With the AI

Before we touch anything Freshdesk-related, let's get comfortable with the loop: **describe → review → direct.**

We'll start with something small and safe — asking the AI to create a simple file.

---

## Open Your AI Agent

Launch Codex (or whichever AI agent your team is using). You should see a chat-style interface where you can type instructions.

This is your primary tool for the rest of the series. Everything you build, you build through here.

---

## Your First Instruction

Type the following into the agent — word for word to start, then we'll talk about why it works:

```
Create a new file called hello.py in the current project folder.
It should print the message: "Freshdesk agent is ready."
Run it and show me the output.
```

Hit enter and watch what happens.

---

## What to Look For

The agent will probably:

1. Show you the code it's about to write
2. Create the file
3. Run it
4. Show you the output

You should see something like:

```
Freshdesk agent is ready.
```

If you do — great. If not, that's also fine. Read whatever error the AI shows you, and move to the next section.

---

## If Something Went Wrong

Don't fix it yourself. Tell the AI what happened:

```
That didn't work. Here's what I saw: [paste the error]
Fix it.
```

That's it. Let it try again. This is normal. This is part of the process.

---

## Why This Matters

You just completed the core loop:

1. You gave an instruction
2. The AI produced something
3. You evaluated the result
4. (If needed) you gave feedback

Every step in this series uses that same loop. The instructions get more specific. The outputs get more complex. The loop stays the same.

---

## Clean Up

Once it's working, tell the AI:

```
Delete hello.py — that was just a test.
```

Then move on to [Step 2: Reading a Config File](step2.md).
