{
  pkgs ? import <nixpkgs> { }
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python3.withPackages (pp: with pp; [
      legacy-cgi # cgi
      aiohttp
      aiohttp-retry
      # nur.repos.milahu.python3.pkgs.selenium-driverless # unfree license
      nur.repos.milahu.python3.pkgs.selenium-driverless-next # unfree license
      nur.repos.milahu.python3.pkgs.cdp-socket
      websockets
      orjson
      nest-asyncio # TODO remove?
      torf
      pdftotext
      beautifulsoup4
    ]))
    # fix: ModuleNotFoundError: No module named 'cdp_socket'
    nur.repos.milahu.python3.pkgs.cdp-socket
  ];
}
