class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc4"

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
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc4/hyperswe-darwin-arm64"
      sha256 "624d0f93d9334c2cde6b6d9b60fb9f9a73296dedb612cd04e7dc35a023de595f"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc4/checksums.txt"
      sha256 "19322196db114592db6b421a6f1bce27207cb8625dd49d009c4c032265dd5a79"
    end
  end

  on_linux do
    depends_on arch: :x86_64

    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc4/checksums.txt"
      sha256 "19322196db114592db6b421a6f1bce27207cb8625dd49d009c4c032265dd5a79"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc4/hyperswe-linux-amd64"
      sha256 "19059c69b633e0bc93175d8bf847f4d56a83a33370035f09d295d37a9b65e68e"
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
