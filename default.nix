{ lib, python3Packages }:

with python3Packages;

buildPythonPackage rec {
  pname = "edb";
  version = "0.1.0";
  src = lib.cleanSource ./.;
}
