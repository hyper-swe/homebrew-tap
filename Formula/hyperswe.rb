class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc5.1"

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
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5.1/hyperswe-darwin-arm64"
      sha256 "449196d8bfb192f75a871a38eb9718908e9f2b8e2e6e2df54a23fc282e588405"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5.1/checksums.txt"
      sha256 "e24cbaa7e9e7ec914ca33ca2d79e3955f489e91713e6b3bb87df68f45e353188"
    end
  end

  on_linux do
    depends_on arch: :x86_64

    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5.1/checksums.txt"
      sha256 "e24cbaa7e9e7ec914ca33ca2d79e3955f489e91713e6b3bb87df68f45e353188"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc5.1/hyperswe-linux-amd64"
      sha256 "45214a8e15e76b61d536e212a6cccbde6bdc8edebaf37437c715b8317b4a75a2"
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
