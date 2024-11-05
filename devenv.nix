{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: let
  pkgs-unstable = import inputs.nixpkgs-unstable {system = pkgs.stdenv.system;};
in {
  packages = with pkgs; [
    at-spi2-core
    cairo
    fontconfig
    git
    gdk-pixbuf
    glib
    gnome.zenity
    gtk3
    gst_all_1.gstreamer
    gst_all_1.gst-plugins-base
    harfbuzz
    libepoxy
    pango
  ];

  env.NIX_LD_LIBRARY_PATH = lib.makeLibraryPath (with pkgs; [
    at-spi2-core
    cairo
    fontconfig
    gdk-pixbuf
    glib
    gtk3
    gst_all_1.gstreamer
    gst_all_1.gst-plugins-base
    harfbuzz
    libepoxy
    pango
  ]);
  env.NIX_LD = lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";

  languages = {
    python = {
      version = "3.12";
      enable = true;
      poetry = {
        enable = true;
      };
    };
  };
}
