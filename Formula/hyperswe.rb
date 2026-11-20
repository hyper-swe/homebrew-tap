class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc5"

  # The release builds two binaries: Apple silicon macOS and x86-64 Linux.
  # Homebrew needs a url on every platform to load a formula at all, so the
  # two platforms with no build point at the release's checksums.txt, which is
  # never installed: the disable! line below refuses the install there before
  # anything is fetched, and says there is no build for that platform.
  # Keep these lines as they are: the release update rewrites the version
  # line, every url line under hyper-swe/*/releases/download/v<version>/, and
  # the sha256 lines in file order (macOS arm, macOS intel, Linux arm, Linux
  # intel).
  on_macos do
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5/hyperswe-darwin-arm64"
      sha256 "a0a91573caee4c1faa500e8742d5e9b42a90fe41dd3b84ef129bced525d44974"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5/checksums.txt"
      sha256 "f8c7cc8f51fe3f8aab5a37bdbe59118eaae29c8ffb32c487304cc3563da639e3"
    end
  end

  on_linux do
    depends_on arch: :x86_64

    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5/checksums.txt"
      sha256 "f8c7cc8f51fe3f8aab5a37bdbe59118eaae29c8ffb32c487304cc3563da639e3"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5/hyperswe-linux-amd64"
      sha256 "bf196c18836cb198b93adc721026103c38fae65c7f1259d87593f9d589f4bce4"
    end
  end

  if (OS.mac? && Hardware::CPU.intel?) || (OS.linux? && Hardware::CPU.arm?)
    disable! date: "2026-10-29", because: "has no build for this platform"
  end

  def install
    binary = Dir["hyperswe-*"].first
    bin.install binary => "hyperswe"
  end

  test do
    assert_match "v#{version}", shell_output("#{bin}/hyperswe --version")
  end
end
