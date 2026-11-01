class Libkrunfw < Formula
  desc "Dynamic library bundling a Linux kernel in a convenient storage format"
  homepage "https://github.com/libkrun/libkrunfw"
  # Upstream publishes three archives for v5.6.2. This formula uses the first:
  #
  #   libkrunfw-prebuilt-aarch64.tgz  the generated kernel.c (the compiled
  #                                   aarch64 guest kernel, linux-6.12.109,
  #                                   as a C array), bin2cbundle.py, a
  #                                   Makefile and both license texts
  #   libkrunfw-aarch64.tgz           a built Linux aarch64 libkrunfw.so
  #   libkrunfw-x86_64.tgz            a built Linux x86_64 libkrunfw.so
  #
  # Only the first one yields a macOS library: `make` compiles kernel.c into
  # libkrunfw.5.dylib with the host's C compiler, with no kernel compile. The
  # other two are Linux shared objects that macOS cannot load.
  #
  # This archive is NOT the kernel source. kernel.c is the compiled kernel
  # image, so the source obligation is met by the offer in SOURCE-OFFER.txt
  # (the kernel tarball, upstream's patches and its kernel config), not by
  # this download.
  #
  # Decided: for the beta this builds from upstream's prebuilt kernel image;
  # the hosted source holds that exact asset. The license duty is the same
  # if the kernel is later built from source.
  #
  # The sha256 below was computed from the downloaded bytes and matches the
  # digest GitHub records for this asset on upstream's v5.6.2 release.
  url "https://github.com/containers/libkrunfw/releases/download/v5.6.2/libkrunfw-prebuilt-aarch64.tgz"
  sha256 "adef6739cc3bda2a1b57f04c08ccbfdf206a6c831d76b32de1beddc0e7984e86"
  # Equals the SPDX expression "LGPL-2.1-only AND GPL-2.0-only": the library
  # code is LGPL-2.1-only; the bundled kernel and upstream's kernel patches
  # are GPL-2.0-only.
  license all_of: ["LGPL-2.1-only", "GPL-2.0-only"]

  # Not keg_only, on purpose. libkrun loads libkrunfw by its file name, and
  # mgit's sandbox looks for it in a fixed list of directories that includes
  # HOMEBREW_PREFIX/lib. A linked keg is found there; a keg_only one is not.
  #
  # The only consumer this tap carries is mgit's macOS sandbox, which runs on
  # Apple silicon. mgit's Linux archive ships its own libkrunfw.
  depends_on arch: :arm64
  depends_on :macos

  def install
    # The library must keep running on macOS 14 whatever macOS builds it. The
    # compiler takes its minimum from this variable, and Homebrew clears it from
    # the environment of a build, so only setting it here reaches `make`.
    ENV["MACOSX_DEPLOYMENT_TARGET"] = "14.0"
    system "make"
    system "make", "PREFIX=#{prefix}", "install"
    prefix.install "LICENSE-GPL-2.0-only", "LICENSE-LGPL-2.1-only"
    (prefix/"NOTICE.txt").write notice
    (prefix/"SOURCE-OFFER.txt").write source_offer
  end

  def kernel_version
    "6.12.109"
  end

  def notice
    <<~EOS
      libkrunfw #{version}, from https://github.com/libkrun/libkrunfw, is a
      library that bundles a Linux kernel (linux-#{kernel_version}) as a storage
      format. Its library code is distributed under LGPL-2.1-only, and the
      bundled kernel and the patches applied to it under GPL-2.0-only; the
      license texts are LICENSE-LGPL-2.1-only and LICENSE-GPL-2.0-only in this
      directory. libkrunfw is a separate library, distributed separately from mgit.
    EOS
  end

  # The source offer. Decided: the source is hosted in the same release as
  # this library's binaries (item 4) and kept for the life of the release; the
  # contact address is swe@hyperswe.com.
  def source_offer
    <<~EOS
      libkrunfw #{version} is distributed under LGPL-2.1-only for the library code
      and GPL-2.0-only for the bundled Linux kernel (linux-#{kernel_version}) and the
      patches applied to it. The complete corresponding source is available
      to anyone, free of charge:

        1. Upstream libkrunfw source (library code, kernel patches, kernel
           configuration and build scripts), tag v#{version}:
           https://github.com/libkrun/libkrunfw/releases/tag/v#{version}
        2. The Linux kernel source the image was built from:
           https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-#{kernel_version}.tar.xz
        3. We apply no patches of our own. This library was built from
           upstream's prebuilt kernel image (libkrunfw-prebuilt-aarch64.tgz,
           object code, sha256 adef6739cc3bda2a1b57f04c08ccbfdf206a6c831d76b32de1beddc0e7984e86) by the build steps in:
           https://github.com/hyper-swe/homebrew-tap/blob/5c359de9b9c9dc7870eed6a44bba6875b9152dbd/Formula/libkrunfw.rb
        4. A copy of items 1 and 2, and of the prebuilt kernel image, kept by us
           beside this library's binaries, with checksums:
           https://github.com/hyper-swe/homebrew-tap/releases/tag/libkrunfw-#{version}
           libkrunfw-v#{version}-kernel-linux-#{kernel_version}.tar.xz,
           libkrunfw-v#{version}-source.tar.gz,
           libkrunfw-v#{version}-prebuilt-aarch64.tgz (object code, for reference)

      This offer is valid for at least three years from the date the binary
      was last distributed, and for as long as the binary is offered; the
      hosted source is kept for the life of the release.
      If any link above stops working, write to swe@hyperswe.com and we will
      send the complete corresponding source, at no charge beyond the cost of
      physically providing it. This offer is open to anyone who has this binary.
    EOS
  end

  test do
    (testpath/"test.c").write <<~C
      #include <stdio.h>
      int krunfw_get_version(void);
      int main(void) {
        printf("%d\\n", krunfw_get_version());
        return 0;
      }
    C
    system ENV.cc, "test.c", "-L#{lib}", "-lkrunfw", "-o", "test"
    assert_equal "5", shell_output("./test").strip
    %w[LICENSE-GPL-2.0-only LICENSE-LGPL-2.1-only NOTICE.txt SOURCE-OFFER.txt].each do |f|
      assert_path_exists prefix/f
    end
    assert_match "linux-#{kernel_version}", (prefix/"SOURCE-OFFER.txt").read
  end
end
