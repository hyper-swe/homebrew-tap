class Libkrunfw < Formula
  desc "Dynamic library bundling a Linux kernel in a convenient storage format"
  homepage "https://github.com/containers/libkrunfw"
  # Upstream publishes three archives for v5.5.0. This formula uses the first:
  #
  #   libkrunfw-prebuilt-aarch64.tgz  the generated kernel.c (the compiled
  #                                   aarch64 guest kernel, linux-6.12.91,
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
  # TODO(maintainer): decide whether to keep building from this prebuilt
  # kernel image or to build the kernel from source on a Linux builder
  # (decision c). The license duty is the same either way.
  #
  # The sha256 below was computed from the bytes downloaded from the URL;
  # it was not checked against a digest the publisher states.
  url "https://github.com/containers/libkrunfw/releases/download/v5.5.0/libkrunfw-prebuilt-aarch64.tgz"
  sha256 "5bfae6efee63dbdf04a8fac2a69d772d9f900af2f54c4429b4acdfd6d86b9979"
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
    system "make"
    system "make", "PREFIX=#{prefix}", "install"
    prefix.install "LICENSE-GPL-2.0-only", "LICENSE-LGPL-2.1-only"
    (prefix/"NOTICE.txt").write notice
    (prefix/"SOURCE-OFFER.txt").write source_offer
  end

  def kernel_version
    "6.12.91"
  end

  def notice
    <<~EOS
      libkrunfw #{version}, from https://github.com/containers/libkrunfw, is a
      library that bundles a Linux kernel (linux-#{kernel_version}) as a storage
      format. Its library code is distributed under LGPL-2.1-only, and the
      bundled kernel and the patches applied to it under GPL-2.0-only; the
      license texts are LICENSE-LGPL-2.1-only and LICENSE-GPL-2.0-only in this
      directory. libkrunfw is a separate library, installed on its own, and is
      not part of any product that loads it.
    EOS
  end

  # The source offer. Items 3 and 4, the retention period and the contact
  # address are open decisions, kept as placeholders:
  #
  # TODO(maintainer): decision a. Host the single source archive (item 4)
  #   beside the bottle, or rely on the upstream URLs only.
  # TODO(maintainer): decision b. How long the source stays available. The
  #   text below states the GPLv2 section 3(b) floor.
  # TODO(maintainer): decision d. The contact address for the offer.
  # TODO(maintainer): decision e. Whether a lawyer reviews this text before
  #   the formula is published.
  def source_offer
    <<~EOS
      libkrunfw #{version} is distributed under LGPL-2.1-only for the library code
      and GPL-2.0-only for the bundled Linux kernel (linux-#{kernel_version}) and the
      patches applied to it. The complete corresponding source is available
      to anyone, free of charge:

        1. Upstream library, patches and configuration:
           https://github.com/containers/libkrunfw/releases/tag/v#{version}
           (source tarball, plus libkrunfw-prebuilt-aarch64.tgz)
        2. The Linux kernel source the image was built from:
           https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-#{kernel_version}.tar.xz
        3. Our build patches and build script, if any:
           TODO(maintainer): URL of the hyper-swe repository path, pinned to a tag
        4. A single archive holding items 1-3 with checksums:
           TODO(maintainer): URL of the release asset, same release as the binary

      This offer is valid for at least three years from the date the binary
      was last distributed, and for as long as the binary is offered.
      Questions: TODO(maintainer): contact address.
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
