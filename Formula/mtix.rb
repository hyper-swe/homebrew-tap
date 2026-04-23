class Mtix < Formula
  desc "AI-native micro issue manager for code-generating LLMs"
  homepage "https://github.com/hyper-swe/mtix"
  license "Apache-2.0"
  version "0.1.3-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_arm64.tar.gz"
      sha256 "50ff358f53f9d7077e6ade0a11d0a7c366ba09ae7c47088fa6a742a0aa28ee3b"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_amd64.tar.gz"
      sha256 "ee42669e2008b6e27d6d7bd93b6b900d1ad6ce0b7cd64c2c6b4480e6621a03ff"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_arm64.tar.gz"
      sha256 "7b332b3566ee2672f02653c6401e2a05a6cef547fe3513a5a5f7c31e6394f89f"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_amd64.tar.gz"
      sha256 "3c5c4c5269d78be65a8e345079d827fd89e26e4e9f4641d436e1b310fad04f06"
    end
  end

  def install
    bin.install "mtix"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mtix --version")
  end
end
