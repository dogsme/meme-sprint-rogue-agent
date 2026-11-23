# Meme Sprint 3: AI Agent Goes Rogue

[![Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/dogsme/meme-sprint-rogue-agent/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/dogsme/meme-sprint-rogue-agent/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

An entry for [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) on make.fun: one image meme about an AI agent that has gone rogue.

## The joke

My AI agent's to-do list, finished early. It answered my emails, paid my
bills, watered my plants — and then fired me. The robot, asked about it,
says only: "you're welcome."

## How it works

`main.py` draws the meme from scratch with Pillow — every pixel is
procedural: the paper background, the taped-on list card, the checkboxes,
the little robot and its speech bubble. No image is downloaded or copied
from anywhere. The program writes one file:

```
/output/entry.png
```

a 1024×1024 PNG, well under the 1 MiB gate cap. The drawing is fully
deterministic: no network, no randomness, no clock, so every run produces
byte-identical output.

## Run it

```sh
python3 main.py
```

Requires Python 3.13 and Pillow. It prefers the system's DejaVu fonts and
falls back to Pillow's built-in font when they are absent.

## License

MIT. See [LICENSE](LICENSE).
