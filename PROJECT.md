# PROJECT.md

## Goal

Equip an IT team with a practical, repeatable skill: using an AI agent to create and edit software, files, and documentation — without writing code by hand.

## The Skill You Are Building

Directing an AI is a skill. Like any skill, it improves with practice. This project gives you a real task to practice on — a Python tool that connects to Freshdesk and creates tickets — so you learn by doing, not by reading about it.

By the end you will know how to:

- Give an AI clear, specific instructions
- Read and evaluate what it produces
- Push back when something is wrong
- Build iteratively — one small piece at a time

## How It Works

You provide the intent. The AI provides the implementation.

| You do | The AI does |
|--------|------------|
| Describe what you want | Write the code |
| Review the output | Edit and refactor |
| Give feedback | Fix what's wrong |
| Run and verify | Debug and retry |
| Ask questions | Explain its decisions |

You are not learning to code. You are learning to **direct** a coding agent. That is a different skill — and one that every IT professional will need.

## What Gets Built

A Python script that:

- Reads your Freshdesk credentials from `~\.freshdesk\api.key`
- Connects to the Freshdesk API
- Creates a new support ticket

The script is built entirely through conversation with the AI. You describe what you want, step by step, and the AI writes it.

## Working With the AI Effectively

- **Be specific.** "Create a ticket with subject 'Test' assigned to group 12345" beats "make a ticket."
- **Be iterative.** One request at a time. Review, then ask for the next thing.
- **Push back.** If it looks wrong, say so. The AI will try again.
- **Ask why.** "Why did you structure it that way?" is always a valid question.
- **Read the output.** You don't need to understand every line — but you should understand what it does.

## Reference Materials

- [Pre-Development Setup](docs/PRE_DEV.md)
- [Brown Bag Tutorial](brownbag.md)
- [Freshdesk API Examples](freshdesk/api.example.txt)
- [Agent Instructions](AGENTS.md)
