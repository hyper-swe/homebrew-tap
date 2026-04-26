class Mtix < Formula
  desc "AI-native micro issue manager for code-generating LLMs"
  homepage "https://github.com/hyper-swe/mtix"
  license "Apache-2.0"
  version "0.1.5-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_arm64.tar.gz"
      sha256 "2073051fe96f9077504b968d09a0ce55a98afc0c6d128226130ec38d85086ef5"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_amd64.tar.gz"
      sha256 "e106d233fb83c706d0f4f25c858d72616616925dd23f42e9c3ac5b496757a944"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_arm64.tar.gz"
      sha256 "99d2876761cac651977ff635b4c58241dee92936aeb1bf6e7908e6cb5a6b0a7d"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_amd64.tar.gz"
      sha256 "bbd9aa06dd1cbdb873ea3d082036b0f4bb34f6ff80e38c482c486462ff505b4d"
    end
  end

  def install
    bin.install "mtix"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mtix --version")
  end
end
