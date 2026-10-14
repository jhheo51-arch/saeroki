param(
    [string]$CharacterPath = (Join-Path $PSScriptRoot '..\assets\saeroki-character-v02.png'),
    [string]$OutputPath = (Join-Path $PSScriptRoot '..\assets\saeroki-motion.svg')
)

$resolvedCharacter = (Resolve-Path -LiteralPath $CharacterPath).Path
$pngBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($resolvedCharacter))
$svg = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" role="img" aria-labelledby="title desc">
  <title id="title">산책하는 새록이</title>
  <desc id="desc">새록이 캐릭터가 초록 들판을 천천히 왔다 갔다 합니다.</desc>
  <style>
    #runner { animation: stroll 10s ease-in-out infinite; }
    #bob { animation: bob 1.2s ease-in-out infinite; transform-origin: center; }
    @keyframes stroll {
      0%, 100% { transform: translateX(20px); }
      50% { transform: translateX(920px); }
    }
    @keyframes bob {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-8px); }
    }
    @media (prefers-reduced-motion: reduce) {
      #runner, #bob { animation: none; }
      #runner { transform: translateX(470px); }
    }
  </style>
  <rect width="1200" height="300" rx="28" fill="#FAF9F6"/>
  <circle cx="108" cy="70" r="34" fill="#ECF39E"/>
  <circle cx="1135" cy="76" r="48" fill="#ECF39E"/>
  <path d="M0 226c148-39 267 23 410-1 183-31 304 26 469-3 138-25 218-2 321 12v66H0z" fill="#90A955"/>
  <path d="M0 254c170-17 283 24 467 3 195-22 317 32 493 1 93-17 157-9 240 3v39H0z" fill="#40916C"/>
  <g id="runner">
    <g id="bob">
      <image href="data:image/png;base64,$pngBase64" x="0" y="18" width="250" height="250"/>
    </g>
  </g>
</svg>
"@

[IO.File]::WriteAllText($OutputPath, $svg, [Text.UTF8Encoding]::new($false))
