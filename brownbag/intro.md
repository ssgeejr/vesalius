# Introduction: A Different Way to Build Software

Welcome.

This series is not a coding class. You will not be memorizing syntax, reading documentation, or debugging stack traces. That is the AI's job.

Your job is to tell it what you want.

---

## What We're Actually Doing

You are going to use an AI agent — Codex, or a similar tool — to build a working Python script. That script will connect to Freshdesk and create a support ticket.

You will do this through conversation. You describe what you want. The AI writes it. You look at what it produced, tell it what to change, and it tries again.

That loop — **describe, review, direct** — is the skill this series teaches.

---

## Why Does This Matter?

AI tools can already write functional code from a plain-English description. That means the bottleneck is no longer "can someone type the code" — it's "can someone clearly describe the problem and evaluate the result."

That is a skill you already have most of. This series helps you apply it to software.

---

## What You Will Build

A Python script that:

1. Reads your Freshdesk credentials from a config file on your computer
2. Connects to the Freshdesk API
3. Creates a new support ticket

You will not write a single line of Python. The AI will. Your job is to direct it clearly enough that what it produces actually works.

---

## How the AI Agent Works

Think of it like this:

You are the architect. The AI is the crew. You describe the building — what rooms it has, what it's for, what it should look like. The crew builds it. You walk through it, point at things that are wrong, and they fix it.

You don't need to know how to mix cement. You need to know what a good building looks like.

---

## Before You Continue

Make sure you have completed the [Pre-Development setup](../docs/PRE_DEV.md). You will need:

- Git, Python 3, and pip3 installed
- PyCharm Community or Notepad++ for viewing files
- Codex (or another AI agent) open and ready
- Your `~\.freshdesk\api.key` file created and filled in

Once that's done, move on to [Step 1: Your First Conversation With the AI](step1.md).
