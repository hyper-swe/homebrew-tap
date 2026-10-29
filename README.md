# Homebrew Tap for HyperSWE

Homebrew formulae for [HyperSWE](https://github.com/hyper-swe) tools.

## Set up the tap

Trust the tap once:

```bash
brew trust hyper-swe/tap
```

Homebrew installs a formula you name on the command line from any tap, but it
loads that formula's dependencies only from a tap you trust. The mgit formula
depends on libkrunfw from this tap on Apple silicon macOS, so trust the tap
before you install mgit there. The trust step is the only setup step.

## Install

```bash
brew install hyper-swe/tap/mgit
brew install hyper-swe/tap/mtix
brew install hyper-swe/tap/hyperswe
```

## Available formulae

| Formula | What it is for |
|---------|----------------|
| [mgit](https://github.com/hyper-swe/mgit) | A sandboxed, checkpointed working substrate for coding agents built on large language models (LLMs). On Apple silicon macOS it depends on `libkrunfw` for its microVM sandbox (a small virtual machine). |
| [mtix](https://github.com/hyper-swe/mtix) | A micro issue manager for code-generating large language models (LLMs). |
| [hyperswe](https://github.com/hyper-swe/releases) | Runs coding agents through a reviewed loop. |
| [libkrunfw](https://github.com/libkrun/libkrunfw) | The library that carries the guest Linux kernel for mgit's microVM sandbox on Apple silicon macOS. Built from upstream release v5.5.0. |

## libkrunfw and its licenses

libkrunfw is an upstream library, distributed separately from mgit's macOS archive.
Its complete source is published at
https://github.com/hyper-swe/homebrew-tap/releases/tag/libkrunfw-5.5.0. Its library code is
distributed under LGPL-2.1-only, and the Linux kernel it bundles, with the
patches applied to it, under GPL-2.0-only. The formula's license field is
`LGPL-2.1-only AND GPL-2.0-only`.

The installed keg holds both license texts (`LICENSE-LGPL-2.1-only`,
`LICENSE-GPL-2.0-only`), a notice (`NOTICE.txt`) and the source offer
(`SOURCE-OFFER.txt`). To read them:

```bash
ls "$(brew --prefix libkrunfw)"
```

The keg is linked into the Homebrew prefix, where mgit's sandbox looks for
the library. If you installed libkrunfw from another tap before, uninstall
that one first: both link `libkrunfw.5.dylib` into the same place.

This tap has no bottles for libkrunfw yet, so Homebrew builds it from
upstream's release archive on your machine. The build compiles the bundled
kernel image into the library; it doesn't compile a kernel.
