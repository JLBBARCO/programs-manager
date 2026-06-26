# Programs Manager Website

The website displays the `log.log` output in real time while the program runs. The UI groups log lines by severity (`INFO`, `DEBUG`, `WARNING`, `ERROR`) and shows recent entries first, with automatic scrolling unless the user scrolls up.

## Frontend (Site)

### Language

English (En-US)

### Main view

- Four containers display `INFO`, `DEBUG`, `WARNING`, and `ERROR` messages.
- Each container has a fixed height and horizontal scrollbar. Older messages appear above newer messages.
- Incoming log lines follow these formats:

  ```log
  [dd/mm/yyyy hh:mm:ss] [INFO] <message>
  [dd/mm/yyyy hh:mm:ss] [WARNING] <message>
  [dd/mm/yyyy hh:mm:ss] [ERROR] <message>
  ```

- Example input line: `[01/06/2026 12:30:45] [SUCCESS] Visual Studio Code installed` is displayed as `01/06/2026 12:30:45 | Visual Studio installed` with the timestamp colored `#808080`.
- The site partitions historical runs: entries older than 1 minute compared to the site's load timestamp are shown in a separate history section.
- The monitor also stores the latest `Start <program>` marker and `Operating System: <system>` marker so the header and history can be grouped by program.

### Footer — Contact container

Contact cards are loaded from a remote JSON and displayed as circular icon buttons. Hovering shows the contact `name`. The JSON `url` becomes the card link and `iconName` indicates the icon to display.

CSS layout example:

```css
display: flex;
flex-flow: row wrap;
justify-content: space-between;
align-items: center;
```

### Error page

If the site cannot access the `log.log` port (the port provided in the page query parameter `?port=NNNN` or any `99xx` port) or the file is not shared, an error page is shown with a refresh button and a link to the GitHub repository: `https://github.com/JLBBARCO/programs-manager`.

## Backend (Site)

The site temporarily records the page load time and uses it to partition current-run logs from historical logs. Monitoring also tracks the current program name and operating system extracted from the log stream. Monitoring stops when the latest log line contains `[INFO] End system`.

### Port probe

On load the site probes the port specified by the query parameter `?port=NNNN` (if present) or falls back to a sensible default in the `99xx` range for up to 30 seconds. If the log endpoint is not available, monitoring is paused until the user refreshes.

### Contacts source

Contact data is fetched from:

`https://raw.githubusercontent.com/JLBBARCO/portfolio/main/src/json/areas/contact.json` and cached by Vercel hourly to minimize GitHub requests.
