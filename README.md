<div>
  <h1>Telegram Python Toolkit: Image Text Extraction &amp; Voice Conversion</h1>
  <p>This Python toolkit for Telegram offers a seamless integration of powerful functionalities, including text
    extraction from images, voice-to-text conversion, and text-to-voice generation. Whether you aim to enhance
    accessibility features or streamline communication processes within your Telegram bot or application, this toolkit
    provides essential tools to augment your user experience.</p>
  <h2>Features:</h2>
  <h3>1. Text Extraction from Images</h3>
  <p>Easily extract text content from images using <a
      href="https://github.com/UB-Mannheim/tesseract/wiki"><strong>Pytesseract</strong></a>.</p>
  <h3>2. Voice-to-Text Conversion</h3>
  <p>Convert voice messages using <a href="https://github.com/openai/whisper"><strong>Whisper</strong></a> or <a
      href="https://github.com/snakers4/silero-models"><strong>Silero STT</strong></a> (<em>work in progress</em>). This
    feature supports multiple languages, including English, German, Italian, Russian, Dutch, Japanese, French, Turkish,
    Chinese, and others.</p>
  <h3>3. Text-to-Voice Generation</h3>
  <p>Efficiently transform textual messages into voice recordings using <a
      href="https://github.com/snakers4/silero-models"><strong>Silero TTS</strong></a>.</p>
  <h2>Getting Started:</h2>
  <ol>
    <li>
      <p><strong>Installation:</strong></p>
      <ul>
        <li>Clone this repository to your local machine or download the ZIP
          file.<br /><code>git clone https://github.com/MoguchiyDuh/TG_BOT</code></li>
        <li>Install pytesseract <a href="https://github.com/UB-Mannheim/tesseract/wiki">here</a>.</li>
        <li>Install the required dependencies listed in <em><code>requirements.txt</code></em>. (<em>Note: If you want
            CUDA to work, install compatible versions of CUDA, cuDNN, and PyTorch. <a href="https://pytorch.org/">See
              more</a></em>)<br /><code>pip install -r requirements.txt</code></li>
      </ul>
    </li>
    <li>
      <p><strong>Configuration:</strong></p>
      <ul>
        <li>Obtain a Telegram Bot API Key from <a href="https://telegram.me/BotFather">here</a> and paste it into
          <strong>config.json</strong>.
        </li>
        <li>All models will download <strong>automatically</strong>. However, you can install other <a
            href="https://models.silero.ai/models/tts/">Silero model languages</a> (place files in
          <strong>text2speech/model/</strong>) and larger <a href="https://github.com/openai/whisper">Whisper models</a>
          (available in <strong>tiny</strong> by default, <strong>base</strong>, <strong>small</strong>,
          <strong>medium</strong>, and <strong>large</strong>&mdash;not recommended unless you have a 4090 GPU). Specify
          the version in config.json.
        </li>
      </ul>
    </li>
    <li>
      <p><strong>Usage:</strong></p>
      <ul>
        <li>Start the bot and enter <em>/start</em> in the Telegram chat.<br /><code>python main.py</code></li>
      </ul>
    </li>
  </ol>
</div>