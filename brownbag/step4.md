# Step 4: Creating a Ticket

This is the main event. Everything we've built — the config loader, the connection check — leads here.

---

## What We're Building

A script that takes input from the user (subject and description), then creates a real ticket in Freshdesk with the correct group, department, responder, and custom fields — all pulled from your config file.

---

## Your Instruction to the AI

```
Write a Python script called create_ticket.py.

It should:
- Import the config loader from config.py
- Prompt the user to enter a ticket subject
- Prompt the user to enter a ticket description
- Make a POST request to https://{domain}.freshservice.com/api/v2/tickets
- Authenticate with api_key using Basic Auth (password is X)
- Send the following fields in the request body as JSON:
    subject: (from user input)
    description: (from user input)
    email: (from config)
    status: 2
    source: 3
    priority: 2
    impact: 1
    urgency: 1
    group_id: (from config)
    responder_id: (from config, field name is resp_id)
    department_id: (from config, field name is dept_id)
    custom_fields:
        location: (from config)
        contact_number: (from config, field name is contact_nbr)

- If the ticket is created successfully, print: "Ticket created. ID: " followed by the ticket ID
- If it fails, print the status code and the error message
```

---

## Run It

The AI will create the script and likely offer to run it. Let it. Enter a test subject and description when prompted — something you can find and close in Freshdesk afterward.

If it works, log into Freshdesk and confirm the ticket actually appeared.

---

## What to Verify in Freshdesk

Open the ticket and check:

- Subject and description match what you entered
- It's assigned to the correct group and responder
- The department is correct
- The location and contact number custom fields are populated

If anything is off, come back and tell the AI specifically what's wrong:

```
The ticket was created but the group_id is wrong — it's showing group 0 instead of my group.
The group_id in my config is 12345. Fix the script.
```

---

## If the Request Fails

**422 Unprocessable Entity** — one or more fields are invalid. Ask the AI:
```
I got a 422 error. Print the full response body so I can see which field is wrong.
```

**403 Forbidden** — your API key may not have permission to create tickets. Check with your Freshdesk administrator.

**workspace_id error** — some Freshdesk instances require a workspace_id. If you see this, tell the AI:
```
Add workspace_id: 2 to the request body.
```

---

## Making It Better

Once the basic version works, try these follow-up instructions one at a time:

```
After creating the ticket, print a direct URL to view it in Freshdesk.
```

```
If the user leaves the subject or description blank, prompt them again instead of submitting an empty ticket.
```

```
Add a --dry-run flag. When passed, print what would be sent to the API without actually creating the ticket.
```

Each of these is a small, specific improvement. That's how real software gets built.

---

## What You Just Did

You directed an AI to build a working integration with an external API. You gave it the spec, watched it produce the code, verified the output against a real system, and iterated when something was off.

That is the skill.

Move on to [Step 5: Putting It All Together](step5.md).
