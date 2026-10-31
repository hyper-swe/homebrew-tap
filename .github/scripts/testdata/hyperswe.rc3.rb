class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc3"

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
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3/hyperswe-darwin-arm64"
      sha256 "bcd62a240505979097dd00b50aa43e6f42c77f917edbdaac370767b473b8adbb"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3/checksums.txt"
      sha256 "779a0f2ab118670e4d9f51a7a765ba8b34d807c2cf03ad9f482091db62bba86e"
    end
  end

  on_linux do
    depends_on arch: :x86_64

    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3/checksums.txt"
      sha256 "779a0f2ab118670e4d9f51a7a765ba8b34d807c2cf03ad9f482091db62bba86e"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3/hyperswe-linux-amd64"
      sha256 "8cc03660546f078a929b60827d21255d5c25279e0a274e33a813dbcf6306dab8"
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
