# Virus Remover

> *some old shit i wrote in python cause i was bored.*

## Overview

This is a **very lw remover** written in Python.

This is **not** a full antivirus, does **not** use signatures like commercial AVs, and does **not** run in the background. It’s just a manual cleanup tool you run when you want to nuke obvious garbage.

## What It Does

* Scans commonly abused directories (temp folders, startup locations, user app data, etc.) inside of luckyware
* Looks for known luckyware files
* Can remove common trojans
* Runs fast and doesn’t hook anything or stay resident

## Why This Exists

* I was bored
* I wanted something small and readable
* I didn’t want bloated AV software
* I wanted a quick "remove luckware" button
* It was a learning project

That’s it.

## Requirements

* Python 3.11.x
* Windows (this was written with Windows paths in mind)
* Administrator privileges **required** for full cleanup

## Usage

Run it like any normal Python script:

```
python main.py
```

## Code Quality Warning

This is:

* Old code
* Not optimized
* Not pretty
* Not production-grade

It works well enough for what it was meant to do.

## License

Do whatever you want with it.
Modify it, improve it, or laugh at it.
