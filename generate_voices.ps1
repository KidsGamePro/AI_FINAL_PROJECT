Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Zira Desktop')
$synth.Rate = -2
$synth.Volume = 90

if (-Not (Test-Path "assets/sounds")) {
    New-Item -ItemType Directory -Path "assets/sounds" | Out-Null
}

$synth.SetOutputToWaveFile('assets/sounds/intro.wav')
$synth.Speak('Welcome to AI Kiddy Learner! Tap Play with Words to start or Speak with AI to talk. Have fun and learn!')

$synth.SetOutputToWaveFile('assets/sounds/game_instruction.wav')
$synth.Speak('In this game, choose the correct word that matches the picture. Listen carefully and have fun!')

$synth.SetOutputToWaveFile('assets/sounds/correct.wav')
$synth.Speak('Wow! That is correct, so clever!')

$synth.SetOutputToWaveFile('assets/sounds/try_again.wav')
$synth.Speak('Oops, try again. You are getting closer!')

$synth.SetOutputToWaveFile('assets/sounds/clap.wav')
$synth.Speak('Clap clap clap, great job!')

$synth.SetOutputToWaveFile('assets/sounds/start.wav')
$synth.Speak('Let us begin the game!')

$synth.Dispose()
