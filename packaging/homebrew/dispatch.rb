# Homebrew formula for dispatch-cli.
#
# Tap setup (once published):
#   brew tap shifttheculture/dispatch
#   brew install dispatch
#
# After each release:
#   1. Bump `version` below to match the PyPI release tag.
#   2. Update `url` to the matching GitHub tarball and regenerate `sha256`:
#        curl -fsSL <url> | sha256sum
#   3. Re-resolve `resource` blocks with:
#        brew update-python-resources dispatch
#   4. Commit to homebrew-dispatch tap repo.

class Dispatch < Formula
  include Language::Python::Virtualenv

  desc "Hub-and-spoke CLI: classify short messages, supercharge to agent prompts, fan out to inboxes"
  homepage "https://github.com/shifttheculture/dispatch"
  url "https://github.com/shifttheculture/dispatch/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_AT_RELEASE_TIME"
  license "MIT"

  depends_on "python@3.12"

  # Resources are auto-populated at release time via:
  #   brew update-python-resources dispatch
  # Stubs below keep the formula syntactically valid until first release.
  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.12.5.tar.gz"
    sha256 "REPLACE"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.9.4.tar.gz"
    sha256 "REPLACE"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    output = shell_output("#{bin}/dispatch version")
    assert_match "dispatch-cli", output
  end
end
