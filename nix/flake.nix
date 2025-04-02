{
  description = "Bluefin AI Agent Trader - Reproducible Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication mkPoetryDevEnv;
      in {
        packages = {
          bluefin-trader = mkPoetryApplication {
            projectDir = ../.;
            python = pkgs.python39;
          };

          default = self.packages.${system}.bluefin-trader;
        };

        devShells.default = mkPoetryDevEnv {
          projectDir = ../.;
          python = pkgs.python39;
        };

        apps = {
          bluefin-trader = {
            type = "app";
            program = "${self.packages.${system}.bluefin-trader}/bin/bluefin-trader";
          };
        };
      }
    );
}