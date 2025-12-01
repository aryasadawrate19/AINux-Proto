"""
Voice input utilities for AiNux.

Provides a simple API to capture audio from the microphone and transcribe
to text using SpeechRecognition (Google Web Speech API). Designed to work
on Windows with graceful errors when dependencies or microphone are missing.

Optional: If you install Vosk and a model, you can switch to offline mode.

Primary API:
	listen_for_command(timeout: float | None = 5, phrase_time_limit: float | None = 8,
					   language: str = "en-US") -> str | None

Returns the recognized text (lowercased) or None if nothing understood.
"""

from __future__ import annotations

from typing import Optional


class VoiceInputError(RuntimeError):
	"""Raised when voice input cannot be initialized or used."""


def _try_import_sr():
	try:
		import speech_recognition as sr  # type: ignore
		return sr
	except Exception as e:
		return None


def _has_microphone(sr_module) -> bool:
	try:
		# Try to access microphones list
		return len(sr_module.Microphone.list_microphone_names() or []) > 0
	except Exception:
		return True  # If listing fails, assume there may be a default mic


def listen_for_command(
	timeout: Optional[float] = 5,
	phrase_time_limit: Optional[float] = 8,
	language: str = "en-US",
	device_index: Optional[int] = None,
) -> Optional[str]:
	"""
	Capture audio from the default microphone and transcribe to text.

	Args:
		timeout: Max seconds to wait for phrase to start (None to wait forever)
		phrase_time_limit: Max seconds for a single phrase (None for unlimited)
		language: BCP-47 language code for recognition (default en-US)
		device_index: Optional microphone device index

	Returns:
		Recognized text (lowercased) or None if not understood / timed out.

	Raises:
		VoiceInputError: If SpeechRecognition or microphone is unavailable.
	"""
	sr = _try_import_sr()
	if sr is None:
		raise VoiceInputError(
			"SpeechRecognition is not installed. Install with: pip install SpeechRecognition"
		)

	# Try importing PyAudio lazily; not strictly required to import here,
	# but we can hint if microphone open fails later.
	try:
		# Importing pyaudio ensures backend availability when needed.
		import pyaudio  # noqa: F401  # type: ignore
	except Exception:
		# We'll still attempt to open microphone; if it fails, raise a helpful error.
		pass

	if not _has_microphone(sr):
		raise VoiceInputError("No microphone detected. Please connect a microphone and try again.")

	recognizer = sr.Recognizer()

	# Calibrate and listen from mic
	try:
		with sr.Microphone(device_index=device_index) as source:
			# Reduce noise impact
			try:
				recognizer.adjust_for_ambient_noise(source, duration=0.5)
			except Exception:
				# Non-fatal; continue
				pass

			audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
	except sr.WaitTimeoutError:
		return None
	except Exception as e:
		# Provide actionable guidance for Windows + PyAudio
		raise VoiceInputError(
			"Failed to access microphone. On Windows, install PyAudio. "
			"If 'pip install pyaudio' fails, try: 'pip install pipwin' then 'pipwin install pyaudio'.\n"
			f"Underlying error: {e}"
		)

	# Recognize using Google's free web API (requires internet)
	try:
		text = recognizer.recognize_google(audio, language=language)
		return text.strip().lower() if text else None
	except sr.UnknownValueError:
		return None
	except sr.RequestError as e:
		# Network or quota error. Gracefully return None; caller can handle.
		return None
	except Exception:
		return None


__all__ = ["listen_for_command", "VoiceInputError"]

