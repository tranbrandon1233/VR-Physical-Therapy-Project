using System;
using System.IO;
using System.Threading.Tasks;
using Amazon;
using Amazon.Polly;
using Meta.WitAi.Events;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Networking;

namespace AWS
{
    public class TextToSpeechAWSManager : MonoBehaviour
    {
        public static TextToSpeechAWSManager Instance { get; private set; }
        private TextToSpeechAWSService _textToSpeechAwsService;

        private void Awake()
        {
            // Singleton
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
                return;
            }
            
            // var (accessKey, secretKey) = GetAccessToken();
            var accessKey = "AKIAZI2LCV64POXRIPZV";
            var secretKey = "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";
            _textToSpeechAwsService = new TextToSpeechAWSService(accessKey, secretKey, RegionEndpoint.USWest2);
            // ConvertTextToSpeech("Testing Amazon Polly in Unity!");
        }

        public async Task ConvertTextToSpeechAndPlayAudio(string text, AudioSource audioSource, VoiceId voice = null)
        {
            string outputPath = $"{Application.persistentDataPath}/audio.mp3";
            Debug.Log("outputPath: " + outputPath);
            if (voice == null) voice = VoiceId.Stephen;
            await _textToSpeechAwsService.ConvertTextToSpeechAsync(text, outputPath, voice);

            using (var www = UnityWebRequestMultimedia.GetAudioClip("file://" + outputPath, AudioType.MPEG))
            {
                var op = www.SendWebRequest();
                while (!op.isDone)
                {
                    await Task.Yield();
                }
                
                // Check for network error
                if (www.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"Error downloading audio clip: {www.error}");
                }
                else
                {
                    audioSource.clip = DownloadHandlerAudioClip.GetContent(www);
                    audioSource.Play();
                    Debug.Log("Playing audio: " + audioSource.clip.name);
                }
            }
        }

        private (string accessKey, string secretKey) GetAccessToken()
        {
            var userPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            var authPath = $"{userPath}/.aws/auth.json";
            if (File.Exists(authPath))
            {
                var json = File.ReadAllText(authPath).Trim();
                var auth = JsonConvert.DeserializeObject<AWSAuth>(json);
                return (auth.access_key, auth.secret_key);
            }
            
            Debug.LogError("API Key is null and auth.json does not exist. Please check https://github.com/srcnalt/OpenAI-Unity#saving-your-credentials except use the filepath of .aws/auth.json instead.");
            return (null, null);
        }
    }
}

