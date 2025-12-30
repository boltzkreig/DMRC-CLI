# DMRC-CLI

A convenient CLI frontend for the DMRC website — with some much-needed addenda.

---

## Features

* Get journey details from one station to another.
* Query journeys with *minimum interchanges* (defaulting to *least distance*, as on the official website).
* Display station details and available amenities.
* Fetch first and last train timings for your route.
* Remembers the most recent station choices; plus ability to switch the journey direction.
* **Extra:** The official website sometimes doesn’t recommend your desired route — use the `via` option to ensure your intended journey is estimated.
* **Extra:** Find the 5 closest stations (with bearing) using [Termux-API](https://github.com/termux/termux-api).

---

## Installation

Navigate to your desired location ($HOME/.config), then run:

```bash
git clone https://github.com/boltzkreig/DMRC-CLI.git
cd DMRC-CLI
python3 entry.py bootstrap
```

Then, add the recommended path as an alias for convenience.

---

## Usage

Use the `--help` flag to learn more.
Some examples:

1. Interactive origin-to-destination query:

   ```bash
   DMRC
   ```

2. Non-interactive query:

   ```bash
   DMRC -f origin -d destination
   ```

3. Use a via station:

   ```bash
   DMRC -v [VIA]
   ```

4. Get station details:

   ```bash
   DMRC -g
   ```

5. Get first and last train timings:

   ```bash
   DMRC -t
   ```

6. Do the Last request again

   ```bash
   DMRC -r
   ```

---

## External Dependencies

* [FZF](https://github.com/junegunn/fzf)
* [Termux (optional)](https://github.com/termux/termux-api)

---

## Project Structure

```
DMRC/
├── src/
│   ├── pathfinder.py
│   ├── main.py
│   ├── definitions.py
│   ├── assets.py
│   └── amenities.py
├── setup.py
├── entry.py
├── aux/
└── README.md
```

---

## Built With

* Python 3.10+
* requests
* pyfzf
* tcolorpy

---

## License

Distributed under the MIT License.
See `LICENSE` for more information.

---

## Acknowledgements

- [Delhi Metro Rail Website](http://www.delhimetrorail.com)

---

## Show Your Support

If you like this project, consider giving it a ⭐ on GitHub:
[https://github.com/boltzkreig/DMRC-CLI](https://github.com/boltzkreig/DMRC-CLI)

---
