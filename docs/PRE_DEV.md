# Pre-Development: Zero to Ready

Welcome. This guide walks you through setting up everything you need to start building with AI-assisted development in this project.

If you know your way around Windows and have used developer tools before, this will take you about 20–30 minutes.

---

## 1. Install Git

Git tracks every change you make. It also gives Codex the ability to branch, commit, and push your work.

1. Download Git for Windows from [git-scm.com](https://git-scm.com/download/win).
2. Run the installer — accept all defaults.
3. Open **Command Prompt** or **PowerShell** and verify:

```powershell
git --version
```

You should see something like `git version 2.xx.x.windows.x`.

---

## 2. Install Python 3

Python powers the scripts and agents you will build.

1. Download Python from [python.org/downloads](https://www.python.org/downloads/). Grab the latest 3.x release for Windows.
2. Run the installer. **Check the box "Add Python to PATH"** before clicking Install.
3. After installation, open a new terminal and verify:

```powershell
python3 --version
pip3 --version
```

Both should return version numbers. If `python3` doesn't work, try `python`.

---

## 3. Generate an SSH Key

SSH keys let you authenticate with GitHub and other remote services without typing passwords.

```powershell
mkdir $home\.ssh
cd $home\.ssh
ssh-keygen -t ed25519 -C "your_email@example.com" -f aitutorial
```

- Press **Enter** to accept the default location (`C:\Users\<you>\.ssh\aitutorial`).
- Press **Enter** again for an empty passphrase, or type one if you prefer.

### Add the SSH Key to GitHub

Open the public key file in Notepad++:

```powershell
notepad++ $home\.ssh\aitutorial.pub
```

Select all, copy, then go to:

1. Open [github.com/settings/keys](https://github.com/settings/keys)
2. Click **New SSH key**
3. Give it a title like `aitutorial`
4. Paste the key into the **Key** field
5. Click **Add SSH key**

That's it — your machine is now authorized to push to your GitHub repos.

---

## 4. Install Notepad++

A fast, reliable text editor for quick edits, config tweaks, and reading code.

1. Download from [notepad-plus-plus.org](https://notepad-plus-plus.org/downloads/).
2. Run the installer — defaults are fine.

---

## 5. Install Tabby

Tabby is a self-hosted terminal that lets you run multiple terminal sessions inside a single window — think tabs and split panes, all persistent.

1. Download from [tabby.sh](https://tabby.sh/) (choose the Windows installer).
2. Run the installer — defaults are fine.
3. Launch Tabby. You can open new tabs (`Ctrl+T`), split panes (`Ctrl+\` or `Ctrl+|`), and manage sessions from the sidebar.

**Why it's useful:** instead of juggling several separate terminal windows, keep every shell — PowerShell, CMD, SSH sessions — organized in one place. Codex commands work perfectly inside Tabby.

---

## 6. Install PyCharm Community

JetBrains PyCharm Community Edition is a full IDE for Python development.

1. Download from [jetbrains.com/pycharm/download](https://www.jetbrains.com/pycharm/download/).
2. Run the installer — accept the defaults.
3. On first launch, you can skip the import wizard.

**Quick tip:** PyCharm bundles `python` and `pip`, but this guide uses the system Python installed in Step 2. In PyCharm, go to **File → Settings → Project → Python Interpreter** and point it to your system Python if you want them to share packages.

---

## 7. Install ChatGPT Codex for Windows

Codex is the AI agent you will work with. It runs inside the Codex desktop app and connects to ChatGPT's models.

1. Download the Codex desktop app from the OpenAI website or your organization's portal.
2. Run the installer and sign in with your OpenAI account.
3. The app opens to a chat window — you're ready to start building.

**What Codex can do:** run terminal commands, edit files, manage git repositories, and respond to instructions like a pair programmer. Think of it as an AI colleague who types alongside you.

---

## 8. Verify Everything

Run these commands in a single terminal session to confirm all tools are ready:

```powershell
git --version
python3 --version
pip3 --version
notepad++ --version
where pycharm
ssh -V
```

No errors? You're ready.

---

## 8. Configure Your Freshdesk Credentials

The Python scripts in this project read your Freshdesk credentials from a config file in your home directory. This keeps secrets off of disk inside the project folder and out of version control.

Open PowerShell and run the following to create the folder and file:

```powershell
New-Item -ItemType Directory -Path "$HOME\.freshdesk" -Force
New-Item -ItemType File -Path "$HOME\.freshdesk\api.key" -Force
notepad++ "$HOME\.freshdesk\api.key"
```

Notepad++ will open the file. Paste in the following and fill in your values:

```
api_key:
domain:
email:
agent_id:
location:
group_id:
dept_id:
resp_id:
contact_nbr:
```

| Field | What to put here |
|-------|-----------------|
| `api_key` | Your Freshdesk API key (found under your profile → API Key) |
| `domain` | Your Freshdesk subdomain (e.g. `acme` from `acme.freshservice.com`) |
| `email` | The agent email address used to log in |
| `agent_id` | Your numeric agent ID (returned by the `/agents/me` endpoint) |
| `location` | The custom location field value for new tickets |
| `group_id` | Numeric ID of the group tickets are assigned to |
| `dept_id` | Numeric ID of your department |
| `resp_id` | Numeric agent ID of the default responder |
| `contact_nbr` | Contact number for the custom field on new tickets |

Save and close the file. The scripts will read this file at runtime — you will never need to paste credentials into the code.

> **Security note:** This file lives outside the repository (`~\.freshdesk\`) and is never committed to GitHub. Do not move or copy it into the project folder.

---

## Next Steps

Fork this repository to your own GitHub account so you have a clean copy to work in.

1. Go to [github.com/ssgeejr/vesalius](https://github.com/ssgeejr/vesalius)
2. Click the **Fork** button (top-right)
3. Choose your personal account as the owner and click **Create fork**

Once your fork is ready, clone it locally:

```powershell
git clone git@github.com:<your-username>/vesalius.git
cd vesalius
```

Open it in Codex and we will start with the `AGENTS.md` file.

Happy building.
