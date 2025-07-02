![Unit Tests](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/ugurserhattoy/TSA/refs/heads/gh-pages/unit-tests.json&logo=pytest&logoColor=white)
![Code Quality](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/ugurserhattoy/TSA/refs/heads/gh-pages/code-check.json&logo=freecodecamp&logoColor=darkblue)
![Security](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/ugurserhattoy/TSA/refs/heads/gh-pages/security-check.json&logo=svelte&logoColor=%23EA0016)

# TSA - Track Sponsored Applications

TSA is a lightweight tool designed to help users track applications for UK companies offering visa sponsorships.
It allows efficient filtering by city and organisation.
You can create application details which includes role, date, contact and notes for each organisation.

## Features
- Filter sponsors by city and organisation.
- Note application details for the organisations.
- Easily track unmarked/new sponsors when the sponsor list is updated.
- Whole pipeline can be managed by keyboard.
- Auto new release check for TSA.
- Cross-platform (Mac, Windows, Linux).

## Confirming the release

Use below commands to compare output with sha256 files.

### MacOS
```sh
shasum -a 256 TSA.dmg
```

### Linux
```sh
shasum -a 256 TSA-Linux.zip
```

### Windows
```sh
Get-FileHash .\TSA.exe -Algorithm SHA256
```

## Running on MacOS

It has not yet been signed by Apple. Hence after installing, it needs to be unlocked as below:
```sh
xattr -rd com.apple.quarantine /Applications/TSA.app
```

# Keyboard Shortcuts

| Shortcut          | Action                   | Details                            |
|-------------------|--------------------------|------------------------------------|
| Ctrl + B          | Previous Page            | Sponsors Table Navigation          |
| Ctrl + N          | Next Page                | Sponsors Table Navigation          |
| Ctrl + F          | Back to Filtering        | Return to filter inputs from table |
| Esc / Backspace   | Back                     | Return to previous screen          |
| Esc / Backspace   | Close Window / Cancel    | Close pop-up window or Cancel      |
| Enter             | Apply Filter             | When focused filter section        |
| Enter             | Open Applications        | When focused sponsor table         |
| E                 | Edit Application         | On Applications Table              |
| A                 | Add New Application      | On Applications Table              |
| Delete            | Delete Application       | On Applications Table              |

## License
This project is licensed under the MIT License (Non-Commercial Clause). See [LICENSE.md](LICENSE.md) for details.