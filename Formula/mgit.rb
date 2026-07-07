class Mgit < Formula
  desc "Sandboxed, checkpointed working substrate for LLM coding agents"
  homepage "https://github.com/hyper-swe/mgit"
  license "Apache-2.0"
  version "0.3.1-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_arm64.tar.gz"
      sha256 "2f3b0a1fe032900a311c92a5f4e9e15623ab86cf329a5bb972550f0876c60b2f"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_amd64.tar.gz"
      sha256 "ab016e0f626b1b05ae4a7b24ef049bebf95e5a008ddf0391b7640386f67c00b5"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_arm64.tar.gz"
      sha256 "50a47bed9852fccf8558528b46a4f8106bf8e8a18e4489107a9bb9a811493946"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_amd64.tar.gz"
      sha256 "6dd573533bdc6d3516f33be8a81f98185c505721a80c2f0cfdfca117d7ba9cff"
    end
  end

  def install
    bin.install "mgit"
    # mgit-sandboxd (the sandbox host daemon) ships in the Linux and
    # macOS-arm64 archives only; File.exist? keeps one body correct across
    # all four bottles (Intel macOS is mgit-only). Refs: mgit MGIT-44.
    bin.install "mgit-sandboxd" if File.exist?("mgit-sandboxd")
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mgit --version")
  end
end
