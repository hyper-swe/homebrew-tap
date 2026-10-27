class Hyperswe < Formula
  desc "Runs AI coding agents through a reviewed loop"
  homepage "https://github.com/hyper-swe/releases"
  version "0.2.0-beta-rc2"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc2/hyperswe-darwin-arm64"
      sha256 "fb45971f9fc182624b0f1d0e3ab51e37e067d55d0cef50de0c8dd2df9a486592"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc2/hyperswe-linux-amd64"
      sha256 "fccee270cf31644ce3a43d236928ef0791af2a9c87af36dd398abce98de005f2"
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
