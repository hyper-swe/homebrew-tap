class Mtix < Formula
  desc "AI-native micro issue manager for code-generating LLMs"
  homepage "https://github.com/hyper-swe/mtix"
  license "Apache-2.0"
  version "0.1.0-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_arm64.tar.gz"
      sha256 "052ca93576c5e0d99e6607c6f1756843da41571eb47bbf0307cf32ca206eaae0"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_amd64.tar.gz"
      sha256 "5462c186f00166b10fbc32ee6b324e2ef7cf837e4c5f20681542f2b51bebd239"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_arm64.tar.gz"
      sha256 "1e2ef69d5922cc913fc54e2c8b4afa549299e4e1b77b6f8f7dd8c37a51f3fc67"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_amd64.tar.gz"
      sha256 "d6f7df3ed0e84051c9e9b8166420d5d4e61248f2f78475244451c182bbc5cb77"
    end
  end

  def install
    bin.install "mtix"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mtix --version")
  end
end
