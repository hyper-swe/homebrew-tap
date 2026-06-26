class Mgit < Formula
  desc "Sandboxed, checkpointed working substrate for LLM coding agents"
  homepage "https://github.com/hyper-swe/mgit"
  license "Apache-2.0"
  version "0.2.0-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_arm64.tar.gz"
      sha256 "45e4261fd0d95edd88ee3d9da0f7c2982d21313041a958d695a220a2912cea0a"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_amd64.tar.gz"
      sha256 "cc4472ae08f204202bfd57d597c7aaf73e482fdb302c96d3d9ad3930bef6504b"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_arm64.tar.gz"
      sha256 "0d73dc90789d623215f67cc778a7fa35097bd17db84290c2faab4614e9fcce02"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_amd64.tar.gz"
      sha256 "61737e568cc6ede4af9dccba326c7a10947d5a07711fea643de5b46aa8c27b42"
    end
  end

  def install
    bin.install "mgit"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mgit --version")
  end
end
