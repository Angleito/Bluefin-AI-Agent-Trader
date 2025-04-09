{
  description = "Bluefin AI Agent Trader Template - Reproducible Production Environment";

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
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication mkPoetryEnv;
        
        # Python version to use
        python = pkgs.python310;
        
        # Common overrides for Python packages that might need special handling
        commonOverrides = pkgs.lib.composeManyExtensions [
          poetry2nix.defaultPoetryOverrides
          (final: prev: {
            # Add any package overrides here if needed
          })
        ];
        
        # The main application package
        app = mkPoetryApplication {
          projectDir = ../.;
          inherit python;
          overrides = commonOverrides;
          # Disable tests during build for production
          checkPhase = "";
        };
        
        # Create a pure Python environment with all dependencies
        pythonEnv = mkPoetryEnv {
          projectDir = ../.;
          inherit python;
          overrides = commonOverrides;
        };
        
        # Runtime dependencies for the Docker image
        runtimeDeps = [
          pkgs.bash
          pkgs.coreutils
          pkgs.curl
          pkgs.cacert
          pkgs.openssl
        ];
        
        # Docker image creation using Nix
        dockerImage = pkgs.dockerTools.buildLayeredImage {
          name = "bluefin-ai-agent-trader-template";
          tag = "latest";
          
          # Include the application and runtime dependencies
          contents = [
            app
            pythonEnv
            pkgs.busybox
          ] ++ runtimeDeps;
          
          # Configure the Docker image
          config = {
            Cmd = [ "${app}/bin/bluefin-trader" ];
            WorkingDir = "/app";
            Env = [
              "PYTHONUNBUFFERED=1"
              "PYTHONPATH=${pythonEnv}/lib/python3.10/site-packages"
              "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
              "PATH=${pkgs.lib.makeBinPath runtimeDeps}:$PATH"
              "SIMULATION_MODE=true"
            ];
            ExposedPorts = {
              "8000/tcp" = {};
            };
            Volumes = {
              "/app/logs" = {};
              "/app/data" = {};
              "/app/config" = {};
            };
          };
        };
        
        # Create a shell script to run the Docker image
        dockerRunScript = pkgs.writeShellScriptBin "run-bluefin-trader" ''
          #!/usr/bin/env bash
          set -euo pipefail
          
          # Load environment variables from .env file if it exists
          if [ -f .env ]; then
            export $(grep -v '^#' .env | xargs)
          fi
          
          # Run the Docker image
          docker run -it --rm \
            -p 8000:8000 \
            -v "$(pwd)/logs:/app/logs" \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/config:/app/config" \
            --env-file .env \
            bluefin-ai-agent-trader-template:latest "$@"
        '';
        
      in {
        packages = {
          # Main application package
          bluefin-trader = app;
          
          # Docker image package
          docker-image = dockerImage;
          
          # Docker run script
          docker-run = dockerRunScript;
          
          # Default package
          default = self.packages.${system}.bluefin-trader;
        };
        
        # Development shell with all tools
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Python development environment
            pythonEnv
            python
            # Additional development tools
            pkgs.poetry
            pkgs.docker
            pkgs.docker-compose
            pkgs.nixfmt
            pkgs.git
          ];
          
          shellHook = ''
            echo "Bluefin AI Agent Trader Template development environment"
            echo "Python: ${python.version}"
            echo "Poetry: $(poetry --version)"
          '';
        };
        
        # Production shell with minimal dependencies
        devShells.production = pkgs.mkShell {
          buildInputs = [
            self.packages.${system}.bluefin-trader
            pkgs.docker
            pkgs.docker-compose
          ];
          
          shellHook = ''
            echo "Bluefin AI Agent Trader Template production environment"
          '';
        };

        # Applications
        apps = {
          bluefin-trader = {
            type = "app";
            program = "${self.packages.${system}.bluefin-trader}/bin/bluefin-trader";
          };
          
          # Helper app to load the docker image
          load-docker-image = {
            type = "app";
            program = toString (pkgs.writeShellScript "load-docker-image" ''
              ${pkgs.docker}/bin/docker load < ${self.packages.${system}.docker-image}
            '');
          };
          
          # Helper app to run the docker image
          run-docker-image = {
            type = "app";
            program = "${self.packages.${system}.docker-run}/bin/run-bluefin-trader";
          };
        };
      }
    );
}
