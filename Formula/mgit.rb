class Mgit < Formula
  desc "Sandboxed, checkpointed working substrate for LLM coding agents"
  homepage "https://github.com/hyper-swe/mgit"
  license "Apache-2.0"
  version "0.3.0-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_arm64.tar.gz"
      sha256 "99f4d30d5f0ffa234ca04495948985b6055fcf96063a50bf56cd37a99c89e045"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_amd64.tar.gz"
      sha256 "dcedefc576829a8dabc26bd52418ff642ee32d553f04af6d659b615cc8d752dd"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_arm64.tar.gz"
      sha256 "52db500d7f77fac7745d45e649a50cf6ecd5370c0c3c50679b3a52eecae7d236"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_amd64.tar.gz"
      sha256 "00ad6a8ecb4fb2624a4b3daa22cd5cc8bfe24161cc1e1aa5fde251f667b4d182"
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
