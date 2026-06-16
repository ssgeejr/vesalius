# Step 3: Connecting to Freshdesk

You have a config loader. Now let's use it — make a real API call to Freshdesk and confirm your credentials work.

---

## What We're Testing

Before we create anything, we want to verify the connection. The Freshdesk API has an endpoint that returns information about the currently authenticated agent — basically "who am I?" — and it's a clean, read-only way to confirm the API key and domain are correct.

---

## Your Instruction to the AI

```
Write a Python script called verify_connection.py.

It should:
- Import the config loader from config.py to get api_key and domain
- Make a GET request to https://{domain}.freshservice.com/api/v2/agents/me
- Authenticate using the api_key with HTTP Basic Auth (username is the api_key, password is the letter X)
- If the response is successful, print: "Connected. Logged in as: " followed by the agent's name and email
- If the response fails, print the status code and the error message from the API

Use the requests library for the HTTP call.
```

---

## Run It

Ask the AI to run it. If your credentials are correct, you'll see something like:

```
Connected. Logged in as: Jane Smith (jane@company.com)
```

That means you have a live, authenticated connection to your Freshdesk instance.

---

## If It Fails

Common problems and what to tell the AI:

**401 Unauthorized**
```
I got a 401 error. The api_key in my config file is correct. 
Check that the Basic Auth header is formatted correctly.
```

**Connection error / DNS failure**
```
I got a connection error. My domain in the config file is "acme" — 
the full URL should be acme.freshservice.com. Make sure the URL is built correctly.
```

**requests is not installed**
```
I got a ModuleNotFoundError for requests. Install it with pip and try again.
```

---

## A Note on the requests Library

`requests` is not part of Python's standard library — it needs to be installed. If the AI didn't handle this already, ask it:

```
Add a requirements.txt file to the project that lists every library the scripts depend on.
```

That file makes it easy for anyone to install the dependencies later with one command.

---

## What You Just Did

You made a real, authenticated API call to an external service — by describing what you wanted. The AI handled the HTTP request, the authentication format, and the error handling.

Next we build on this to actually create a ticket.

Move on to [Step 4: Creating a Ticket](step4.md).
