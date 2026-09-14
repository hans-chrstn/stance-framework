{
  description = "Development environment for the Stances Framework Skyrim plugin and authoring tools";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      # The current development target is a 64-bit Linux/NixOS workstation.
      # Skyrim's Windows artifact is produced through the xwin cross-toolchain.
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      llvm = pkgs.llvmPackages_latest;

      developmentPackages = [
        # Stable task and repository interface
        pkgs.just
        pkgs.git
        pkgs.git-lfs
        pkgs.ripgrep
        pkgs.fd
        pkgs.jq
        pkgs.yq-go

        # Native build and inspection
        pkgs.cmake
        pkgs.ninja
        pkgs.pkg-config
        pkgs.vcpkg
        llvm.clang
        llvm.clang-tools
        llvm.lld
        llvm.llvm
        pkgs.xwin

        # Repository tooling
        pkgs.python3
        pkgs.uv
        pkgs.ruff
        pkgs.dotnet-sdk
        pkgs.shellcheck
        pkgs.shfmt
        pkgs.actionlint
        pkgs.nixfmt
        pkgs.deadnix
        pkgs.statix

        # Archive and network utilities
        pkgs.p7zip
        pkgs.zip
        pkgs.unzip
        pkgs.cacert
        pkgs.curl
        pkgs.file
      ];

      runtimeTestPackages = [
        # Kept out of the default shell because these have a larger closure.
        pkgs.wineWow64Packages.stable
        pkgs.gamescope
        pkgs.libei
        pkgs.vulkan-tools
      ];

      mkStancesShell =
        {
          name,
          extraPackages ? [ ],
        }:
        pkgs.mkShell {
          inherit name;
          packages = developmentPackages ++ extraPackages;

          # Compatibility inputs for the currently selected runtime lane.
          # These values do not claim that runtime compatibility has passed.
          STANCES_TARGET_STOREFRONT = "steam";
          STANCES_TARGET_SKYRIM_RUNTIME = "1.7.104.0";
          STANCES_TARGET_SKSE = "2.3.1";
          STANCES_TARGET_ADDRESS_LIBRARY = "13";
          STANCES_TARGET_OAR = "3.2.1";
          STANCES_TARGET_COMMONLIB = "8.0.1";

          CMAKE_GENERATOR = "Ninja";
          VCPKG_ROOT = "${pkgs.vcpkg}/share/vcpkg";
          DOTNET_NOLOGO = "1";
          DOTNET_CLI_TELEMETRY_OPTOUT = "1";
          NUGET_XMLDOC_MODE = "skip";

          shellHook = ''
            # The parent launcher supplies this when the shell is loaded from
            # above Source/. Direct use from Source/ derives it from Git.
            if [[ -z "''${STANCES_SOURCE_ROOT:-}" ]]; then
              export STANCES_SOURCE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"
            fi
            export STANCES_SOURCE_ROOT="$(realpath -- "$STANCES_SOURCE_ROOT")"
            export STANCES_CACHE_ROOT="$STANCES_SOURCE_ROOT/.cache"
            export XWIN_CACHE_DIR="$STANCES_CACHE_ROOT/xwin-cache"
            export XWIN_SYSROOT="$STANCES_CACHE_ROOT/xwin-sysroot"
            export VCPKG_DOWNLOADS="$STANCES_CACHE_ROOT/vcpkg-downloads"
            export VCPKG_DEFAULT_BINARY_CACHE="$STANCES_CACHE_ROOT/vcpkg-binary-cache"
            export UV_CACHE_DIR="$STANCES_CACHE_ROOT/uv"
            export DOTNET_CLI_HOME="$STANCES_CACHE_ROOT/dotnet"
            export NUGET_PACKAGES="$STANCES_CACHE_ROOT/nuget"
            export WINEPREFIX="$STANCES_CACHE_ROOT/wineprefix"

            mkdir -p \
              "$XWIN_CACHE_DIR" \
              "$VCPKG_DOWNLOADS" \
              "$VCPKG_DEFAULT_BINARY_CACHE" \
              "$UV_CACHE_DIR" \
              "$DOTNET_CLI_HOME" \
              "$NUGET_PACKAGES"

            echo "Stances Framework development shell: ${name}"
            echo "Target: Steam Skyrim $STANCES_TARGET_SKYRIM_RUNTIME / SKSE $STANCES_TARGET_SKSE"
            echo "Run: just doctor"
          '';
        };
    in
    {
      devShells.${system} = {
        default = mkStancesShell { name = "stances-framework-dev"; };
        runtime-test = mkStancesShell {
          name = "stances-framework-runtime-test";
          extraPackages = runtimeTestPackages;
        };
      };

      formatter.${system} = pkgs.nixfmt;
    };
}
