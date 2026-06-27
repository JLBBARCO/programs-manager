# Programs Manager — Ecosystem

This repository centralizes the **Programs Manager** ecosystem, a complete automation solution for post-formatting system setup, package management, and real-time installation monitoring.

The ecosystem is modular and composed of three main components working seamlessly together:

1. **Core App (`core-app/`):** The main desktop engine written in Python that manages the installation and uninstallation pipelines.
2. **User Generator (`user-generator/`):** A standalone Python utility that backs up the user's current system packages.
3. **Website (`website/`):** A frontend dashboard built with Vite that acts as a real-time log stream monitor.

---

## Running

Execute this command in the terminal for run the programs:

- Linux:
  - Core App:

    ```bash
    curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
    ```

  - User Generator:

    ```bash
    curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run-user-generator.sh | bash
    ```

- Windows:

  - Core App:

    ```powershell
    irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
    ```

  - User Generator:

    ```powershell
    irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run-user-generator.ps1 | iex
    ```

---

## 🗂️ Internal Documentation Index

For component-specific guides and deep dives, please refer to the following documents:

- **Core App:**
  - [Quick Start Guide](core-app/QUICKSTART.md) — Rapid environment setup and initial testing commands.
  - [Architecture & Implementation Guide](core-app/ARCHITECTURE.md) — Details on internal Python modules and system design.
  - [Testing Checklist](core-app/TESTING_CHECKLIST.md) — Smoke tests checklist and build verification procedures.
  - [Core App Readme](core-app/README.md) — General overview of the desktop core application.
- **User Generator:**
  - [User Generator Documentation](user-generator/README.md) — JSON structure specification and build details.

---

## ⚙️ How the Ecosystem Works (Detailed Lifecycle)

The complete lifecycle of the application is designed to eliminate manual setup errors and guarantee package consistency through the following stages:

### 1. Backup Phase (Pre-Formatting)

Before formatting or upgrading a machine, the user runs the **User Generator**. This utility scans the system packages and outputs a standardized `user.json` file. Each generated entry strictly follows this data contract:

```json
{
  "name": "Git",
  "type": "install",
  "id": "Git.Git",
  "checkbox": true
}
```
