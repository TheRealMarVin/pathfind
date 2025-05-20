# Pathfind

**Pathfind** is a Python project designed to test and compare different pathfinding strategies. The initial goal was to get A\* and D\* Lite up and running in a common framework. Now that they’re happily coexisting, the plan is to add more algorithms and eventually include proper stat tracking to make comparisons more insightful.

If you've ever asked yourself:

* “How does A\* behave when things move around?”
* “Is D\* Lite really smarter in dynamic maps?”
* “What if I want to plug in my own idea for a pathfinder?”

Then you're in the right place.

---

## Installation

```bash
git clone https://github.com/TheRealMarVin/pathfind.git
cd pathfind
pip install -r requirements.txt
```

Requirements are minimal — mostly `pygame`, `numpy`, and some good intentions.

---

## How to Use

Once installed, you can run the main loop and watch the agents make their moves:

```bash
python main.py
```

The config is stored in `config/config.yaml`. You can tweak things like:

* Which algorithms to run (`agent_types`)
* Number of maps and spawns
* Update interval for the agents
* Colors, if you’re into that sort of thing

Agents will move, obstacles will shift, and you'll see how each algorithm adapts (or doesn’t).

---

## Roadmap

Coming soon:

* Stats: frame counts, replans, distance traveled, success rates
* More algorithms (suggestions welcome!)

---

## Contributing

Contributions are welcome, especially if:

* You have a new pathfinding method you want to try out
* You’re good at collecting and reporting stats
* You enjoy code that can be run, understood, and modified in the same sitting

Open a pull request or start a discussion — just keep it respectful and constructive. We're all here to learn (or prove that our favorite algorithm is better).
