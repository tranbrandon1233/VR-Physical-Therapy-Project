using System;
using System.Collections;
using System.Threading.Tasks;
using Amazon.Polly;
using OpenAI;
using UnityEngine;

namespace AWS
{
    public class TextToSpeech : MonoBehaviour
    {
        public static Action OnStartTalking;
        public static Action OnFinishedTalking;
        private TextToSpeechAWSManager _textToSpeechAwsManager;
        private AudioSource _audioSource;
        private VoiceId _voiceId = VoiceId.Stephen;
        
        private void Awake()
        {
            _audioSource = GetComponent<AudioSource>();
        }

        private void Start()
        {
            _textToSpeechAwsManager = TextToSpeechAWSManager.Instance;
            _voiceId = VoiceId.Stephen;
        }

        private void OnEnable()
        {
            WhisperVoice.OnEndRecording += ConvertTextToSpeechAndPlayAudioAsync;
        }

        private void OnDisable()
        {
            WhisperVoice.OnEndRecording -= ConvertTextToSpeechAndPlayAudioAsync;
        }
        
        private async void ConvertTextToSpeechAndPlayAudioAsync(string text)
        {
            _audioSource.Stop();
           
            print("Converting text to speech: " + text);
            OnStartTalking?.Invoke();
            await _textToSpeechAwsManager.ConvertTextToSpeechAndPlayAudio(text, _audioSource, _voiceId);
            await WaitForAudioToEnd();
            OnFinishedTalking?.Invoke();
        }
    
        private Task WaitForAudioToEnd()
        {
            var tcs = new TaskCompletionSource<bool>();
            StartCoroutine(WaitForAudioToEndCoroutine(tcs));
            return tcs.Task;
        }
        
        private IEnumerator WaitForAudioToEndCoroutine(TaskCompletionSource<bool> tcs)
        {
            yield return new WaitWhile(() => _audioSource.isPlaying);
            tcs.SetResult(true); // Marks the Task as completed.
        }
        
        public void PlayAudio()
        {
            _audioSource.Play();
        }
    }
}

