class Mtix < Formula
  desc "AI-native micro issue manager for code-generating LLMs"
  homepage "https://github.com/hyper-swe/mtix"
  license "Apache-2.0"
  version "0.5.1-beta"

  on_macos do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_arm64.tar.gz"
      sha256 "ecf73cc3cd878d259b0fa38104c23d22d39b3cd6cee4dd51092bce71df534000"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_darwin_amd64.tar.gz"
      sha256 "2bc537e940526cd80b7cf3f3da1e05732356ac3ec00541ab1db8e46db07d3a02"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_arm64.tar.gz"
      sha256 "f934532bec1cd2bf5ccbd19c0e7fc7e5767abad3ba046e389bb1bc439096fb1e"
    end
    on_intel do
      url "https://github.com/hyper-swe/mtix/releases/download/v#{version}/mtix_#{version}_linux_amd64.tar.gz"
      sha256 "dde70c02fe2ba1966d5f44d11599485383a4a40d703510b8e6e4b6653b893db6"
    end
  end

  def install
    bin.install "mtix"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mtix --version")
  end
end
