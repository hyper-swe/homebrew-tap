class Mgit < Formula
  desc "Sandboxed, checkpointed working substrate for LLM coding agents"
  homepage "https://github.com/hyper-swe/mgit"
  license "Apache-2.0"
  version "0.2.1-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_arm64.tar.gz"
      sha256 "d9afefcc0efc91b93cd10aa8949b9cab87ce30b4e5a1a73a1169054a12f90b09"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_darwin_amd64.tar.gz"
      sha256 "b7a6eaec26184eb59cf874bf8c9feecab2d9a4728a14b5e6c42d1dccfa65e0f6"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_arm64.tar.gz"
      sha256 "2542c5cfaef2df9e4b8c44f7582c95f868e735abbbcc4b1f4a62efc75f23305f"
    end
    on_intel do
      url "https://github.com/hyper-swe/mgit/releases/download/v#{version}/mgit_#{version}_linux_amd64.tar.gz"
      sha256 "cacbe442f5b2d36951e3b191c3e9f868f7f458fc84f34d0b745ce2943013a9e4"
    end
  end

  def install
    bin.install "mgit"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mgit --version")
  end
end
