class Mtix < Formula
  desc "AI-native micro issue manager for code-generating LLMs"
  homepage "https://github.com/hyper-swe/mtix"
  license "Apache-2.0"
  version "0.1.0-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_arm64.tar.gz"
      sha256 "PLACEHOLDER"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_amd64.tar.gz"
      sha256 "PLACEHOLDER"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_arm64.tar.gz"
      sha256 "PLACEHOLDER"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_amd64.tar.gz"
      sha256 "PLACEHOLDER"
    end
  end

  def install
    bin.install "mtix"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mtix --version")
  end
end
