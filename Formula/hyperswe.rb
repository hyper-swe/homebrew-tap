class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc3.1"

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
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3.1/hyperswe-darwin-arm64"
      sha256 "e55d0a8df90b809391c18d262026477e338c548c8480c2fc5e92013392b22aad"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3.1/checksums.txt"
      sha256 "b1da60fbe02d41002dfdcb5d26c7c2872d525418c2c863ca76f296f2f4716d62"
    end
  end

  on_linux do
    depends_on arch: :x86_64

    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3.1/checksums.txt"
      sha256 "b1da60fbe02d41002dfdcb5d26c7c2872d525418c2c863ca76f296f2f4716d62"
    end
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3.1/hyperswe-linux-amd64"
      sha256 "4ce4dbef4898a99a57ca51e1e706ec70ece9e582caaad622716faf0af3024f0a"
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
