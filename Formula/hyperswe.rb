class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc1"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc1/hyperswe-darwin-arm64"
      sha256 "672d4e1f533e3b5bb54864c3c3afb877e914ccc8e8fe9a29044aa25a753923f9"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc1/hyperswe-linux-amd64"
      sha256 "8caf25a64fb7c00b96a1431d9051a65a5d130c51d1430c3ed5eafd73c14211dd"
    end
  end

  def install
    binary = Dir["hyperswe-*"].first
    bin.install binary => "hyperswe"
  end

  test do
    assert_match "v#{version}", shell_output("#{bin}/hyperswe --version")
  end
end
