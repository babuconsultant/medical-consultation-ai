import speech_recognition as sr
import streamlit as st
import tempfile
import os
import numpy as np
import soundfile as sf
from typing import Optional, Tuple
import torch
import logging
import pyaudio
import wave
import threading
import time
import requests
import json
from pydub import AudioSegment
from pydub.utils import which

# Try to import whisper for better transcription
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    st.warning("⚠️ Whisper not installed. Using basic speech recognition. Install with: pip install openai-whisper")

class EnhancedAudioProcessor:
    """
    Enhanced Audio Processing class with multiple transcription engines and better performance.
    """

    def __init__(self, model_size: str = "base", device: Optional[str] = None, use_whisper: bool = True):
        """
        Initialize the Enhanced AudioProcessor.
        
        Args:
            model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            device (str): Device to run processing on
            use_whisper (bool): Whether to use Whisper model for transcription
        """
        self.model_size = model_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.use_whisper = use_whisper and WHISPER_AVAILABLE
        
        # Initialize basic speech recognizer as fallback
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        try:
            self.microphone = sr.Microphone()
        except:
            self.microphone = None
            
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.mp4', '.avi', '.mov', '.webm']
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Audio recording parameters
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        
        # Initialize Whisper model if available
        self.whisper_model = None
        if self.use_whisper:
            self._initialize_whisper()
        
        # Initialize speech recognition
        self._initialize_recognizer()

    def _initialize_whisper(self) -> None:
        """Initialize Whisper model for better transcription."""
        try:
            if WHISPER_AVAILABLE:
                with st.spinner(f"Loading Whisper {self.model_size} model..."):
                    self.whisper_model = whisper.load_model(self.model_size, device=self.device)
                self.logger.info(f"Whisper {self.model_size} model loaded successfully on {self.device}")
            else:
                self.use_whisper = False
                st.warning("Whisper not available, falling back to basic speech recognition")
        except Exception as e:
            self.logger.error(f"Failed to initialize Whisper: {e}")
            self.use_whisper = False
            st.warning(f"Whisper initialization failed: {e}. Using basic speech recognition.")

    def _initialize_recognizer(self) -> None:
        """Initialize the speech recognition system."""
        try:
            if self.microphone:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Speech recognition system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")

    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> dict:
        """
        Transcribe audio file to text using the best available method.
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str): Language code (default: "en" for English)
            
        Returns:
            dict: Transcription result with text, confidence, and metadata
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # Use Whisper if available (much better accuracy and speed)
            if self.use_whisper and self.whisper_model:
                return self._transcribe_with_whisper(audio_file_path, language)
            else:
                return self._transcribe_with_speech_recognition(audio_file_path, language)

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {
                'text': f"Error during transcription: {str(e)}",
                'language': language,
                'segments': [],
                'confidence': 0.0,
                'duration': 0.0,
                'model_used': 'error',
                'error': str(e)
            }

    def _transcribe_with_whisper(self, audio_file_path: str, language: str = "en") -> dict:
        """Transcribe using Whisper model (preferred method)."""
        try:
            with st.spinner("🚀 Transcribing with Whisper AI..."):
                # Whisper expects specific language codes
                whisper_lang = "en" if language == "en" else language
                
                # Transcribe with Whisper
                result = self.whisper_model.transcribe(
                    audio_file_path, 
                    language=whisper_lang,
                    verbose=False
                )
                
                # Extract segments information
                segments = []
                if 'segments' in result:
                    segments = [
                        {
                            'start': seg.get('start', 0),
                            'end': seg.get('end', 0),
                            'text': seg.get('text', '').strip()
                        }
                        for seg in result['segments']
                    ]

                transcription_data = {
                    'text': result['text'].strip(),
                    'language': result.get('language', language),
                    'segments': segments,
                    'confidence': 0.95,  # Whisper generally has high confidence
                    'duration': self._get_audio_duration(audio_file_path),
                    'model_used': f'whisper-{self.model_size}'
                }

                self.logger.info(f"Whisper transcription completed. Text length: {len(transcription_data['text'])} characters")
                return transcription_data

        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            # Fallback to speech recognition
            return self._transcribe_with_speech_recognition(audio_file_path, language)

    def _transcribe_with_speech_recognition(self, audio_file_path: str, language: str = "en") -> dict:
        """Fallback transcription using speech_recognition library."""
        try:
            with st.spinner("🎯 Transcribing with Speech Recognition..."):
                
                # Convert to WAV if needed for better compatibility
                wav_path = audio_file_path
                if not audio_file_path.lower().endswith('.wav'):
                    wav_path = audio_file_path.replace(os.path.splitext(audio_file_path)[1], '.wav')
                    self._convert_to_wav(audio_file_path, wav_path)
                
                with sr.AudioFile(wav_path) as source:
                    # Adjust for noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = self.recognizer.record(source)
                
                # Try multiple recognition engines
                text = ""
                confidence = 0.0
                
                # Try Google Speech Recognition first (most accurate)
                try:
                    text = self.recognizer.recognize_google(audio_data, language=language)
                    confidence = 0.85
                    model_used = "google_sr"
                except sr.UnknownValueError:
                    text = "Could not understand audio clearly"
                    confidence = 0.0
                except sr.RequestError:
                    # Try Sphinx offline recognition
                    try:
                        text = self.recognizer.recognize_sphinx(audio_data)
                        confidence = 0.70
                        model_used = "sphinx_offline"
                    except:
                        text = "Speech recognition service unavailable"
                        confidence = 0.0
                        model_used = "none"

                # Clean up temporary WAV file if created
                if wav_path != audio_file_path and os.path.exists(wav_path):
                    os.unlink(wav_path)

                transcription_data = {
                    'text': text.strip() if text else '',
                    'language': language,
                    'segments': [],
                    'confidence': confidence,
                    'duration': self._get_audio_duration(audio_file_path),
                    'model_used': model_used
                }

                self.logger.info(f"Speech recognition completed. Text length: {len(transcription_data['text'])} characters")
                return transcription_data

        except Exception as e:
            self.logger.error(f"Speech recognition failed: {e}")
            return {
                'text': f"Speech recognition error: {str(e)}",
                'language': language,
                'segments': [],
                'confidence': 0.0,
                'duration': 0.0,
                'model_used': 'speech_recognition_error',
                'error': str(e)
            }

    def transcribe_uploaded_file(self, uploaded_file) -> dict:
        """
        Transcribe uploaded audio file from Streamlit file uploader.
        """
        try:
            # Validate file format
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                # For better compatibility, convert to WAV if not already
                if file_extension != '.wav':
                    wav_path = tmp_file_path.replace(file_extension, '.wav')
                    self._convert_to_wav_enhanced(tmp_file_path, wav_path)
                    transcription_path = wav_path
                else:
                    transcription_path = tmp_file_path

                # Transcribe the file
                result = self.transcribe_audio(transcription_path)
                return result

            finally:
                # Clean up temporary files
                for path in [tmp_file_path, tmp_file_path.replace(file_extension, '.wav')]:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                        except:
                            pass

        except Exception as e:
            self.logger.error(f"Failed to process uploaded file: {e}")
            return {
                'text': f"Error processing uploaded file: {str(e)}",
                'language': 'en',
                'segments': [],
                'confidence': 0.0,
                'duration': 0.0,
                'model_used': 'upload_error',
                'error': str(e)
            }

    def record_and_transcribe(self, duration: int = 30, sample_rate: int = 16000) -> dict:
        """
        Record audio from microphone and transcribe it.
        """
        if not self.microphone:
            return {
                'text': "Microphone not available",
                'language': 'en',
                'segments': [],
                'confidence': 0.0,
                'duration': 0.0,
                'model_used': 'no_microphone',
                'error': 'Microphone not available'
            }

        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Recording parameters
            self.sample_rate = sample_rate
            
            # Create temporary file for recording
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file_path = tmp_file.name

            # Record audio with progress
            with st.spinner(f"🎤 Recording for {duration} seconds..."):
                frames = []
                
                stream = audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size
                )
                
                # Show progress
                progress_bar = st.progress(0)
                for i in range(0, int(self.sample_rate / self.chunk_size * duration)):
                    data = stream.read(self.chunk_size)
                    frames.append(data)
                    progress = (i + 1) / int(self.sample_rate / self.chunk_size * duration)
                    progress_bar.progress(progress)
                
                stream.stop_stream()
                stream.close()
                audio.terminate()
                progress_bar.empty()

            # Save recorded audio to file with better quality
            with wave.open(tmp_file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))

            try:
                # Transcribe the recorded audio
                result = self.transcribe_audio(tmp_file_path)
                return result
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

        except Exception as e:
            self.logger.error(f"Recording failed: {e}")
            return {
                'text': f"Recording error: {str(e)}",
                'language': 'en',
                'segments': [],
                'confidence': 0.0,
                'duration': 0.0,
                'model_used': 'recording_error',
                'error': str(e)
            }

    def _convert_to_wav_enhanced(self, input_path: str, output_path: str) -> None:
        """Enhanced audio conversion using pydub for better format support."""
        try:
            # Try pydub first (supports more formats)
            if which("ffmpeg") or which("avconv"):
                audio = AudioSegment.from_file(input_path)
                # Ensure consistent format for transcription
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(output_path, format="wav")
            else:
                # Fallback to soundfile
                self._convert_to_wav(input_path, output_path)
        except Exception as e:
            # Final fallback
            self._convert_to_wav(input_path, output_path)

    def _convert_to_wav(self, input_path: str, output_path: str) -> None:
        """Convert audio file to WAV format using soundfile."""
        try:
            data, sample_rate = sf.read(input_path)
            # Ensure mono and consistent sample rate
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            sf.write(output_path, data, 16000)
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {e}")
            raise

    def _get_audio_duration(self, audio_file_path: str) -> float:
        """Get duration of audio file in seconds."""
        try:
            data, sample_rate = sf.read(audio_file_path)
            duration = len(data) / sample_rate
            return round(duration, 2)
        except Exception:
            return 0.0

    def get_model_info(self) -> dict:
        """Get information about the current processing system."""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'supported_formats': self.supported_formats,
            'whisper_available': self.use_whisper,
            'system': 'whisper' if self.use_whisper else 'speech_recognition',
            'microphone_available': self._check_microphone_availability()
        }

    def _check_microphone_availability(self) -> bool:
        """Check if microphone is available."""
        try:
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            audio.terminate()
            return device_count > 0
        except:
            return False

    def change_model(self, new_model_size: str) -> bool:
        """
        Change the Whisper model size.
        
        Args:
            new_model_size (str): New model size ('tiny', 'base', 'small', 'medium', 'large')
            
        Returns:
            bool: Success status
        """
        try:
            if self.use_whisper and new_model_size != self.model_size:
                self.model_size = new_model_size
                self._initialize_whisper()
                self.logger.info(f"Model changed to: {new_model_size}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to change model: {e}")
            return False

# Utility functions
def create_audio_processor(model_size: str = "base") -> EnhancedAudioProcessor:
    """
    Factory function to create EnhancedAudioProcessor instance with caching.
    """
    cache_key = f'enhanced_audio_processor_{model_size}'
    if cache_key not in st.session_state:
        st.session_state[cache_key] = EnhancedAudioProcessor(model_size=model_size)
    return st.session_state[cache_key]

def get_supported_audio_formats() -> list:
    """Get list of supported audio formats."""
    return ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.mp4', '.avi', '.mov', '.webm']

# Enhanced model recommendations with Whisper
MODEL_RECOMMENDATIONS = {
    'tiny': {
        'description': 'Fastest processing, good for real-time (39 MB)',
        'vram': '~1 GB',
        'use_case': 'Quick transcription, real-time processing'
    },
    'base': {
        'description': 'Balanced speed and accuracy (74 MB)',
        'vram': '~1 GB', 
        'use_case': 'Recommended for most applications'
    },
    'small': {
        'description': 'Better accuracy, moderate speed (244 MB)',
        'vram': '~2 GB',
        'use_case': 'Higher accuracy requirements'
    },
    'medium': {
        'description': 'High accuracy, slower processing (769 MB)',
        'vram': '~5 GB',
        'use_case': 'Professional medical transcription'
    },
    'large': {
        'description': 'Best accuracy, slowest processing (1550 MB)',
        'vram': '~10 GB',
        'use_case': 'Maximum accuracy for critical applications'
    }
}