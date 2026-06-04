# Full-Stack SQL Injection (SQLi) Vulnerability & Mitigation Lab

This repository serves as an educational cybersecurity lab demonstrating the mechanics of SQL Injection (SQLi) vulnerabilities and how to properly secure web applications against them. The project features a dual-implementation backend showcasing both a vulnerable application environment and a patched, secure production-ready version.

## 🚀 Features & Learning Objectives

- **Vulnerable Environment:** Demonstrates how un-sanitized user input can lead to authentication bypasses (e.g., `' OR 1=1 --`) and unauthorized data extraction.
- **Exploit Verification:** Contains functional verification scripts (Bash/cURL and Python) simulating realistic `UNION`-based automated attacks.
- **Secure Mitigation:** Implements industry-standard defenses using parameterized queries and object-relational mapping (ORM) abstractions to neutralize structural query manipulation.

## 🛠️ Tech Stack & Security Tools

- **Backend:** Python 3.13, FastAPI, SQLAlchemy (ORM)
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Security Concepts:** Input Validation, Parameterized Queries, Proof-of-Concept (PoC) Exploit Scripting

## 📁 Repository Structure

- `/backend`: The initial implementation containing the structural flaws.
- `/fixes`: The hardened code utilizing secure database interaction patterns.
- `/exploits`: Automation scripts used to audit and verify the vulnerability state.

## 🔒 Disclaimer
This project is created strictly for educational and security research purposes. The exploit techniques demonstrated here should only be executed within controlled laboratory environments.
